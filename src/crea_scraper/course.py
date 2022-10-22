from dataclasses import dataclass


@dataclass
class CourseGeneralInfo:
    url: str
    naam: str  # e.g. zangles
    categorie: str  # e.g. muziek
    beschrijving: str


@dataclass
class Course:
    naam: str  # e.g zangles

    dag: str  # e.g. ma, di, ...
    tijd: str  # e.g. 20:00 - 22:00
    dag_tijd: str  # e.g. ma 20:00 - 22:00

    startdatum: str  # e.g. 2022-10-22
    duur: str  # e.g. 2 weken

    periode: str  # e.g. blok 2
    prijs: str  # e.g. €100
    cursusnummer: str  # 12345
    docent: str  # e.g. Yke Rusticus
    taal: str  # e.g. 🇳🇱
    cursus_type: str  # e.g. Fysiek
    status: str  # e.g. open
