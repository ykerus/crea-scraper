from typing import List

import pandas as pd
from langchain.document_loaders import DataFrameLoader
from langchain.schema import Document


def prepare_for_search(course_data: pd.DataFrame) -> pd.DataFrame:
    return (
        course_data.drop(columns=["dag", "tijd", "dag_tijd", "startdatum", "status"])
        .drop_duplicates(subset=["naam"])
        .reset_index(drop=True)
        .assign(
            search_info=lambda x: "Course title: "
            + x["naam"]
            + "\nCourse description: "
            + x["beschrijving"]
        )
    )


def get_course_documents_for_search(data_for_search: pd.DataFrame) -> List[Document]:
    loader = DataFrameLoader(data_for_search, "search_info")
    documents = loader.load()
    return documents


def write_course_data(df: pd.DataFrame, output_path: str) -> None:
    df.drop_duplicates().to_csv(output_path, index=False, sep=",")


def load_course_data(path: str) -> pd.DataFrame:
    return pd.read_csv(path)
