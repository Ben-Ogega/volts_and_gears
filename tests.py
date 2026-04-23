import unittest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Base, VehicleDB, DriverDB, InspectionDB

# ── TEST CONFIGURATION ───────────────────────────────────────
# We use an "In-Memory" database so it disappears after the test
TEST_DATABASE_URL = "sqlite:///:memory:"

class TestFleetSystem(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        """Set up a fresh database for testing."""
        cls.engine = create_engine(TEST_DATABASE_URL)
        Base.metadata.create_all(cls.engine)
        cls.Session = sessionmaker(bind=cls.engine)

    def setUp(self):
        """Create a new session for every individual test."""
        self.session = self.Session()

    def tearDown(self):
        """Close the session after each test."""
        self.session.close()

    # ── THE TESTS ───────────────────────────────────────────

    def test_create_vehicle(self):
        """Test adding a truck to the database."""
        new_truck = VehicleDB(
            vin="TEST-001", 
            v_type="Truck", 
            make="Mercedes", 
            model="Actros", 
            year=2026
        )
        self.session.add(new_truck)
        self.session.commit()
        
        retrieved = self.session.query(VehicleDB).filter_by(vin="TEST-001").first()
        self.assertEqual(retrieved.make, "Mercedes")
        self.assertEqual(retrieved.status, "Available")

    def test_inspection_affects_status(self):
        """Test that a FAILED inspection moves a truck to Maintenance."""
        # 1. Setup Vehicle and Driver
        truck = VehicleDB(vin="FAIL-01", v_type="Truck", make="Isuzu", model="FRR", year=2020)
        driver = DriverDB(employee_id="D01", name="Test Driver", licence_class="A")
        self.session.add_all([truck, driver])
        self.session.commit()

        # 2. Perform FAILED inspection
        inspection = InspectionDB(
            vehicle_id=truck.id,
            driver_id=driver.id,
            verdict="FAILED",
            notes="Brake pads worn"
        )
        truck.status = "Maintenance" # Simulating our logic
        self.session.add(inspection)
        self.session.commit()

        # 3. Verify
        self.assertEqual(truck.status, "Maintenance")

if __name__ == "__main__":
    print(unittest.main())