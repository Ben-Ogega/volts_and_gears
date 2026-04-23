# ============================================================
# VOLTS AND GEARS — Fleet Management System
# Learning OOP — April 2026
# ============================================================

from datetime import datetime

# ── CONSTANTS ────────────────────────────────────────────────
MAX_DRIVING_HOURS = 8        # Kenya Traffic Act limit
OIL_SERVICE_THRESHOLD = 5000  # engine hours before service


# ── VEHICLE (BASE CLASS) ─────────────────────────────────────
class Vehicle:
    def __init__(self, vin, make, model, year, engine, engine_hours,
                 odometer, fuel_level, status="Available",
                 tyre_condition="Good", lights_status="Working",
                 coolant_level="Full"):
        self.vin = vin
        self.make = make
        self.model = model
        self.year = year
        self.engine = engine
        self.engine_hours = engine_hours
        self.odometer = odometer
        self.fuel_level = fuel_level
        self.status = status
        self.tyre_condition = tyre_condition
        self.lights_status = lights_status
        self.coolant_level = coolant_level

    @property
    def age(self):
        return 2026 - self.year
    
    @property
    def is_service_due(self):
        return self.engine_hours >= OIL_SERVICE_THRESHOLD
    
    @property
    def fuel_percentage(self):
        if hasattr(self, 'fuel_capacity') and self.fuel_capacity > 0:
            return round((self.fuel_level / self.fuel_capacity) * 100, 2)
        return None
    
    @staticmethod
    def validate_vin(vin):
        # Simple VIN validation (replace with actual validation logic)
        return len(vin) >= 5 and vin.isalnum()
    
    @classmethod 
  
    def from_dict(cls, data):
        """
        In simple terms what this does is allow us to create a Vehicle instance from
        a dictionary of attributes.
        For example, if we have a dictionary like this:
        {
            "vin": "1HGBH41JXMN109186",
            "make": "Toyota",
            "model": " Hilux",
            "year": 2020,
            "engine": "2.8L 4-cylinder",
            "engine_hours": 5000,
            "odometer": 10000,
            "fuel_level": 50,
            "status": "Available"
        }
        """
        return cls(
            vin=data.get('vin'),
            make=data.get('make'),
            model=data.get('model'),
            year=data.get('year'),
            engine=data.get('engine'),
            engine_hours=data.get('engine_hours', 0),
            odometer=data.get('odometer', 0),
            fuel_level=data.get('fuel_level', 0),
            status=data.get('status', "Available"),
            tyre_condition=data.get('tyre_condition', "Good"),
            lights_status=data.get('lights_status', "Working"),
            coolant_level=data.get('coolant_level', "Full")
        )

    def update_mileage(self, new_mileage):
        if new_mileage > self.odometer:
            self.odometer = new_mileage
            return f"New mileage: {self.odometer} km"
        else:
            print("Error: new mileage cannot be less than current odometer")

    def get_status(self):
        return self.status

    def update_status(self, status):
        statuses = ["Available", "InTransit", "Maintenance", "Scrapped"]
        if status in statuses:
            self.status = status
            return f"Vehicle status updated: {self.status}"
        else:
            print("Error: Invalid status")


# ── TRUCK ────────────────────────────────────────────────────
class Truck(Vehicle):
    def __init__(self, vin, make, model, year, engine, engine_hours,
                 odometer, fuel_level, capacity, fuel_capacity, axles,
                 is_loaded, status="Available", tyre_condition="Good",
                 lights_status="Working", coolant_level="Full"):
        super().__init__(vin, make, model, year, engine, engine_hours,
                         odometer, fuel_level, status,
                         tyre_condition, lights_status, coolant_level)
        self.capacity = capacity
        self.axles = axles
        self.is_loaded = is_loaded
        self.fuel_capacity = fuel_capacity

    def check_current_weight(self):
        if self.is_loaded:
            return self.capacity
        else:
            return 0

    def estimate_fuel_burn(self, load, terrain, engine_capacity):
        terrain_bases = {
            "tarmac": 1.0,
            "murram": 1.5,
            "offroad": 1.67
        }
        if terrain not in terrain_bases:
            print("Error: Invalid terrain. Choose tarmac, murram or offroad")
            return None

        base_rate = 30
        load_factor = load / self.capacity
        terrain_multiplier = terrain_bases[terrain]
        engine_factor = engine_capacity / 10000

        fuel_burn = base_rate * terrain_multiplier * load_factor * engine_factor
        return round(fuel_burn, 2)


