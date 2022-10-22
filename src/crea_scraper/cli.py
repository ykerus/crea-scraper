import time

import pandas as pd
import typer

app = typer.Typer()

OUTPUT_PATH = typer.Argument(default="output/data.csv", help="Path to write data to")


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

    pd.DataFrame(
        [
            {"x": time.time(), "y": time.time() + 10},
            {"time": time.time() + 1, "y": time.time() + 11},
        ]
    ).to_csv(output_path)
