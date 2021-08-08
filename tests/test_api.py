import pytest
from httpx import AsyncClient

from ebay_alerts_service.app import api
from ebay_alerts_service.db import Alert, DbConnection

ALERTS = [
    dict(email="email1@test.local", phrase="first", interval=2),
    dict(email="email2@test.local", phrase="second", interval=2),
]


@pytest.mark.asyncio
async def test_get_alerts(test_client: AsyncClient, db_connection: DbConnection):
    await db_connection.bulk_create([Alert(**a) for a in ALERTS])
    url = "/alerts"
    res = await test_client.get(url)
    assert res.status_code == 200
    data = res.json()
    assert len(data) == 2
    assert data == [
        {"id": 1, "email": "email1@test.local", "phrase": "first", "interval": 2},
        {"id": 2, "email": "email2@test.local", "phrase": "second", "interval": 2},
    ]


@pytest.mark.asyncio
async def test_create_alert(test_client: AsyncClient, mock_callbacks):
    url = "/alerts"
    payload = {"email": "first@test.local", "phrase": "first", "interval": 10}
    res = await test_client.post(url, json=payload)
    assert res.status_code == 201
    assert res.json()["id"] == 1
    api.state.conn.on_create.assert_called()


@pytest.mark.asyncio
async def test_get_alert(test_client: AsyncClient, db_connection: DbConnection):
    await db_connection.bulk_create([Alert(**a) for a in ALERTS])
    url = "/alerts/1"
    res = await test_client.get(url)
    assert res.status_code == 200
    assert res.json() == {
        "id": 1,
        "email": "email1@test.local",
        "phrase": "first",
        "interval": 2,
    }


@pytest.mark.asyncio
async def test_update_alert(
    test_client: AsyncClient, db_connection: DbConnection, mock_callbacks
):
    await db_connection.bulk_create([Alert(**a) for a in ALERTS])
    url = "/alerts/2"
    payload = {"phrase": "changed"}
    res = await test_client.patch(url, json=payload)
    assert res.status_code == 200
    assert res.json()["phrase"] == "changed"
    api.state.conn.on_update.assert_called()


@pytest.mark.asyncio
async def test_delete_alert(
    test_client: AsyncClient, db_connection: DbConnection, mock_callbacks
):
    await db_connection.bulk_create([Alert(**a) for a in ALERTS])
    url = "/alerts/2"
    res = await test_client.delete(url)
    assert res.status_code == 200
    assert res.json() == {
        "id": 2,
        "email": "email2@test.local",
        "phrase": "second",
        "interval": 2,
    }
    url = "/alerts"
    res = await test_client.get(url)
    assert res.status_code == 200
    data = res.json()
    assert len(data) == 1
    assert data == [
        {"id": 1, "email": "email1@test.local", "phrase": "first", "interval": 2}
    ]
    api.state.conn.on_delete.assert_called()
