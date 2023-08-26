import importlib.metadata
from enum import Enum
from pathlib import Path
from typing import Annotated, Optional

import typer
from devtools import debug  # noqa: F401
from rich import print
from rich.progress import Progress, SpinnerColumn, TextColumn

from .lib import Leno, LenoException
from .source import Source, get_source, get_sources

APP_NAME = "leno"
INSTANCE_URL = "http://127.0.0.1:8001"
app = typer.Typer()


def version_callback(value: bool):
    if value:
        print(importlib.metadata.version(APP_NAME))
        raise typer.Exit()


@app.callback()
def main(
    ctx: typer.Context,
    datasette_url: Annotated[
        str, typer.Option("--datasette-url", "-u", envvar="LENO_URL")
    ] = INSTANCE_URL,
    token: Annotated[str, typer.Option("--token", "-t", envvar="LENO_TOKEN")] = "",
    version: Annotated[
        Optional[bool],
        typer.Option("--version", "-V", callback=version_callback, is_eager=True),
    ] = None,
) -> None:
    ctx.ensure_object(dict)

    ctx.obj["app_dir"] = Path(typer.get_app_dir(APP_NAME))
    ctx.obj["data_dir"] = ctx.obj["app_dir"] / "data"
    ctx.obj["venv"] = ctx.obj["app_dir"] / "venv"


@app.command()
def update(
    ctx: typer.Context,
    source: Annotated[
        Optional[str], typer.Option("--source", "-s", help="Data source")
    ] = None,
    list_sources: Annotated[
        bool, typer.Option("--list-sources", "-l", help="List available sources")
    ] = False,
    data_dir: Annotated[
        Optional[Path],
        typer.Option(
            "--data-dir", "-d", help="Data directory where database is stored"
        ),
    ] = None,
) -> None:
    """
    Update data sources
    """
    # FIXME: ☝️ Default shouldn't be firefox, something more general like remote

    if list_sources:
        for s in get_sources():
            print(s)
        raise typer.Exit()

    if not source:
        print(":x: --source is required to update")
        raise typer.Exit(code=1)

    # Bail if passed --data-dir doesn't exist
    if data_dir and not data_dir.is_dir():
        print(f":x: {data_dir} is not a directory.")
        raise typer.Exit(code=1)

    # Create data dir if missing from default location
    if data_dir is None:
        data_path = ctx.obj["data_dir"]
        try:
            data_path.mkdir(parents=True)
            print(f"Created '{data_path}'")
        except FileExistsError:
            pass
    else:
        data_path = data_dir

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        transient=True,
    ) as progress:
        try:
            src: Source = get_source(source, data_path, ctx.obj["venv"])

            if not src.enabled:
                print(f":x: Source ({source}) is currently disabled.")
                raise typer.Exit()

            if not src.is_installed():
                install = progress.add_task(description="Installing...", total=None)
                src.install()
                progress.remove_task(install)

            progress.add_task(description="Updating...", total=None)
            src.update()
        except LenoException as error:
            print(f":x: {error}")
            raise typer.Exit(code=1)

    print(f":white_check_mark: Source ({source}) updated.")


class OutputEnum(str, Enum):
    plain = "plain"
    json = "json"


@app.command()
def firehose(
    ctx: typer.Context,
    output: OutputEnum = OutputEnum.plain,
    limit: int = 20,
    datasette_url: str = typer.Option(default=INSTANCE_URL, envvar="LENO_URL"),
    token: str = typer.Option(envvar="LENO_TOKEN"),
) -> None:
    """
    Everything, I mean everything
    """
    if not token:
        print(":x: Leno API token required. Set LENO_TOKEN or --token")
        raise typer.Exit(code=1)

    leno = Leno(datasette_url, token)
    items = leno.firehose()

    cnt = 0
    for item in items:
        if cnt == limit:
            break
        description = item.description
        if len(item.description) > 100:
            description = item.description[:100].strip() + "..."

        # FIXME: need to strip tags unrenderable by rich
        # Just here so it doesn't slow me down
        if "[/satire]" in item.description:
            description = description.strip("[/satire]")

        print(
            f"\[{item.label}] [bold]{item.title}[/bold]: {description} ({item.timestamp})"  # noqa: E501
        )
        cnt += 1


if __name__ == "__main__":
    app()
