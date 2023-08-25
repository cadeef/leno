import datetime
import itertools
from dataclasses import dataclass
from typing import Generator
from urllib.parse import ParseResult, parse_qs, urlencode, urljoin, urlparse, urlunparse

import httpx
from bs4 import BeautifulSoup

# from devtools import debug  # noqa: F401


@dataclass
class Item:
    """Generic Item"""

    title: str
    description: str
    label: str
    timestamp: datetime.datetime
    link: str | None = None

    def __str__(self):
        return (
            f"[{self.category}] {self.title}: {self.description}\nat {self.timestamp}"
        )

    def to_markdown(self):
        return f"[{self.title}]({self.link}): {self.description}"


@dataclass
class Leno:
    url: str
    token: str

    def firehose(self):
        hose = itertools.chain(
            self.mastodon_bookmarks(), self.github_releases(), self.mastodon_favorites()
        )
        return sorted(hose, key=lambda i: i.timestamp, reverse=True)

    def fetch_json(self, url: str) -> list[dict]:
        url = self._build_fetch_url(url)

        headers = {"authorization": f"Bearer {self.token}"}
        r = httpx.get(url, headers=headers)

        return r.json()

    def _build_fetch_url(self, url: str) -> str:
        """
        Provides a qualified URL for consistent data handling

        :param url: a datasette query URL
        """
        query = Query.from_url(url)
        # Set json output mode to array
        query.json_mode("array")
        q_url = query.url()

        # Prepend datasette server to url if passed only a path
        # We don't always overwrite it since I might one day query another datasette
        # server at the same time
        if not query.host:
            q_url = urljoin(self.url, q_url)

        return q_url

    def github_releases(self) -> Generator[Item, None, None]:
        result = self.fetch_json("/github/releases.json?_labels=on")

        if result:
            for r in result:
                yield Item(
                    title=f"{r['repo']['label']} {r['tag_name']}",
                    description=r["body"],
                    label="release",
                    timestamp=r["published_at"],
                    link=r["html_url"],
                )

    def mastodon_bookmarks(self) -> Generator[Item, None, None]:
        result = self.fetch_json("/mastodon/bookmarks.json")

        if result:
            for r in result:
                yield Item(
                    title=f":elephant: {r['username']}",
                    # FIXME: Simply stripping the tags out isn't the *most* readable,
                    # probaly should parse for links, etc
                    description=BeautifulSoup(r["content"], "html.parser").text,
                    label="bookmark",
                    timestamp=r["created_at"],
                    link=f"{r['url']}/{r['id']}",
                )

    def mastodon_favorites(self) -> Generator[Item, None, None]:
        result = self.fetch_json("/mastodon/favorites.json")

        if result:
            for r in result:
                yield Item(
                    title=f":elephant: {r['username']}",
                    # FIXME: Simply stripping the tags out isn't the *most* readable,
                    # probaly should parse for links, etc
                    description=BeautifulSoup(r["content"], "html.parser").text,
                    label="favorite",
                    timestamp=r["created_at"],
                    link=f"{r['url']}/{r['id']}",
                )


class LenoException(Exception):
    """Base Leno Exception"""


@dataclass
class Query:
    """Client for making datasette queries"""

    protocol: str
    host: str
    path: str
    args: dict

    def __post_init__(self) -> None:
        if not self.path:
            raise LenoException("Path is missing from URL")
        # Add .json for proper output if it's missing
        if not self.path.endswith(".json"):
            self.path += ".json"

    def url(self) -> str:
        return urlunparse(
            ParseResult(
                scheme=self.protocol,
                netloc=self.host,
                path=self.path,
                params="",
                query=self.query_string(),
                fragment="",
            )
        )

    def query_string(self) -> str:
        return urlencode(self.args)

    def json_mode(self, mode) -> None:
        self.args["_shape"] = mode

    def sort(self, column: str, reverse: bool = False) -> None:
        if reverse:
            self.args["_sort_desc"] = column
            if "_sort" in self.args:
                del self.args["_sort"]
        else:
            self.args["_sort"] = column
            if "_sort_desc" in self.args:
                del self.args["_sort_desc"]

    def limit(self, limit: int) -> None:
        # FIXME: Doesn't seem to work for canned queries
        self.args["_size"] = str(limit)

    @staticmethod
    def from_url(url: str) -> "Query":
        parsed_url = urlparse(url)

        args = parse_qs(parsed_url.query)
        sani_args = {}
        for arg in args:
            # FIXME: Specifically breaks _col, _nocol, _label from
            # https://docs.datasette.io/en/stable/json_api.html#special-table-arguments
            # for simplicity.
            if type(args[arg]) == "list" and len(args["arg"]) > 1:
                raise LenoException(
                    f"URL with repeated '{arg}' in the query string, bailing."
                )
            sani_args[arg] = args[arg][0]

        return Query(
            protocol=parsed_url.scheme,
            host=parsed_url.netloc,
            path=parsed_url.path,
            args=sani_args,
        )
