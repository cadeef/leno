import configparser
import json
import os

# import venv
from contextlib import contextmanager
from pathlib import Path
from shutil import copy2
from subprocess import run
from typing import Callable, ClassVar

from sqlite_utils import Database

# from devtools import debug
from typing_extensions import override


class Source:
    """Base Source"""

    name: ClassVar[str] = ""
    description: ClassVar[str] = ""
    packages: ClassVar[list[str]] = []
    script: ClassVar[str] = ""
    enabled: ClassVar[bool] = True

    def __init__(self, data_dir: Path, venv: Path) -> None:
        self.data_dir = data_dir.resolve()
        self.venv = venv.resolve()

    def install(self) -> bool:
        if not self.venv.is_dir():
            # FIXME: venv.create is broken somehow in 3.11.5...
            # venv.create(self.venv, with_pip=True)
            run(
                ["python", "-m", "venv", self.venv],
                capture_output=True,
                check=True,
            )

        pip = self.venv / "bin/pip"
        for pkg in self.packages:
            run(
                [pip, "install", pkg],
                capture_output=True,
                check=True,
            )
        return True

    def update(self) -> bool:
        """
        Must be implemented by sub-class
        """
        return True

    @property
    def database(self) -> Path:
        return self.data_dir / f"{self.name}.db"

    @property
    def script_path(self) -> Path:
        if not self.script:
            raise AttributeError("Class variable 'script' must be defined")

        return self.venv / "bin" / self.script

    @property
    def auth_file_path(self):
        return self.data_dir / f"auth_{self.name}.json"

    def is_installed(self) -> bool:
        if self.script_path.is_file():
            return True
        else:
            return False


class FeedsSource(Source):
    """Feeds Source"""

    name = "feeds"
    description = "RSS feeds"
    packages = ["feed-to-sqlite"]
    script = "feed-to-sqlite"

    @override
    def update(self) -> bool:
        feeds = ["https://cade.pro/rss.xml"]
        run(
            [str(self.script_path), str(self.database)] + feeds,
            capture_output=True,
            check=True,
            shell=False,
        )
        return True


class FirefoxSource(Source):
    """Firefox Source"""

    name = "firefox"
    description = 'Firefox "places" (history & bookmarks)'
    packages = []
    script = ""

    @override
    def install(self) -> bool:
        # No install necessary
        return True

    @override
    def update(self) -> bool:
        firefox_path = Path.home() / "Library/Application Support/Firefox"
        firefox_profile_config = firefox_path / "profiles.ini"

        if firefox_profile_config.is_file():
            config = configparser.ConfigParser()
            config.read(firefox_profile_config)

            for i in config.sections():
                if i.startswith("Install"):
                    profile_path = firefox_path / config[i]["Default"]
                    # FIXME: Not exactly sure if there might be more than one Install
                    # section
                    break

            copy2(profile_path / "places.sqlite", self.database)
            # Disable sqlite WAL-mode
            Database(self.database).disable_wal()
        else:
            raise SourceException(
                f"Unable to determine profile, '{firefox_profile_config}' missing"
            )
        return True

    @override
    def is_installed(self) -> bool:
        return True


class GithubSource(Source):
    """Github Source"""

    name = "github"
    description = "Github"
    packages = ["github-to-sqlite"]
    script = "github-to-sqlite"

    @override
    def update(self) -> bool:
        repos = [
            "cadeef/cade-task",
            "cadeef/.files",
            "cadeef/firefox-to-sqlite",
            "cadeef/leno",
        ]
        data_points = ["commits", "releases"]

        with auth_file(
            self.auth_file_path,
            github_personal_token=os.environ["LENO_GITHUB_TOKEN"],
        ):
            # Fetch repos associated with user
            run(
                [
                    self.script_path,
                    "repos",
                    "--auth",
                    self.auth_file_path,
                    self.database,
                ],
                capture_output=True,
                check=True,
                shell=False,
            )

            # Fetch interesting data about repos
            for data_point in data_points:
                cmd = [
                    str(self.script_path),
                    data_point,
                    "--auth",
                    str(self.auth_file_path),
                    str(self.database),
                ] + repos
                run(
                    cmd,
                    capture_output=True,
                    check=True,
                    shell=False,
                )
        return True


class HealthkitSource(Source):
    """Healthkit Source"""

    name = "healthkit"
    description = "Apple health data"
    packages = ["healthkit-to-sqlite"]
    script = "healthkit-to-sqlite"

    @override
    def update(self) -> bool:
        run(
            [self.script_path, "exports/healthkit.zip", self.database],
            capture_output=True,
            check=True,
            shell=False,
        )
        return True


class MastodonSource(Source):
    """Mastodon Source"""

    name = "mastodon"
    description = "Mastodon"
    packages = ["mastodon-to-sqlite"]
    script = "mastodon-to-sqlite"

    @override
    def update(self) -> bool:
        data_points = ["bookmarks", "favourites", "followers", "followings", "statuses"]

        with auth_file(
            self.auth_file_path,
            mastodon_domain=os.environ["LENO_MASTODON_DOMAIN"],
            mastodon_access_token=os.environ["LENO_MASTODON_ACCESS_TOKEN"],
        ):
            for data_point in data_points:
                run(
                    [
                        self.script_path,
                        data_point,
                        "--auth",
                        self.auth_file_path,
                        self.database,
                    ],
                    capture_output=True,
                    check=True,
                    shell=False,
                )
        return True


class PhotosSource(Source):
    """Photos Source"""

    name = "photos"
    description = "Apple photos"
    packages = ["dogsheep-photos"]
    script = "dogsheep-photos"
    enabled = False

    @override
    def update(self) -> bool:
        run(
            [
                self.script_path,
                "apple-photos",
                "--library",
                Path.home() / "Pictures/Photos Library.photoslibrary",
                self.database,
            ],
            # capture_output=True,
            check=True,
            shell=False,
        )
        return True


class PocketSource(Source):
    """Pocket Source"""

    name = "pocket"
    description = "Pocket"
    packages = ["pocket-to-sqlite"]
    script = "pocket-to-sqlite"

    @override
    def update(self) -> bool:
        with auth_file(
            self.auth_file_path,
            pocket_consumer_key=os.environ["LENO_POCKET_CONSUMER_KEY"],
            pocket_username=os.environ["LENO_POCKET_USERNAME"],
            pocket_access_token=os.environ["LENO_POCKET_ACCESS_TOKEN"],
        ):
            run(
                [
                    self.script_path,
                    "fetch",
                    "--auth",
                    self.auth_file_path,
                    self.database,
                ],
                capture_output=True,
                check=True,
                shell=False,
            )
        return True


class SourceException(Exception):
    """Source Exception"""


@contextmanager
def auth_file(file: Path, **kwargs):
    if len(kwargs) == 0:
        raise KeyError("Requires 1 or more key/value pairs")

    file.write_text(json.dumps(kwargs))
    yield
    file.unlink()


def get_source(src: str, data_dir: Path, venv: Path) -> Source:
    """
    Returns a Source object
    """
    sources = get_sources()
    if src in sources:
        return sources[src](data_dir, venv)
    else:
        raise SourceException(f"Invalid source: {src}")


def get_sources() -> dict[str, Callable]:
    """
    Returns an dictionary of defined sources
    """
    symbols = globals()
    sources = {}
    for s in symbols:
        if s.endswith("Source") and s != "Source":
            name = symbols[s].name
            sources[name] = symbols[s]

    return sources
