URL = "https://example.com/some/long/page"


def create(client, **extra):
    return client.post("/api/links", json={"original_url": URL, **extra})


def test_create_link_generates_code(client):
    res = create(client)
    assert res.status_code == 201
    data = res.json()
    assert len(data["code"]) == 7
    assert data["short_url"].endswith(data["code"])
    assert data["original_url"] == URL


def test_create_link_with_custom_code(client):
    res = create(client, custom_code="my-link")
    assert res.status_code == 201
    assert res.json()["code"] == "my-link"


def test_duplicate_custom_code_returns_409(client):
    create(client, custom_code="taken")
    assert create(client, custom_code="taken").status_code == 409


def test_reserved_code_returns_409(client):
    assert create(client, custom_code="docs").status_code == 409


def test_invalid_url_returns_422(client):
    res = client.post("/api/links", json={"original_url": "not-a-url"})
    assert res.status_code == 422


def test_read_and_list_links(client):
    code = create(client).json()["code"]
    assert client.get(f"/api/links/{code}").json()["code"] == code
    assert len(client.get("/api/links").json()) == 1


def test_read_unknown_link_returns_404(client):
    assert client.get("/api/links/unknown").status_code == 404


def test_update_link(client):
    code = create(client).json()["code"]
    res = client.patch(f"/api/links/{code}", json={"original_url": "https://new.dev/x"})
    assert res.status_code == 200
    assert res.json()["original_url"] == "https://new.dev/x"


def test_delete_link(client):
    code = create(client).json()["code"]
    assert client.delete(f"/api/links/{code}").status_code == 204
    assert client.get(f"/api/links/{code}").status_code == 404


def test_redirect(client):
    code = create(client).json()["code"]
    res = client.get(f"/{code}", follow_redirects=False)
    assert res.status_code == 307
    assert res.headers["location"] == URL


def test_redirect_unknown_code_returns_404(client):
    assert client.get("/nope123", follow_redirects=False).status_code == 404


def test_stats_count_clicks_and_referrers(client):
    code = create(client).json()["code"]
    for _ in range(3):
        client.get(f"/{code}", follow_redirects=False, headers={"referer": "https://twitter.com"})
    client.get(f"/{code}", follow_redirects=False)  # direct visit

    stats = client.get(f"/api/links/{code}/stats").json()
    assert stats["total_clicks"] == 4
    assert stats["top_referrers"][0] == {"referrer": "https://twitter.com", "clicks": 3}
    assert {"referrer": "direct", "clicks": 1} in stats["top_referrers"]
    assert sum(d["clicks"] for d in stats["clicks_per_day"]) == 4