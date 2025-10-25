from __future__ import annotations
import os
import uuid
from datetime import date, datetime, time as dtime
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse
from sqlalchemy import delete
from sqlmodel import Session, select

from ..database import get_session
from ..models import (
    Reservation,
    ReservationCreate,
    ReservationItem,
    ReservationRead,
    ReservationUpdate,
)
from ..pdf_service import generate_reservation_pdf, generate_day_pdf

router = APIRouter(prefix="/api/reservations", tags=["reservations"])


@router.get("", response_model=List[ReservationRead])
def list_reservations(
    q: Optional[str] = None,
    service_date: Optional[date] = None,
    session: Session = Depends(get_session),
):
    stmt = select(Reservation).order_by(Reservation.service_date.desc(), Reservation.arrival_time.asc())
    results = session.exec(stmt).all()
    rows: List[Reservation] = results
    if q:
        rows = [r for r in rows if q.lower() in r.client_name.lower()]
    if service_date:
        rows = [r for r in rows if r.service_date == service_date]

    # Attach items for read model
    out: List[ReservationRead] = []
    for r in rows:
        items = session.exec(select(ReservationItem).where(ReservationItem.reservation_id == r.id)).all()
        rr = ReservationRead(**r.model_dump(), items=items)
        out.append(rr)
    return out


@router.post("", response_model=ReservationRead)
def create_reservation(payload: ReservationCreate, session: Session = Depends(get_session)):
    res = Reservation(**payload.model_dump(exclude={"items"}))
    session.add(res)
    session.commit()
    session.refresh(res)

    for it in payload.items:
        rit = ReservationItem(**it.model_dump(), reservation_id=res.id)
        session.add(rit)
    session.commit()

    items = session.exec(select(ReservationItem).where(ReservationItem.reservation_id == res.id)).all()
    return ReservationRead(**res.model_dump(), items=items)


@router.get("/{reservation_id}", response_model=ReservationRead)
def get_reservation(reservation_id: uuid.UUID, session: Session = Depends(get_session)):
    res = session.get(Reservation, reservation_id)
    if not res:
        raise HTTPException(404, "Reservation not found")
    items = session.exec(select(ReservationItem).where(ReservationItem.reservation_id == res.id)).all()
    return ReservationRead(**res.model_dump(), items=items)


@router.put("/{reservation_id}", response_model=ReservationRead)
def update_reservation(reservation_id: uuid.UUID, payload: ReservationUpdate, session: Session = Depends(get_session)):
    res = session.get(Reservation, reservation_id)
    if not res:
        raise HTTPException(404, "Reservation not found")

    update_data = payload.model_dump(exclude_unset=True, exclude={"items"})
    # Normalize string date/time to proper types
    if isinstance(update_data.get("service_date"), str):
        try:
            update_data["service_date"] = date.fromisoformat(update_data["service_date"][:10])
        except Exception:
            del update_data["service_date"]
    if isinstance(update_data.get("arrival_time"), str):
        try:
            t = update_data["arrival_time"]
            if len(t) == 5:
                t = f"{t}:00"
            update_data["arrival_time"] = dtime.fromisoformat(t)
        except Exception:
            del update_data["arrival_time"]
    for k, v in update_data.items():
        setattr(res, k, v)
    # touch updated_at
    try:
        setattr(res, 'updated_at', datetime.utcnow())
    except Exception:
        pass
    session.add(res)

    if payload.items is not None:
        session.exec(delete(ReservationItem).where(ReservationItem.reservation_id == res.id))
        for it in payload.items:
            rit = ReservationItem(**it.model_dump(), reservation_id=res.id)
            session.add(rit)

    session.commit()
    session.refresh(res)
    items = session.exec(select(ReservationItem).where(ReservationItem.reservation_id == res.id)).all()
    return ReservationRead(**res.model_dump(), items=items)


@router.delete("/{reservation_id}")
def delete_reservation(reservation_id: uuid.UUID, session: Session = Depends(get_session)):
    res = session.get(Reservation, reservation_id)
    if not res:
        raise HTTPException(404, "Reservation not found")
    session.delete(res)
    session.exec(delete(ReservationItem).where(ReservationItem.reservation_id == res.id))
    session.commit()
    return {"ok": True}


@router.post("/{reservation_id}/duplicate", response_model=ReservationRead)
def duplicate_reservation(reservation_id: uuid.UUID, session: Session = Depends(get_session)):
    res = session.get(Reservation, reservation_id)
    if not res:
        raise HTTPException(404, "Reservation not found")
    items = session.exec(select(ReservationItem).where(ReservationItem.reservation_id == res.id)).all()

    new_res = Reservation(**{k: getattr(res, k) for k in [
        'client_name','pax','service_date','arrival_time','drink_formula','notes','status'
    ]})
    session.add(new_res)
    session.commit()
    session.refresh(new_res)

    for it in items:
        session.add(ReservationItem(type=it.type, name=it.name, quantity=it.quantity, reservation_id=new_res.id))
    session.commit()

    new_items = session.exec(select(ReservationItem).where(ReservationItem.reservation_id == new_res.id)).all()
    return ReservationRead(**new_res.model_dump(), items=new_items)


@router.get("/{reservation_id}/pdf")
def export_reservation_pdf(reservation_id: uuid.UUID, session: Session = Depends(get_session)):
    res = session.get(Reservation, reservation_id)
    if not res:
        raise HTTPException(404, "Reservation not found")
    items = session.exec(select(ReservationItem).where(ReservationItem.reservation_id == res.id)).all()
    path = generate_reservation_pdf(res, items)
    return FileResponse(path, filename=os.path.basename(path), media_type="application/pdf")


@router.get("/day/{d}/pdf")
def export_day_pdf(d: date, session: Session = Depends(get_session)):
    rows = session.exec(select(Reservation).where(Reservation.service_date == d).order_by(Reservation.arrival_time.asc())).all()
    items_by_res = {}
    for r in rows:
        items = session.exec(select(ReservationItem).where(ReservationItem.reservation_id == r.id)).all()
        items_by_res[str(r.id)] = items
    path = generate_day_pdf(d, rows, items_by_res)
    return FileResponse(path, filename=os.path.basename(path), media_type="application/pdf")
