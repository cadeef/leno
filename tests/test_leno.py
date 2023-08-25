import pytest
from devtools import debug  # noqa: F401

from leno.lib import Leno, LenoException, Query

leno = Leno("http://127.0.0.1:8001", "a-very-nice-token-for-testing")


@pytest.mark.parametrize(
    "url,expected",
    (
        # Exact
        (
            "http://127.0.0.1:8001/mastodon/bookmarks.json?_shape=array",
            "http://127.0.0.1:8001/mastodon/bookmarks.json?_shape=array",
        ),
        # Wrong shape
        (
            "http://127.0.0.1:8001/mastodon/bookmarks.json?_shape=object",
            "http://127.0.0.1:8001/mastodon/bookmarks.json?_shape=array",
        ),
        # Missing .json
        (
            "http://127.0.0.1:8001/firefox/frecent_docs",
            "http://127.0.0.1:8001/firefox/frecent_docs.json?_shape=array",
        ),
        # Plain-jane, no _shape
        (
            "http://127.0.0.1:8001/mastodon/bookmarks.json",
            "http://127.0.0.1:8001/mastodon/bookmarks.json?_shape=array",
        ),
        # No hostname
        (
            "/github/releases.json",
            "http://127.0.0.1:8001/github/releases.json?_shape=array",
        ),
        # Different server than Leno(url)
        (
            "http://example.com/github/releases.json",
            "http://example.com/github/releases.json?_shape=array",
        ),
        # Extra query parameters
        (
            "http://127.0.0.1:8001/github/releases.json?_labels=on&_sort_desc=published_at",
            "http://127.0.0.1:8001/github/releases.json?_labels=on&_sort_desc=published_at&_shape=array",
        ),
    ),
)
def test_leno__build_fetch_url(url, expected):
    assert leno._build_fetch_url(url) == expected


def test_leno__build_fetch_url_no_path():
    with pytest.raises(LenoException):
        leno._build_fetch_url("https://example.com")


def test_query_functions():
    query = Query.from_url(
        "http://127.0.0.1:8001/mastodon/bookmarks.json?_shape=object&_sort=bob"
    )

    query.sort("testaroo")
    assert (
        query.url()
        == "http://127.0.0.1:8001/mastodon/bookmarks.json?_shape=object&_sort=testaroo"
    )
    query.sort("bill", reverse=True)
    assert (
        query.url()
        == "http://127.0.0.1:8001/mastodon/bookmarks.json?_shape=object&_sort_desc=bill"
    )
    query.limit(10)
    assert (
        query.url()
        == "http://127.0.0.1:8001/mastodon/bookmarks.json?_shape=object&_sort_desc=bill&_size=10"
    )
    query.json_mode("array")
    assert (
        query.url()
        == "http://127.0.0.1:8001/mastodon/bookmarks.json?_shape=array&_sort_desc=bill&_size=10"
    )
