import typer
from web_scraping_er_v2.pipeline import pipeline
from typing_extensions import Annotated

app = typer.Typer(
    name="webscraping-exchange-rates",
    help="",
    add_completion=False,
)


@app.command("")
def main(
    currency: Annotated[
        str,
        typer.Option(
            "-c",
        ),
    ] = "LKR"
):
    pipeline(currency)


if __name__ == "__main__":
    app()
