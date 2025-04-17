import importlib.metadata
import os
import re
import sys
from pathlib import Path
from typing import List, Optional

import typer
import wikipedia
from rich.console import Console
from rich.markdown import Markdown
from rich.progress import Progress, SpinnerColumn, TextColumn
from transformers import pipeline, Pipeline
from wikipedia.exceptions import DisambiguationError, PageError

APP_NAME = "Wiki Query CLI"
try:
    APP_VERSION = importlib.metadata.version("wiki_query_cli")
except importlib.metadata.PackageNotFoundError:
    APP_VERSION = "0.0.1"

console = Console()
app = typer.Typer(
    help=f"{APP_NAME} - Transform user requests into Wikipedia queries via a free neural model and fetch summaries.",
    no_args_is_help=True
)


def _initialize_model(model_name: str) -> Pipeline:
    """
    Initialize the text2text-generation pipeline for converting requests.
    """
    console.print(f"[cyan]Loading model '{model_name}'...[/cyan]")
    try:
        gen = pipeline("text2text-generation", model=model_name)
        console.print(f"[green]Model loaded successfully[/green]")
        return gen
    except Exception as e:
        console.print(f"[bold red]Failed to load model '{model_name}': {e}[/bold red]")
        sys.exit(1)


def _convert_to_query(
        prompt: str,
        gen: Pipeline,
        max_length: int = 64
) -> str:
    """
    Use the neural model to rewrite the user prompt into a concise Wikipedia search query.
    """
    instruction = (
            "Convert the following user request into a concise search query for Wikipedia:\n" + prompt.strip()
    )
    out = gen(instruction, max_length=max_length, truncation=True)
    return out[0].get("generated_text", out[0].get("text", "")).strip()


def _select_page_title(results: List[str]) -> str:
    """
    If multiple Wikipedia pages match, prompt the user to select one.
    """
    if len(results) == 1:
        return results[0]
    console.print("[yellow]Multiple articles found:[/yellow]")
    for idx, title in enumerate(results[:5], start=1):
        console.print(f"{idx}. {title}")
    choice = console.input("Select article number [1]: ").strip()
    try:
        idx = int(choice) if choice else 1
        if not 1 <= idx <= min(len(results), 5):
            raise ValueError
    except ValueError:
        console.print("[red]Invalid choice, defaulting to 1[/red]")
        idx = 1
    return results[idx - 1]


def _fetch_summary(query: str, sentences: int = 5) -> str:
    """
    Sanitize the query, search Wikipedia, allow page selection, and return the summary.
    """
    # 1) Sanitize hyphens and unusual characters
    sanitized = re.sub(r"[–—-]+", " ", query).strip()
    console.print(f"[cyan]Searching Wikipedia for:[/cyan] [bold]{sanitized}[/bold]")

    # 2) Search titles
    try:
        results = wikipedia.search(sanitized)
    except Exception as e:
        console.print(f"[bold red]Search error:[/bold red] {e}")
        sys.exit(1)

    if not results:
        console.print(f"[yellow]No results found for '{sanitized}'.[/yellow]")
        sys.exit(0)

    # 3) Choose page title
    page_title = _select_page_title(results)
    console.print(f"[cyan]Loading page:[/cyan] [green]{page_title}[/green]")

    # 4) Load page object
    try:
        page = wikipedia.page(page_title, auto_suggest=False, redirect=True)
    except DisambiguationError as e:
        alt = e.options[0]
        console.print(f"[yellow]Disambiguation: using first option '{alt}'[/yellow]")
        page = wikipedia.page(alt)
    except PageError:
        console.print(f"[yellow]Page '{page_title}' not found, trying auto_suggest...[/yellow]")
        try:
            page = wikipedia.page(sanitized, auto_suggest=True)
        except (DisambiguationError, PageError) as e:
            console.print(f"[bold red]Failed after auto_suggest: {e}[/bold red]")
            sys.exit(1)

    # 5) Extract summary sentences
    text = page.summary.replace("\n", " ").strip()
    parts = text.split(". ")
    summary = ". ".join(parts[:sentences]) + ("…" if len(parts) > sentences else "")

    return f"**{page.title}**\n\n{summary}"


@app.command()
def ask(
        message: str = typer.Argument(..., help="The user request to process."),
        model_name: str = typer.Option(
            "google/flan-t5-base", "--model", "-m",
            help="The Hugging Face model to use for rewriting the query."
        ),
        sentences: int = typer.Option(
            5, "--sentences", "-s",
            help="Number of sentences to include in the Wikipedia summary."
        ),
        cache_dir: Optional[Path] = typer.Option(
            None, "--cache-dir", help="Optional cache directory for Hugging Face models."
        ),
):
    """
    Transform a user request into a Wikipedia query using a free neural model and display the summary.
    """
    if cache_dir:
        os.environ["TRANSFORMERS_CACHE"] = str(cache_dir)

    gen = _initialize_model(model_name)

    with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            transient=True,
            console=console,
    ) as progress:
        progress.add_task("Converting request into Wikipedia query...", total=None)
        wiki_query = _convert_to_query(message, gen)

    summary = _fetch_summary(wiki_query, sentences=sentences)
    console.print(Markdown(summary))


@app.callback()
def version(
        _version: bool = typer.Option(
            None, "--version",
            callback=lambda v: (console.print(f"{APP_NAME} v{APP_VERSION}"), sys.exit(0)) if v else None,
            is_eager=True,
            help="Show version information and exit."
        )
):
    pass


if __name__ == "__main__":
    app()