# ── VAN ──────────────────────────────────────────────────────
class Van(Vehicle):
    def __init__(self, vin, make, model, year, engine, engine_hours,
                 odometer, fuel_level, passenger_capacity, fuel_capacity,
                 status="Available", tyre_condition="Good",
                 lights_status="Working", coolant_level="Full"):
        super().__init__(vin, make, model, year, engine, engine_hours,
                         odometer, fuel_level, status,
                         tyre_condition, lights_status, coolant_level)
        self.passenger_capacity = passenger_capacity
        self.fuel_capacity = fuel_capacity


# ── DRIVER ───────────────────────────────────────────────────
class Driver:
    def __init__(self, name, employee_id, licence_class,
                 status="Off Duty", current_vehicle=None,
                 driving_hours=0, total_kilometres=0):
        self.name = name
        self.employee_id = employee_id
        self.licence_class = licence_class
        self.status = status
        self.current_vehicle = current_vehicle
        self.driving_hours = driving_hours
        self.total_kilometres = total_kilometres

    def clock_in(self):
        self.status = "On Duty"
        return self.status

    def clock_out(self):
        self.status = "Off Duty"
        self.driving_hours = 0
        return self.status

    def assign_vehicle(self, vehicle):
        if self.status == "On Duty":
            self.current_vehicle = vehicle
            return f"Vehicle {vehicle.vin} assigned to {self.name}"
        else:
            return f"Error: {self.name} is Off Duty. Cannot assign vehicle."

    def log_trip(self, distance):
        if self.current_vehicle is None:
            return "Error: No vehicle assigned"
        self.current_vehicle.odometer += distance
        self.total_kilometres += distance
        return f"Trip logged: {distance} km. Total: {self.total_kilometres} km"


# ── PRE TRIP INSPECTION ───────────────────────────────────────
class PreTripInspection:
    def __init__(self, inspection_id, vehicle, driver, notes=""):
        self.inspection_id = inspection_id
        self.vehicle = vehicle
        self.driver = driver
        self.date = datetime.now()
        self.notes = notes
        self.results = {}

    def check_fuel(self):
        limit = 0.25 * self.vehicle.fuel_capacity
        passed = self.vehicle.fuel_level > limit
        self.results['Fuel Level'] = "Passed" if passed else "Failed"
        return passed

    def check_engine_hours(self):
        passed = self.vehicle.engine_hours < OIL_SERVICE_THRESHOLD
        self.results['Engine Hours'] = "Passed" if passed else "Warning — Service Due"
        return passed

    def check_tyres(self):
        passed = self.vehicle.tyre_condition == "Good"
        self.results['Tyres'] = "Passed" if passed else "Failed"
        return passed

    def check_lights(self):
        passed = self.vehicle.lights_status == "Working"
        self.results['Lights'] = "Passed" if passed else "Failed"
        return passed

    def check_coolant(self):
        passed = self.vehicle.coolant_level == "Full"
        self.results['Coolant'] = "Passed" if passed else "Failed"
        return passed

    def is_roadworthy(self):
        checks = [
            self.check_fuel(),
            self.check_tyres(),
            self.check_lights(),
            self.check_coolant(),
        ]
        roadworthy = all(checks)
        if not roadworthy:
            self.vehicle.update_status("Maintenance")
        return roadworthy

    def generate_summary(self):
        roadworthy = self.is_roadworthy()
        status = "PASSED" if roadworthy else "FAILED"
        summary = f"\n--- Inspection {self.inspection_id} ---\n"
        summary += f"Date:     {self.date.strftime('%Y-%m-%d %H:%M')}\n"
        summary += f"Vehicle:  {self.vehicle.make} {self.vehicle.model} ({self.vehicle.vin})\n"
        summary += f"Driver:   {self.driver.name}\n"
        summary += f"Verdict:  {status}\n"
        summary += f"{'─' * 30}\n"
        for check, result in self.results.items():
            summary += f"  {check:<20} {result}\n"
        if self.notes:
            summary += f"\nNotes: {self.notes}\n"
        return summary




