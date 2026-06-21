#_*_ coding: utf-8 _*_
import json
import csv
from datetime import datetime

class Vehicle:
    def __init__(self, **kwargs):
        # We extract values from kwargs. If a key is missing, we provide a default.
        self.vin = kwargs.get('vin', "N/A")
        self.make = kwargs.get('make', "Generic")
        self.model = kwargs.get('model', "Generic")
        self.year = kwargs.get('year', datetime.now().year)
        self.engine = kwargs.get('engine', "N/A")
        self.engine_hours = kwargs.get('engine_hours', 0)
        self.odometer = kwargs.get('odometer', 0)
        self.fuel_level = kwargs.get('fuel_level', 0)
        self.fuel_capacity = kwargs.get('fuel_capacity', 1)
        self.status = kwargs.get('status', "Available")
        
        # Inspection Data
        self.tyre_condition = kwargs.get('tyre_condition', "Good")
        self.lights_status = kwargs.get('lights_status', "Working")
        self.coolant_level = kwargs.get('coolant_level', "Full")

    @property
    def fuel_percentage(self):
        return round((self.fuel_level / self.fuel_capacity) * 100, 2)

    def to_dict(self):
        data = self.__dict__.copy()
        data['type'] = self.__class__.__name__
        return data

class Truck(Vehicle):
    def __init__(self, **kwargs):
        # 1. Initialize parent first
        super().__init__(**kwargs)
        # 2. Add Truck-specific attributes
        self.capacity = kwargs.get('capacity', 0)
        self.axles = kwargs.get('axles', 2)
        self.is_loaded = kwargs.get('is_loaded', False)

class Van(Vehicle):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.passenger_capacity = kwargs.get('passenger_capacity', 14)

class Fleet:
    def __init__(self, fleet_name):
        self.fleet_name = fleet_name
        self.vehicles = []

    def load_from_json(self, filename="fleet_data.json"):
        try:
            with open(filename, 'r', encoding='utf-8-sig') as f:
                data = json.load(f)
                self.vehicles = []
                for item in data:
                    v_type = item.get('type') # Use .get to avoid KeyError
                    if v_type == 'Truck':
                        self.vehicles.append(Truck(**item))
                    elif v_type == 'Van':
                        self.vehicles.append(Van(**item))
            return f"Loaded {len(self.vehicles)} vehicles."
        except (FileNotFoundError, json.JSONDecodeError):
            return "No valid data file found."

    def save_to_json(self, filename="fleet_data.json"):
        data = [v.to_dict() for v in self.vehicles]
        with open(filename, 'w', encoding='utf-8-sig') as f:
            json.dump(data, f, indent=4)
        return f"Saved to {filename}"

    # ── NEW: THE CSV EXPORTER ───────────────────────────────
    def export_to_csv(self, filename="fleet_report.csv"):
        if not self.vehicles: return "Nothing to export."
        
        # Extract headers from the first vehicle's dictionary
        headers = self.vehicles[0].to_dict().keys()
        
        with open(filename, 'w', newline='', encoding='utf-8-sig') as f:
            writer = csv.DictWriter(f, fieldnames=headers)
            writer.writeheader()
            for v in self.vehicles:
                writer.writerow(v.to_dict())
        return f"CSV Report generated: {filename}"
    

    

# ── TEST RUN ────────────────────────────────────────────────
if __name__ == "__main__":
    nairobi_hub = Fleet("Nairobi Hub")
    print(nairobi_hub.load_from_json())

    # Example: If file was empty, add a truck with the new kwargs style
    if not nairobi_hub.vehicles:
        nairobi_hub.vehicles.append(Truck(
            vin="KBZ001", make="Mercedes", model="Actros", 
            fuel_level=100, fuel_capacity=400, capacity=30000
        ))
    
    print(nairobi_hub.save_to_json())
    print(nairobi_hub.export_to_csv())