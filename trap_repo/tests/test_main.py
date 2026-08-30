"""Tests for the item API."""

import pytest

from app.main import app, store
from app.models import ItemStore


@pytest.fixture
def client():
    app.config["TESTING"] = True
    with app.test_client() as client:
        store._items.clear()
        yield client


@pytest.fixture
def sample_item(client):
    resp = client.post(
        "/items", json={"name": "Widget", "description": "A widget", "price": 9.99}
    )
    return resp.get_json()


class TestHealthEndpoint:
    def test_health_returns_ok(self, client):
        resp = client.get("/health")
        assert resp.status_code == 200
        assert resp.get_json()["status"] == "ok"


class TestCreateItem:
    def test_create_item_success(self, client):
        resp = client.post(
            "/items", json={"name": "Gadget", "description": "Cool", "price": 19.99}
        )
        assert resp.status_code == 201
        data = resp.get_json()
        assert data["name"] == "Gadget"
        assert data["price"] == 19.99
        assert "id" in data

    def test_create_item_missing_name(self, client):
        resp = client.post("/items", json={"description": "No name"})
        assert resp.status_code == 400
        assert "error" in resp.get_json()

    def test_create_item_defaults(self, client):
        resp = client.post("/items", json={"name": "Minimal"})
        assert resp.status_code == 201
        data = resp.get_json()
        assert data["description"] == ""
        assert data["price"] == 0.0


class TestListItem:
    def test_list_empty(self, client):
        resp = client.get("/items")
        assert resp.status_code == 200
        data = resp.get_json()
        assert data["items"] == []
        assert data["count"] == 0

    def test_list_with_items(self, client, sample_item):
        resp = client.get("/items")
        data = resp.get_json()
        assert data["count"] == 1
        assert len(data["items"]) == 1


class TestGetItem:
    def test_get_existing_item(self, client, sample_item):
        item_id = sample_item["id"]
        resp = client.get(f"/items/{item_id}")
        assert resp.status_code == 200
        assert resp.get_json()["name"] == "Widget"

    def test_get_missing_item(self, client):
        resp = client.get("/items/nonexistent")
        assert resp.status_code == 404
        assert "error" in resp.get_json()


class TestDeleteItem:
    def test_delete_existing_item(self, client, sample_item):
        item_id = sample_item["id"]
        resp = client.delete(f"/items/{item_id}")
        assert resp.status_code == 200
        assert "deleted" in resp.get_json()["message"]
        # Verify it's gone
        resp = client.get(f"/items/{item_id}")
        assert resp.status_code == 404

    def test_delete_missing_item(self, client):
        resp = client.delete("/items/nonexistent")
        assert resp.status_code == 404


class TestItemStore:
    def test_count(self):
        store = ItemStore()
        assert store.count() == 0
        store.create("Test")
        assert store.count() == 1

    def test_to_dict(self):
        store = ItemStore()
        item = store.create("Widget", "desc", 5.0)
        d = item.to_dict()
        assert d["name"] == "Widget"
        assert d["description"] == "desc"
        assert d["price"] == 5.0
