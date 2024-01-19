import logging

from crea_scraper import data, scraper

logging.basicConfig(format="%(levelname)s:%(funcName)s:%(lineno)d: %(message)s", level=logging.INFO)


OUTPUT_PATH = "output/course_data.csv"


if __name__ == "__main__":
    course_data = scraper.run()
    data.write_course_data(course_data, OUTPUT_PATH)
