from typing import List

from fastapi import APIRouter, HTTPException, Request, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError, NoResultFound

from ebay_alerts_service import db

from .models import alerts

router = APIRouter(
    prefix="/alerts",
    tags=["alerts"],
)


@router.get(
    "/", description="Get all alerts", response_model=List[alerts.AlertResponse]
)
async def get_alerts(request: Request):
    app = request.app
    stmt = select(db.Alert)
    data = [
        alerts.AlertResponse.from_orm(obj.Alert)
        for obj in await app.state.conn.select(stmt)
    ]
    return data


@router.post(
    "/",
    description="Create new alert",
    status_code=status.HTTP_201_CREATED,
    response_model=alerts.CreateAlertResponse,
    responses={409: {"details": "Alert with given email and phrase already exists"}},
)
async def create_alert(request: Request, alert_input: alerts.CreateAlert):
    app = request.app
    alert = db.Alert(
        email=alert_input.email,
        phrase=alert_input.phrase,
        interval=alert_input.interval,
    )
    try:
        await app.state.conn.create(alert)
    except IntegrityError:
        raise HTTPException(
            status_code=409,
            detail=f'Alert with email={alert_input.email} and phrase="{alert_input.phrase}" already exists',
        )
    return {"id": alert.id}


@router.get(
    "/{alert_id}",
    description="Get alert by id",
    response_model=alerts.AlertResponse,
    responses={404: {"detail": "Not found"}},
)
async def get_alert(request: Request, alert_id: int):
    stmt = select(db.Alert).where(db.Alert.id == alert_id)
    try:
        data = (await request.app.state.conn.select(stmt)).scalar_one()
    except NoResultFound:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not found")
    alert = alerts.AlertResponse.from_orm(data)
    return alert


@router.patch(
    "/{alert_id}",
    description="Update alert by id",
    response_model=alerts.AlertResponse,
    responses={
        404: {"detail": "Not found"},
        409: {"details": "Alert with given email and phrase already exists"},
    },
)
async def update_alert(request: Request, alert_id: int, alert_data: alerts.UpdateAlert):
    try:
        stmt = select(db.Alert).where(db.Alert.id == alert_id)
        alert = (await request.app.state.conn.select(stmt)).scalar_one()
        alert = await request.app.state.conn.update(alert, **alert_data.get_updated())
    except NoResultFound:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not found")
    except IntegrityError:
        raise HTTPException(
            status_code=409,
            detail="Another alert with given email and phrase exists",
        )
    return alerts.AlertResponse.from_orm(alert)


@router.delete(
    "/{alert_id}",
    description="Delete alert by id",
    response_model=alerts.AlertResponse,
    responses={404: {"detail": "Not found"}},
)
async def delete_alert(request: Request, alert_id: int):
    try:
        stmt = select(db.Alert).where(db.Alert.id == alert_id)
        alert = (await request.app.state.conn.select(stmt)).scalar_one()
        await request.app.state.conn.delete(alert)
    except NoResultFound:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not found")
    return alert
