import os

import pandas as pd
import streamlit as st
from streamlit import error, session_state, text_input  # type: ignore

from crea_scraper.data import get_course_documents_for_search, load_course_data, prepare_for_search
from crea_scraper.search import get_relevant_courses

demo_password = os.environ["CREA_DEMO_PASSWORD"]


@st.cache_data
def load_data():
    course_data = load_course_data("output/course_data.csv")
    data_for_search = prepare_for_search(course_data)
    course_documents = get_course_documents_for_search(data_for_search)
    return course_data, course_documents


def check_password():
    """Returns `True` if the user had the correct password."""

    def password_entered():
        """Checks whether a password entered by the user is correct."""
        if session_state["password"] == demo_password:
            session_state["password_correct"] = True
            del session_state["password"]  # don't store password
        else:
            session_state["password_correct"] = False

    if "password_correct" not in session_state:
        # First run, show input for password.
        text_input("Password", type="password", on_change=password_entered, key="password")
        return False
    elif not session_state["password_correct"]:
        # Password not correct, show input + error.
        text_input("Password", type="password", on_change=password_entered, key="password")
        error("😕 Password incorrect")
        return False
    else:
        # Password correct.
        return True


def make_clickable(url):
    return f'<a href="{url}" target="_blank">link</a>'


def app():
    st.title("Crea course recommender")
    st.write("Enter your interests below")
    interests = st.text_area("Interests", "I like to draw and paint")

    n_recommendations = st.slider("Number of recommendations", min_value=1, max_value=10, value=3)

    # center relative to the width of the page
    # _, center, _ = st.columns([1, 6, 1]) - this is too far to the left
    _, _, center, _, _ = st.columns([1, 1, 1, 1, 1])
    with center:
        generate_button = st.button("Recommend")

    if generate_button:
        course_data, course_documents = load_data()
        recommendations = get_relevant_courses(
            query=interests,
            courses=course_documents,
            k=n_recommendations,
            method="embedding",
            vector_db_path="output/vector_db",
            verbose=True,
        )
        course_names = [course.metadata["naam"] for course in recommendations]
        course_links = [make_clickable(course.metadata["url"]) for course in recommendations]
        # course_names = ["Course 1", "Course 2", "Course 3"]
        # course_links = [make_clickable("www.nos.nl") for course in course_names]
        # table with "naam" as index and clickable urls with shortcut "link"
        df = pd.DataFrame({"Course name": course_names, "Webpage": course_links})

        # Display the DataFrame as an HTML table with clickable links
        with st.container():
            st.write(
                df.to_html(
                    escape=False,
                    index=False,
                    col_space=350,
                    justify="left",
                ),
                unsafe_allow_html=True,
            )


if __name__ == "__main__":
    if check_password():
        app()