# Create a fleet management system with classes for Vehicle, Truck, Van, Driver, and PreTripInspection. 
# Include methods for updating mileage, checking fuel levels, assigning vehicles to drivers, 
# and generating inspection summaries.

class DispatchError(Exception):
    pass

class NoDriverAvailable(DispatchError):
    pass

class NoVehicleAvailable(DispatchError):
    pass

class Fleet:
    def __init__(self, fleet_name):
        self.fleet_name = fleet_name
        self.vehicle_list = []
        self.driver_roster = []
        self.active_assignments = {}

    def add_vehicle(self, vehicle):
        self.vehicle_list.append(vehicle)
        return f"Vehicle {vehicle.vin} added to fleet."
    
    def remove_vehicle(self, vin):
        for vehicle in self.vehicle_list:
            if vehicle.vin == vin:
                self.vehicle_list.remove(vehicle)
                return f"Vehicle {vin} removed from fleet."
        return f"Vehicle {vin} not found."
    
    def hire_driver(self, driver):
        self.driver_roster.append(driver)
        return f"Driver {driver.name} hired."
    
    def fire_driver(self, employee_id):
        for driver in self.driver_roster:
            if driver.employee_id == employee_id:
                self.driver_roster.remove(driver)
                return f"Driver {driver.name} fired."
        return f"Driver with ID {employee_id} not found."


    def dispatch(self, vin, employee_id):
        vehicle = next((v for v in self.vehicle_list if v.vin == vin), None)
        driver = next((d for d in self.driver_roster if d.employee_id == employee_id), None)

        if not vehicle:
            raise NoVehicleAvailable(f"Vehicle {vin} not found.")
        if not driver:
            raise NoDriverAvailable(f"Driver with ID {employee_id} not found.")
        if driver.status != "On Duty":
            raise DispatchError(f"Driver {driver.name} is not On Duty.")
        if vehicle.status != "Available":
            raise DispatchError(f"Vehicle {vin} is not Available.")

        driver.assign_vehicle(vehicle)
        vehicle.update_status("InTransit")
        self.active_assignments[employee_id] = vin
        return f"Driver {driver.name} dispatched with vehicle {vin}."
    
    def generate_report(self):
        report = f"\n--- Fleet Report: {self.fleet_name} ---\n"
        report += f"Total Vehicles: {len(self.vehicle_list)}\n"
        report += f"Total Drivers: {len(self.driver_roster)}\n"
        report += f"Active Assignments: {len(self.active_assignments)}\n"
        report += f"{'-' * 40}\n"
        for vehicle in self.vehicle_list:
            report += f"{vehicle.vin}: {vehicle.make} {vehicle.model} - Status: {vehicle.status}\n"
        return report
    
    def maintenance_alert(self):
        alerts = []
        for vehicle in self.vehicle_list:
            if vehicle.engine_hours >= OIL_SERVICE_THRESHOLD:
                alerts.append(f"{vehicle.vin} — Service due: {vehicle.engine_hours} engine hours")
            if vehicle.status == "Maintenance":
                alerts.append(f"{vehicle.vin} — Currently in Maintenance")
        return alerts


    def __str__(self):
        return f"Fleet: {self.fleet_name} | Vehicles: {len(self.vehicle_list)} | Drivers: {len(self.driver_roster)}"

    def __len__(self):
        return len(self.vehicle_list)

    def __repr__(self):
        return f"Fleet(name='{self.fleet_name}', vehicles={len(self.vehicle_list)}, drivers={len(self.driver_roster)})"


