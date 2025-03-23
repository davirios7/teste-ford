from sqlmodel import Session
from app.core.database import engine
from faker import Faker
import random
from app.models.locations import DimLocations, MarketEnum
from app.models.parts import DimParts
from app.models.purchases import DimPurchases, PurchaseTypeEnum
from app.models.supplier import DimSupplier
from app.models.user import User
from app.models.vehicle import DimVehicle, PropulsionType
from app.models.warranties import FactWarranties
from sqlalchemy import text

fake = Faker()


def create_locations(session, num=10):
    locations = [
        DimLocations(
            market=random.choice(list(MarketEnum)),
            country=fake.country(),
            province=fake.state(),
            city=fake.city(),
        )
        for _ in range(num)
    ]
    session.add_all(locations)
    session.commit()


def create_suppliers(session, num=10):
    location_ids = [
        row[0]
        for row in session.exec(text("SELECT location_id FROM dimlocations")).all()
    ]
    suppliers = [
        DimSupplier(
            supplier_name=fake.company(),
            location_id=random.choice(location_ids),
        )
        for _ in range(num)
    ]
    session.add_all(suppliers)
    session.commit()


def create_parts(session, num=20):
    supplier_ids = [
        row[0]
        for row in session.exec(text("SELECT supplier_id FROM dimsupplier")).all()
    ]
    parts = [
        DimParts(
            part_name=fake.word(),
            last_id_purchase=random.randint(1, 100),
            supplier_id=random.choice(supplier_ids),
        )
        for _ in range(num)
    ]
    session.add_all(parts)
    session.commit()


def create_purchases(session, num=20):
    part_ids = [
        row[0] for row in session.exec(text("SELECT part_id FROM dimparts")).all()
    ]
    purchases = [
        DimPurchases(
            purchase_type=random.choice(list(PurchaseTypeEnum)),
            purchase_date=fake.date_between(start_date="-5y", end_date="today"),
            part_id=random.choice(part_ids),
        )
        for _ in range(num)
    ]
    session.add_all(purchases)
    session.commit()


def create_users(session, num=10):
    users = [
        User(
            username=fake.user_name(),
            email=fake.email(),
            password=fake.password(),
        )
        for _ in range(num)
    ]
    session.add_all(users)
    session.commit()


def create_vehicles(session, num=15):
    vehicles = [
        DimVehicle(
            model=fake.word().capitalize(),
            prod_date=fake.date_between(start_date="-10y", end_date="today"),
            year=random.randint(2000, 2024),
            propulsion=random.choice(list(PropulsionType)),
        )
        for _ in range(num)
    ]
    session.add_all(vehicles)
    session.commit()


def create_warranties(session, num=30):
    vehicle_ids = [
        row[0] for row in session.exec(text("SELECT vehicle_id FROM dimvehicle")).all()
    ]
    part_ids = [
        row[0] for row in session.exec(text("SELECT part_id FROM dimparts")).all()
    ]
    location_ids = [
        row[0]
        for row in session.exec(text("SELECT location_id FROM dimlocations")).all()
    ]
    purchase_ids = [
        row[0]
        for row in session.exec(text("SELECT purchase_id FROM dimpurchases")).all()
    ]

    warranties = [
        FactWarranties(
            vehicle_id=random.choice(vehicle_ids),
            repair_date=fake.date_this_decade(),
            client_complaint=fake.sentence(),
            tech_comment=fake.sentence(),
            part_id=random.choice(part_ids),
            classified_issue=fake.word(),
            location_id=random.choice(location_ids),
            purchase_id=random.choice(purchase_ids),
        )
        for _ in range(num)
    ]
    session.add_all(warranties)
    session.commit()


def populate_database():
    with Session(engine) as session:
        create_locations(session)
        create_suppliers(session)
        create_parts(session)
        create_purchases(session)
        create_users(session)
        create_vehicles(session)
        create_warranties(session)
    print("Banco de dados populado com sucesso!")


if __name__ == "__main__":
    populate_database()
