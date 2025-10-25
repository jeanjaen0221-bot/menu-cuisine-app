from __future__ import annotations
import uuid
from datetime import date, time, datetime
from enum import Enum
from typing import List, Optional

from sqlmodel import Field, SQLModel


class ReservationStatus(str, Enum):
    draft = "draft"
    confirmed = "confirmed"
    printed = "printed"


class MenuItemBase(SQLModel):
    name: str
    type: str  # entrée / plat / dessert
    active: bool = True


class MenuItem(MenuItemBase, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True, index=True)
    type: str
    active: bool = True


class MenuItemCreate(MenuItemBase):
    pass


class MenuItemRead(MenuItemBase):
    id: uuid.UUID


class MenuItemUpdate(SQLModel):
    name: Optional[str] = None
    type: Optional[str] = None
    active: Optional[bool] = None


class ReservationItemBase(SQLModel):
    type: str  # entrée / plat / dessert
    name: str
    quantity: int = 1


class ReservationItem(ReservationItemBase, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    reservation_id: uuid.UUID | None = Field(default=None, foreign_key="reservation.id")
    type: str
    name: str
    quantity: int = 0


class ReservationItemCreate(ReservationItemBase):
    pass


class ReservationItemRead(ReservationItemBase):
    id: uuid.UUID


class ReservationBase(SQLModel):
    client_name: str
    pax: int
    service_date: date
    arrival_time: time
    drink_formula: str
    notes: Optional[str] = None
    status: ReservationStatus = ReservationStatus.draft


class Reservation(ReservationBase, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True, index=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class ReservationCreate(ReservationBase):
    items: List[ReservationItemCreate] = Field(default_factory=list)


# Input model variant that accepts strings for date/time (used by create endpoint)
class ReservationCreateIn(SQLModel):
    client_name: str
    pax: int
    service_date: str
    arrival_time: str
    drink_formula: str
    notes: Optional[str] = None
    status: ReservationStatus = ReservationStatus.draft
    items: List[ReservationItemCreate] = Field(default_factory=list)


class ReservationUpdate(SQLModel):
    client_name: Optional[str] = None
    pax: Optional[int] = None
    service_date: Optional[str] = None
    arrival_time: Optional[str] = None
    drink_formula: Optional[str] = None
    notes: Optional[str] = None
    status: Optional[ReservationStatus] = None
    items: Optional[List[ReservationItemCreate]] = None


class ReservationRead(ReservationBase):
    id: uuid.UUID
    created_at: datetime
    updated_at: datetime
    items: List[ReservationItemRead] = Field(default_factory=list)


# Key/Value settings storage (e.g., Zenchef token and restaurant id)
class Setting(SQLModel, table=True):
    key: str = Field(primary_key=True)
    value: str
