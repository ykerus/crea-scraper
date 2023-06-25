import typer

from crea_scraper import data, scraper

app = typer.Typer()

OUTPUT_PATH = typer.Argument(
    default="output/course_data.csv", help="Path to write data to"
)


@app.callback()
def main() -> None:
    # TODO: configure logger
    ...


@app.command()
def crea(
    output_path: str = OUTPUT_PATH,
) -> None:
    """Scrape CREA website

    Usage: run `scrape crea`
    Help: run `scrape crea --help`

    """
    course_data = scraper.run()
    data.write_course_data(course_data, output_path)
