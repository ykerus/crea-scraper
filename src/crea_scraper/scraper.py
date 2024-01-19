import asyncio
import logging
import os
import time
from typing import Dict, List, Tuple

import aiohttp
import pandas as pd
from bs4 import BeautifulSoup

from crea_scraper.course import Course, CourseGeneralInfo
from crea_scraper.data import write_course_data

logger = logging.getLogger(__name__)


async def _request_async(session, url: str):
    async with session.get(url) as resp:
        if resp.status == 200:
            return BeautifulSoup(await resp.text(), "html.parser")
        return None


async def _multi_request_async(urls: List[str]) -> List:
    # see https://www.twilio.com/blog/asynchronous-http-requests-in-python-with-aiohttp
    async with aiohttp.ClientSession() as session:
        tasks = []
        for url in urls:
            tasks.append(asyncio.ensure_future(_request_async(session, url)))
        contents = await asyncio.gather(*tasks)
        return contents


def _get_course_overview_subpage_urls(
    page_from: int,
    page_to: int,
    base_url: str = "https://www.crea.nl/cursussen/cursussen-overzicht",
) -> List[str]:
    subpage_urls = []
    for page_nr in range(page_from, page_to):
        subpage_urls.append(os.path.join(base_url, "page", str(page_nr)))
    return subpage_urls


def get_course_overview_subpages_html_content(
    max_subpages: int = 100, n_sim_requests: int = 25
) -> List[str]:
    """
    -> [subpage_1, ..., subpage_n]
    """

    n_sim_requests = min(max_subpages, n_sim_requests)

    # The course overview page consists of several subpages, so we have
    # to send multiple requests until we've reached all subpages
    subpage_from, subpage_to = 1, n_sim_requests + 1
    subpage_urls = _get_course_overview_subpage_urls(subpage_from, subpage_to)
    subpages_html = []

    while subpage_to <= max_subpages + 1:
        logger.info(f"Requesting subpages {subpage_from} to {subpage_to} ...")

        subpages_html += asyncio.run(_multi_request_async(subpage_urls))
        if subpages_html[-1] is None:
            break

        subpage_from += n_sim_requests
        subpage_to += n_sim_requests

    subpages_html = [sp for sp in subpages_html if sp is not None]
    return subpages_html


def _get_courses_html_content_from_overview_subpage(subpage_html) -> List:
    """
    subpage -> [course_1, ..., course_n]
    """
    selection = subpage_html.find("ul", {"class": "stm-courses"})
    courses_html = selection.findChildren("li", recursive=False)
    return courses_html


def get_courses_html_content_from_overview_subpages(subpages_html: List) -> List:
    """
    [subpage_1, ..., subpage_n] -> [course_1, ..., course_m]
    """
    courses_html = []
    for subpage in subpages_html:
        courses_html += _get_courses_html_content_from_overview_subpage(subpage)
    return courses_html


def _get_course_url(course_html, from_overview_page: bool = False) -> str:
    if from_overview_page:
        return course_html.find("a", href=True)["href"]
    # else from course page
    return course_html.find("link", {"rel": "alternate"}, href=True)["href"]


def get_course_urls(overview_courses_html: List) -> List[str]:
    course_urls = []
    for overview_course_html in overview_courses_html:
        course_urls.append(_get_course_url(overview_course_html, from_overview_page=True))
    return course_urls


def get_courses_html_content(course_urls):
    return asyncio.run(_multi_request_async(course_urls))


def _get_course_category(course_html) -> str:
    """
    A course can have multiple categories. These get returned
    as one category, separated by " / ".

    """

    for e in course_html.find_all("div", class_="meta_values"):
        element_content = e.text.lower()
        if "categorie" in element_content or "category" in element_content:
            category_html = e
            break
    categories = [e.text[:-1] for e in category_html.find_all("a")]
    return " / ".join(categories)


def _get_course_name(course_html) -> str:
    return course_html.find(class_="product_title entry-title").text


def _get_course_description(course_html) -> str:
    parts = [e.text for e in course_html.find(class_="wpb_wrapper").findChildren("p")]
    description = "\n\n".join(parts)
    return description


