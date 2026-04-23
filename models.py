#_*_ coding: utf-8 _*_
from sqlalchemy import create_engine, Column, Integer, String, Float, Boolean
# --- Updated Import ---
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, sessionmaker
from datetime import datetime

# --- Modern 2.0 Way to define the Base ---
class Base(DeclarativeBase):
    pass

class VehicleDB(Base):
    __tablename__ = 'fleet'

    # Using mapped_column is the modern standard
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    vin: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    v_type: Mapped[str] = mapped_column(String(20))  # 'Truck' or 'Van'
    make: Mapped[str] = mapped_column(String(50))
    model: Mapped[str] = mapped_column(String(50))
    year: Mapped[int] = mapped_column(Integer)
    engine_hours: Mapped[float] = mapped_column(Float, default=0.0)
    odometer: Mapped[int] = mapped_column(Integer, default=0)
    fuel_level: Mapped[float] = mapped_column(Float, default=0.0)
    fuel_capacity: Mapped[float] = mapped_column(Float, default=1.0)
    status: Mapped[str] = mapped_column(String(20), default="Available")
    
    # Specific Specs (Nullable because they depend on v_type)
    capacity: Mapped[float] = mapped_column(Float, nullable=True) 
    axles: Mapped[int] = mapped_column(Integer, nullable=True)
    passenger_capacity: Mapped[int] = mapped_column(Integer, nullable=True)

    @property
    def is_service_due(self):
        return self.engine_hours >= 5000

    @property
    def fuel_percentage(self):
        return round((self.fuel_level / self.fuel_capacity) * 100, 2)

    def __repr__(self):
        return f"<Vehicle(VIN='{self.vin}', Type='{self.v_type}')>"

# ── ENGINE SETUP ─────────────────────────────────────────────
engine = create_engine('sqlite:///fleet.db')
Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)
session = Session()

# ── CORE FUNCTIONS ───────────────────────────────────────────
def add_vehicle(data_dict):
    try:
        # We extract the type safely
        current_type = data_dict.pop('type', 'Truck')
        
        # We create the object using the modern Mapped columns
        new_v = VehicleDB(v_type=current_type, **data_dict)
        session.add(new_v)
        session.commit()
        return f"Successfully added {new_v.vin}."
    except Exception as e:
        session.rollback()
        return f"Error: {e}"


def seed_professional_data():
    """Seeds the database with a diverse, professional dataset."""
    professional_entries = [
        # --- Heavy Duty Trucks ---
        {"type": "Truck", "vin": "KDC-H01", "make": "Mercedes", "model": "Actros", "year": 2021, 
        "engine_hours": 5100, "odometer": 150000, "fuel_level": 300, "fuel_capacity": 500, "capacity": 30000, "axles": 3},
        {"type": "Truck", "vin": "KDC-H02", "make": "Scania", "model": "G440", "year": 2022, 
        "engine_hours": 2100, "odometer": 85000, "fuel_level": 120, "fuel_capacity": 450, "capacity": 28000, "axles": 3},
        {"type": "Truck", "vin": "KDC-H03", "make": "MAN", "model": "TGX", "year": 2019, 
        "engine_hours": 7200, "odometer": 250000, "fuel_level": 50, "fuel_capacity": 400, "capacity": 25000, "axles": 2},
        {"type": "Truck", "vin": "KDC-H04", "make": "Volvo", "model": "FH16", "year": 2024, 
        "engine_hours": 450, "odometer": 12000, "fuel_level": 550, "fuel_capacity": 600, "capacity": 32000, "axles": 4},
        
        # --- Medium Duty / Distribution ---
        {"type": "Truck", "vin": "KDC-M01", "make": "Isuzu", "model": "FRR", "year": 2020, 
        "engine_hours": 4950, "odometer": 110000, "fuel_level": 150, "fuel_capacity": 200, "capacity": 10000, "axles": 2},
        {"type": "Truck", "vin": "KDC-M02", "make": "Mitsubishi", "model": "Fuso", "year": 2021, 
        "engine_hours": 3200, "odometer": 75000, "fuel_level": 80, "fuel_capacity": 180, "capacity": 8000, "axles": 2},
        {"type": "Truck", "vin": "KDC-M03", "make": "Hino", "model": "500", "year": 2018, 
        "engine_hours": 8500, "odometer": 300000, "fuel_level": 20, "fuel_capacity": 250, "capacity": 12000, "axles": 2, "status": "Maintenance"},

        # --- Passenger & Delivery Vans ---
        {"type": "Van", "vin": "KDC-V01", "make": "Toyota", "model": "Hiace", "year": 2023, 
        "passenger_capacity": 14, "engine_hours": 900, "odometer": 25000, "fuel_level": 45, "fuel_capacity": 70},
        {"type": "Van", "vin": "KDC-V02", "make": "Nissan", "model": "NV350", "year": 2022, 
        "passenger_capacity": 14, "engine_hours": 1500, "odometer": 55000, "fuel_level": 30, "fuel_capacity": 65},
        {"type": "Van", "vin": "KDC-V03", "make": "Volkswagen", "model": "Crafter", "year": 2021, 
        "passenger_capacity": 19, "engine_hours": 2800, "odometer": 95000, "fuel_level": 60, "fuel_capacity": 75},
        {"type": "Van", "vin": "KDC-V04", "make": "Ford", "model": "Transit", "year": 2024, 
        "passenger_capacity": 12, "engine_hours": 150, "odometer": 5000, "fuel_level": 75, "fuel_capacity": 80},
    ]

    for data in professional_entries:
        # Check if VIN exists to avoid errors on re-run
        exists = session.query(VehicleDB).filter_by(vin=data['vin']).first()
        if not exists:
            v_type = data.pop('type')
            new_v = VehicleDB(v_type=v_type, **data)
            session.add(new_v)
    
    session.commit()
    print("Database seeded with professional fleet data.")


from sqlalchemy import func

def generate_fleet_dashboard():
    print(f"\n{'='*20} FLEET DASHBOARD {'='*20}")
    
    # 1. Total Fleet Count
    total = session.query(VehicleDB).count()
    
    # 2. Maintenance Alerts (Engine Hours > 5000)
    to_service = session.query(VehicleDB).filter(VehicleDB.engine_hours >= 5000).all()
    
    # 3. Fuel Crisis (Fuel Level < 15%)
    low_fuel = [v for v in session.query(VehicleDB).all() if v.fuel_percentage < 15]
    
    # 4. Total Tonnage Capacity (Sum of all truck capacities)
    # This is a pure SQL 'SUM' function
    total_tonnage = session.query(func.sum(VehicleDB.capacity)).scalar()

    print(f"Total Vehicles:    {total}")
    print(f"Service Required:  {len(to_service)} units")
    print(f"Refuel Urgent:    {len(low_fuel)} units")
    print(f"Total Fleet Cap:   {total_tonnage/1000:.1f} Tonnes")
    print("="*57)

# Run the report
# generate_fleet_dashboard()

# Run this once in your if __name__ == "__main__": block
if __name__ == "__main__":
    seed_professional_data()
    generate_fleet_dashboard()

