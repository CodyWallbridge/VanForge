from sqlmodel import Session, select

from .database import engine
from .models import Profession

PROFESSIONS = [
    "Alchemy",
    "Blacksmithing",
    "Enchanting",
    "Engineering",
    "Inscription",
    "Jewelcrafting",
    "Leatherworking",
    "Tailoring",
]

def seed_professions():
    print("Seeding professions...")  
    with Session(engine) as session:

        for name in PROFESSIONS:
            statement = select(Profession).where(Profession.name == name)
            existing = session.exec(statement).first()

            if not existing:
                session.add(Profession(name=name))

        session.commit()
    print("Seeding complete")