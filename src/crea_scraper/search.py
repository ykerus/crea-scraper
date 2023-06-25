import os
from typing import List

from langchain.llms import AzureOpenAI
from langchain.schema import Document
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import linear_kernel

from crea_scraper.prompts import search_prompt_template
from crea_scraper.vector_db import load_vector_db


def embedding_search(query: str, k: int, vector_db_path: str) -> List[Document]:
    if not os.path.exists(vector_db_path):
        raise FileNotFoundError(
            "Vector database not found. Run `python -m crea_scraper.vector_db` to create it."
        )
    db = load_vector_db(vector_db_path)
    return db.similarity_search(query, k=k)


def tfidf_search(query: str, courses: List[Document], k: int) -> List[Document]:
    vectorizer = TfidfVectorizer()
    course_descriptions = [course.page_content for course in courses]
    tfidf_documents = vectorizer.fit_transform(course_descriptions)
    tfidf_query = vectorizer.transform([query])
    similarities = linear_kernel(tfidf_query, tfidf_documents).flatten()
    top_k_indices = similarities.argsort()[-k:][::-1]
    top_k_documents = [courses[index] for index in top_k_indices]
    return top_k_documents


def prepare_query_for_search(query: str) -> str:
    llm = AzureOpenAI(
        model_name="gpt-4",
        temperature=0.7,
        max_tokens=250,
        top_p=1.0,
        verbose=True,
        engine="gpt-4-us",
    )
    return llm(search_prompt_template().format(query=query))


def get_relevant_courses(
    query: str,
    courses: List[Document],
    method: str = "embedding",
    k: int = 10,
    vector_db_path: str = "output/vector_db",
    verbose: bool = True,
) -> List[Document]:

    assert method in ["embedding", "tfidf"]

    search_query = prepare_query_for_search(query)
    if verbose:
        print(f"Search query:\n{search_query}")

    if method == "tfidf":
        return tfidf_search(search_query, courses, k)
    elif method == "embedding":
        return embedding_search(
            search_query, k, vector_db_path
        )  # courses already stored in vector db
