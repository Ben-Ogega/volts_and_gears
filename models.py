#_*_ coding: utf-8 _*_
from sqlalchemy import create_engine, String, Integer, Float, ForeignKey, DateTime
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship, sessionmaker
from datetime import datetime
from typing import List

class Base(DeclarativeBase):
    pass

# ── VEHICLE TABLE ────────────────────────────────────────────
class VehicleDB(Base):
    __tablename__ = 'fleet'

    id: Mapped[int] = mapped_column(primary_key=True)
    vin: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    v_type: Mapped[str] = mapped_column(String(20)) 
    make: Mapped[str] = mapped_column(String(50))
    model: Mapped[str] = mapped_column(String(50))
    year: Mapped[int] = mapped_column(Integer)
    engine_hours: Mapped[float] = mapped_column(Float, default=0.0)
    odometer: Mapped[int] = mapped_column(Integer, default=0)
    fuel_level: Mapped[float] = mapped_column(Float, default=0.0)
    fuel_capacity: Mapped[float] = mapped_column(Float, default=1.0)
    status: Mapped[str] = mapped_column(String(20), default="Available")
    
    # Specs
    capacity: Mapped[float] = mapped_column(Float, nullable=True) 
    axles: Mapped[int] = mapped_column(Integer, nullable=True)
    passenger_capacity: Mapped[int] = mapped_column(Integer, nullable=True)

    # RELATIONSHIP: One vehicle can have many inspections
    inspections: Mapped[List["InspectionDB"]] = relationship(back_populates="vehicle")

# ── DRIVER TABLE ─────────────────────────────────────────────
class DriverDB(Base):
    __tablename__ = 'drivers'

    id: Mapped[int] = mapped_column(primary_key=True)
    employee_id: Mapped[str] = mapped_column(String(20), unique=True)
    name: Mapped[str] = mapped_column(String(100))
    licence_class: Mapped[str] = mapped_column(String(10))
    status: Mapped[str] = mapped_column(String(20), default="Off Duty")

    # RELATIONSHIP: One driver can perform many inspections
    inspections: Mapped[List["InspectionDB"]] = relationship(back_populates="driver")

# ── INSPECTION TABLE ─────────────────────────────────────────
class InspectionDB(Base):
    __tablename__ = 'inspections'

    id: Mapped[int] = mapped_column(primary_key=True)
    date: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)
    
    # Foreign Keys (The "Bolts")
    vehicle_id: Mapped[int] = mapped_column(ForeignKey("fleet.id"))
    driver_id: Mapped[int] = mapped_column(ForeignKey("drivers.id"))
    
    verdict: Mapped[str] = mapped_column(String(10)) # PASSED/FAILED
    notes: Mapped[str] = mapped_column(String(255), nullable=True)

    # Back-references
    vehicle: Mapped["VehicleDB"] = relationship(back_populates="inspections")
    driver: Mapped["DriverDB"] = relationship(back_populates="inspections")

# ── DATABASE SETUP ───────────────────────────────────────────
engine = create_engine('sqlite:///fleet.db')
Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)
session = Session()