# Queries

Interesting queries.

## Streaming

### Max

:::{note}
Covers max.com and previous hbomax.com.
:::

- [Pages browsed](http://127.0.0.1:8001/firefox?sql=select%0D%0A++id%2C%0D%0A++url%2C%0D%0A++title%2C%0D%0A++visit_count%2C%0D%0A++frecency%2C%0D%0A++last_visit_date%2C%0D%0A++description%0D%0Afrom%0D%0A++moz_places%0D%0Awhere%0D%0A++%22origin_id%22+in+%287%2C+235%2C+908%2C+909%2C+992%29%0D%0Aorder+by%0D%0A++visit_count+desc%2C%0D%0A++id)
- [Titles browsed](http://127.0.0.1:8001/firefox?sql=select%0D%0A++id%2C%0D%0A++url%2C%0D%0A++title%2C%0D%0A++visit_count%2C%0D%0A++frecency%2C%0D%0A++last_visit_date%2C%0D%0A++description%0D%0Afrom%0D%0A++moz_places%0D%0Awhere%0D%0A++%22origin_id%22+in+%287%2C+235%2C+908%2C+909%2C+992%29%0D%0A++and+%28url+like+%22%25%2Fshow%2F%25%22+or+url+like+%22%25%3Ahbo%3Apage%3A%25series%22%29%0D%0A++and+title+like+%22%25%E2%80%A2%25Max%22%0D%0Aorder+by%0D%0A++visit_count+desc%2C%0D%0A++id)

### Netflix

- [Titles browsed](http://127.0.0.1:8001/firefox?sql=select%0D%0A++title%2C%0D%0A++url%2C%0D%0A++visit_count%2C%0D%0A++frecency%2C%0D%0A++last_visit_date%0D%0Afrom%0D%0A++moz_places%0D%0Awhere%0D%0A++%22origin_id%22+%3D+48%0D%0A++and+url+like+%22%25browse%3Fjbv%25%22%0D%0Aorder+by%0D%0A++visit_count+desc%2C%0D%0A++id)

## Tech

- [Most used Python documentation](http://127.0.0.1:8001/firefox?sql=select+id%2C+url%2C+title%2C+rev_host%2C+visit_count%2C+hidden%2C+typed%2C+frecency%2C+last_visit_date%2C+guid%2C+foreign_count%2C+url_hash%2C+description%2C+preview_image_url%2C+site_name%2C+origin_id%2C+recalc_frecency%2C+alt_frecency%2C+recalc_alt_frecency+from+moz_places+where+%22origin_id%22+like+36+order+by+visit_count+desc+limit+101&p0=36)