def _get_raw_table_data(table_html, incl_empty_values=True):
    table_data = []
    rows = table_html.find_all("tr")
    for row in rows:
        cols = row.find_all("td")
        cols = [e.text.strip() for e in cols]
        table_data.append([e for e in cols if e or incl_empty_values])
    return table_data


def _get_dict_from_raw_table_data(table_data):
    table_dict = {}
    for i, row in enumerate(table_data):
        if i % 2 != 0:
            continue
        for j, col in enumerate(row):
            if not col:
                continue
            table_dict[col] = table_data[i + 1][j]
    return table_dict


def _separate_time_from_day(table_dict):
    time_data_split = table_dict["tijd"].split()

    error_msg = f"Error while parsing: {table_dict['tijd']}"
    assert len(time_data_split) < 5, error_msg

    day = time_data_split[0]
    time = " ".join(time_data_split[1:])

    table_dict["dag"] = day
    table_dict["tijd"] = time
    table_dict["dag_tijd"] = f"{day} {time}"
    return table_dict


def _rename_table_columns(table_dict):
    try:
        table_dict["cursus_type"] = table_dict["cursus type"]
        del table_dict["cursus type"]
    except KeyError:
        print(f"Key 'cursus type' not found in {table_dict.keys()}")
        table_dict["cursus_type"] = ""

    return table_dict


def _extract_data_from_table(table_html):
    table_data = _get_raw_table_data(table_html)
    table_dict = _get_dict_from_raw_table_data(table_data)
    table_dict = _separate_time_from_day(table_dict)
    return table_dict


def _get_course_status(register_link_html):
    if "vol" in register_link_html.text:
        return "vol"
    if "gestart" in register_link_html.text:
        return "gestart"
    return "open"


def _get_course_table_data(course_html) -> List[Dict]:
    div = course_html.find("div", class_="product_main_data")
    register_links_html = div.findChildren("a", class_="register_link")
    tables_html = div.findChildren("table", recursive=False)
    if not len(tables_html):
        print(f"No tables found for {_get_course_url(course_html)}")
    table_data = []
    for table_html, register_link_html in zip(tables_html, register_links_html):
        table_dict = _extract_data_from_table(table_html)
        table_dict = _rename_table_columns(table_dict)
        course_status = _get_course_status(register_link_html)
        table_dict["status"] = course_status
        table_data.append(table_dict)
    return table_data


def _get_course_data(course_html) -> Tuple[CourseGeneralInfo, List[Course]]:
    url = _get_course_url(course_html)
    print(f"Parsing {url} ...")
    general_info = CourseGeneralInfo(
        url=url,
        naam=_get_course_name(course_html),
        categorie=_get_course_category(course_html),
        beschrijving=_get_course_description(course_html),
    )
    course_data = []
    table_data = _get_course_table_data(course_html)
    for table in table_data:
        course_data.append(Course(naam=general_info.naam, **table))

    print("Success!")
    return general_info, course_data


def get_courses_data(courses_html) -> pd.DataFrame:
    courses_data: List[List[Course]] = []
    general_info: List[CourseGeneralInfo] = []
    for course_html in courses_html:
        info, data = _get_course_data(course_html)
        courses_data.append(data)
        general_info.append(info)

    general_info_df = pd.DataFrame(general_info)
    courses_data_df = pd.concat([pd.DataFrame(data) for data in courses_data])

    df = courses_data_df.merge(general_info_df, how="inner", on="naam")
    assert len(df) >= len(courses_data_df), "Each course should have general info"
    return df


def run() -> pd.DataFrame:
    logger.info("Starting scraper ...")
    overview_subpages_html = get_course_overview_subpages_html_content()
    overview_courses_html = get_courses_html_content_from_overview_subpages(overview_subpages_html)

    course_urls = get_course_urls(overview_courses_html)
    courses_html = get_courses_html_content(course_urls)

    courses_data = get_courses_data(courses_html)
    return courses_data


if __name__ == "__main__":
    start_time = time.time()
    write_course_data(run(), "output/course_data.csv")
    print("--- %s seconds ---" % (time.time() - start_time))
