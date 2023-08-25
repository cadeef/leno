# Notes

Getting Datasette/Dogsheep Going

## Datasette

- [Canned Queries](https://docs.datasette.io/en/stable/sql_queries.html#canned-queries)
- [Metadata](https://docs.datasette.io/en/stable/metadata.html)

## Tailscale

- <https://login.tailscale.com/admin/>
- [Enable tailscale on Fly](https://tailscale.com/kb/1132/flydotio/)

## Data Sources

### [google-takeout-to-sqlite](https://github.com/dogsheep/google-takeout-to-sqlite)

#### Issues

- Not totally broken, my first export (cade@) didn't have the data specified

### [healthkit-to-sqlite](https://github.com/dogsheep/healthkit-to-sqlite)

#### Issues

- Had to use <https://github.com/tomaskrehlik/healthkit-to-sqlite/tree/3e1b2945bc7c31be59e89c5fed86a5d2a59ebd5a> to get it running
- Still doesn't work completely with patch, failes on a type error

### [pocket-to-sqlite](https://github.com/dogsheep/pocket-to-sqlite)

#### Issues

- Requires auth.json, need to figure out how to do it with env variables

### [github-to-sqlite](https://github.com/dogsheep/github-to-sqlite)

### [feeds-to-sqlite](https://github.com/eyeseast/feed-to-sqlite)

### [mastodon-to-sqlite](https://github.com/myles/mastodon-to-sqlite)

## Workflows

### Update Data/ Publish

#### Actions

- <https://github.com/marketplace/actions/setup-just>
- <https://github.com/marketplace/actions/github-action-for-flyctl>
- <https://github.com/marketplace/actions/setup-python>
- <https://github.com/marketplace/actions/checkout>
- <https://github.com/marketplace/actions/git-auto-commit>
- <https://github.com/marketplace/actions/pre-commit>

## Publish

### Auth

:::{note}
This took some time
:::

- <https://github.com/simonw/datasette-auth-github>
- <https://github.com/simonw/datasette-auth-tokens>

### Required environment variables

| Variable | Dedpendent | Source |
| -------- | ---------- | ------ |
| GITHUB_TOKEN | github-to-sqlite | [Github Personal Access Token](https://github.com/settings/tokens) |
| POCKET_CONSUMER_KEY | pocket-to-sqlite | `pocket-to-sqlite auth` in auth.json |
| POCKET_USERNAME | pocket-to-sqlite | `pocket-to-sqlite auth` in auth.json |
| POCKET_ACCESS_TOKEN | pocket-to-sqlite | `pocket-to-sqlite auth` in auth.json |
| FLY_API_TOKEN | datasette-publish-fly, `flyctl` | `flyctl auth token` |
| GITHUB_CLIENT_ID | datasette-auth-github | [Github OAuth Settings](https://github.com/settings/developers) |
| GITHUB_CLIENT_SECRET | datasette-auth-github | [Github OAuth Settings](https://github.com/settings/developers) |
| MASTODON_DOMAIN | mastodon-to-sqlite | `mastodon-to-sqlite auth` in auth.json |
| MASTODON_ACCESS_TOKEN | mastodon-to-sqlite | `mastodon-to-sqlite auth` in auth.json |

## Adding a datasource

- Add environment variables to workflows (update.yml, publish.yml) where necessary
- Add environment variables to remote services (Github, Fly)
- Add update logic to Justfile

```sql
select
  repos.rowid as rowid,
  repos.html_url as repo,
  releases.html_url as release,
  substr(releases.published_at, 0, 11) as date,
  releases.body as body_markdown,
  releases.published_at,
  coalesce(repos.topics, '[]') as topics
from
  releases
  join repos on repos.id = releases.repo
order by
  releases.published_at desc;
```
