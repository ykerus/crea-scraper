from dataclasses import dataclass


class CourseClass:
    def __post_init__(self):
        self._replace_commas()

    def _replace_comma(self, attr: str, replacement=";"):
        self.__setattr__(attr, self.__getattribute__(attr).replace(",", replacement))

    def _replace_commas(self, replacement=";"):
        for attr in self.__dict__.keys():
            self._replace_comma(attr, replacement)


@dataclass
class CourseGeneralInfo(CourseClass):
    url: str
    naam: str  # e.g. zangles
    categorie: str  # e.g. muziek
    beschrijving: str


@dataclass
class Course(CourseClass):
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
    status: str  # e.g. open