# ============================================================
# TEST INSTANCES
# ============================================================

truck_001 = Truck(
    vin="KBZ001",
    make="Mercedes",
    model="Actros",
    year=2020,
    engine="OM471",
    engine_hours=4500,
    odometer=120000,
    fuel_level=150,
    capacity=30000,
    fuel_capacity=400,
    axles=3,
    is_loaded=True,
)

van_001 = Van(
    vin="KBC001",
    make="Toyota",
    model="Hiace",
    year=2021,
    engine="2TR-FE",
    engine_hours=1200,
    odometer=45000,
    fuel_level=40,
    passenger_capacity=14,
    fuel_capacity=70,
)

driver_001 = Driver(
    name="James Kamau",
    employee_id="EMP001",
    licence_class="Class A",
)

# ── TESTS ────────────────────────────────────────────────────
driver_001.clock_in()
driver_001.assign_vehicle(truck_001)

inspection = PreTripInspection(
    inspection_id="INSP001",
    vehicle=truck_001,
    driver=driver_001,
    notes="Northern Corridor run — Nairobi to Mombasa"
)


# ── FLEET TESTS ──────────────────────────────────────────────

# 1. Create fleet
nairobi_fleet = Fleet("Nairobi Northern Corridor Hub")

# 2. Add vehicles and drivers
nairobi_fleet.add_vehicle(truck_001)
nairobi_fleet.add_vehicle(van_001)
nairobi_fleet.hire_driver(driver_001)

# 3. Test __str__ and __len__
print(nairobi_fleet)
print(f"Fleet size: {len(nairobi_fleet)}")

# 4. Test dispatch
driver_001.clock_in()
print(nairobi_fleet.dispatch("KBZ001", "EMP001"))

# 5. Test generate_report
print(nairobi_fleet.generate_report())

# 6. Test maintenance_alert
print(nairobi_fleet.maintenance_alert())

# 7. Test dispatch error handling
try:
    nairobi_fleet.dispatch("KBZ001", "EMP001")
except DispatchError as e:
    print(f"Dispatch failed: {e}")


# Test staticmethod
print(Vehicle.validate_vin("KBZ001"))  # True
print(Vehicle.validate_vin("KB"))      # False

# Test classmethod
data = {
    'vin': 'KBZ999',
    'make': 'Volvo',
    'model': 'FH16',
    'year': 2019,
    'engine': 'D16G',
    'engine_hours': 3200,
    'odometer': 98000,
    'fuel_level': 200,
}
volvo = Vehicle.from_dict(data)
print("==Vehicle Make === Model === Age ==")
print(f"{volvo.make}, {volvo.model}, {volvo.age}")
print()
print(Vehicle.validate_vin("KBZ001"))  # True
print(Vehicle.validate_vin("KB"))      # False
print(Vehicle.validate_vin("KBZ 001")) # False — space in VIN
# print(f"Truck Age: {truck_001.age} years old")
# print(f"Is Service Due: {truck_001.is_service_due} hours")
# print(f"Fuel Percentage: {truck_001.fuel_percentage}%")

# print(f"Van Age: {van_001.age} years old")
# print(f"Is Service Due: {van_001.is_service_due} hours")
# print(f"Fuel Percentage: {van_001.fuel_percentage}%")
# print()

# print(inspection.generate_summary())
# print(truck_001.estimate_fuel_burn(25000, "murram", 12000))
# print(driver_001.log_trip(480))