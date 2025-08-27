from sqlalchemy import create_engine, Column, Integer, String, DECIMAL, Date, ForeignKey, TIMESTAMP, Boolean
from sqlalchemy.orm import sessionmaker, declarative_base, relationship

DATABASE_URL = "postgresql+psycopg2://postgres:1774@localhost:5432/postgres"
# Open connection to PostgreSQL database
engine = create_engine(DATABASE_URL, echo=True)
# Generate session to interact with the database
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Parent class for tables
Base = declarative_base()

# Patient table
class Patient(Base):
    __tablename__ = "patients"
    patient_id = Column(Integer, primary_key=True, index=True)
    age = Column(Integer)
    sex = Column(String(10))
    weight = Column(DECIMAL(5, 2))
    height = Column(DECIMAL(5, 2))
    diagnosis_code = Column(String(10))
    devices = relationship("Device", back_populates="patient")

# Device table
class Device(Base):
    __tablename__ = "devices"
    device_id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(Integer, ForeignKey("patients.patient_id"))
    device_type = Column(String(50))
    implant_date = Column(Date)
    manufacturer = Column(String(50))
    patient = relationship("Patient", back_populates="devices")
    readings = relationship("Reading", back_populates="device")
    outcomes = relationship("Outcome", back_populates="device")

# Reading table
class Reading(Base):
    __tablename__ = "readings"
    reading_id = Column(Integer, primary_key=True, index=True)
    device_id = Column(Integer, ForeignKey("devices.device_id"))
    timestamp = Column(TIMESTAMP)
    heart_rate = Column(Integer)
    blood_pressure = Column(String(7))
    battery_level = Column(Integer)
    device = relationship("Device", back_populates="readings")

# Outcome table
class Outcome(Base):
    __tablename__ = "outcomes"
    outcome_id = Column(Integer, primary_key=True, index=True)
    device_id = Column(Integer, ForeignKey("devices.device_id"))
    complication_occurred = Column(Boolean)
    device_replacement_needed = Column(Boolean)
    time_to_failure = Column(Integer)
    readmission_within_30_days = Column(Boolean)
    device = relationship("Device", back_populates="outcomes")

# Initialize database
def init_db():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    print("Database tables created")

# Drop database
def drop_db():
    Base.metadata.drop_all(bind=engine)
