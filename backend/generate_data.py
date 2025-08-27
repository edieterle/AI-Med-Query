from db import SessionLocal, init_db, Patient, Device, Reading, Outcome, DATABASE_URL
from faker import Faker
from datetime import timedelta
import random
import pandas as pd
from sqlalchemy import create_engine

fake = Faker()

# Generate synthetic, realistic, and correlated data
# Patients: age, sex, and BMI affect a risk score
# Devices: 1-3 per patient; device type affects outcome probabilities
# Readings: 30-day readings correlated with risk score
# Outcomes: complications, replacemnts, and readmissions depend on risk score and device type
# Trends: heart rate increases slighlty over time for high-risk patients; battery decreases gradually

# 1. Initialize database
init_db()
db = SessionLocal()

# 2. Helper functions

def generate_patient():
    age = random.randint(20, 90)
    sex = random.choices(["Male", "Female"], weights=[0.48, 0.52])[0]
    height = round(random.uniform(150, 200), 2)
    weight = round(random.uniform(50, 120), 2)
    diagnosis_code = f"D{random.randint(100, 999)}"

    # Risk score for complications
    risk_score = 0
    if age > 65:
        risk_score += 1.5
    if sex == "Male":
        risk_score += 0.5
    bmi = weight / ((height/100)**2)
    if bmi > 30:
        risk_score += 1

    return {
        "age": age,
        "sex": sex,
        "weight": weight,
        "height": height,
        "diagnosis_code": diagnosis_code,
        "risk_score": risk_score
    }

def generate_reading(risk_score):
    heart_rate = random.randint(60, 80) + int(risk_score * 5)
    heart_rate = min(heart_rate, 130)
    systolic = random.randint(110, 120) + int(risk_score * 5)
    diastolic = random.randint(70, 80) + int(risk_score * 3)
    systolic = min(systolic, 180)
    diastolic = min(diastolic, 120)
    blood_pressure = f"{systolic}/{diastolic}"
    battery_level = random.randint(50, 100)
    return {
        "heart_rate": heart_rate,
        "blood_pressure": blood_pressure,
        "battery_level": battery_level
    }

def generate_reading_over_time(risk_score, day):
    reading = generate_reading(risk_score)
    reading["heart_rate"] += int(day * 0.2 * risk_score)   # gradual trend
    reading["battery_level"] = max(reading["battery_level"] - day, 0)
    return reading

def generate_outcome(device_type, risk_score):
    base_prob = 0.02
    if device_type == "Pacemaker":
        base_prob += 0.05
    elif device_type == "Defibrillator":
        base_prob += 0.03

    prob_complication = base_prob + 0.1 * risk_score

    complication_occurred = random.random() < prob_complication
    device_replacement_needed = complication_occurred and random.random() < 0.6
    readmission_within_30_days = complication_occurred and random.random() < 0.4
    time_to_failure = random.randint(30, 1000) if complication_occurred else random.randint(1000, 2000)

    return {
        "complication_occurred": complication_occurred,
        "device_replacement_needed": device_replacement_needed,
        "readmission_within_30_days": readmission_within_30_days,
        "time_to_failure": time_to_failure
    }

# 3. Populate database
device_types = ["Pacemaker", "Defibrillator", "Neurostimulator"]
manufacturers = ["Medtronic", "Boston Scientific", "Abbott"]

patients = []
for _ in range(20):  # 20 patients
    p_data = generate_patient()
    patient = Patient(
        age=p_data["age"],
        sex=p_data["sex"],
        weight=p_data["weight"],
        height=p_data["height"],
        diagnosis_code=p_data["diagnosis_code"]
    )
    db.add(patient)
    db.commit()
    db.refresh(patient)
    p_data["db_obj"] = patient
    patients.append(p_data)

    for _ in range(random.randint(1, 3)):  # 1-3 devices per patient
        device_type = random.choice(device_types)
        implant_date = fake.date_between(start_date='-5y', end_date='today')
        device = Device(
            patient_id=patient.patient_id,
            device_type=device_type,
            implant_date=implant_date,
            manufacturer=random.choice(manufacturers)
        )
        db.add(device)
        db.commit()
        db.refresh(device)

        # 30 days of readings per device
        for day in range(30):
            timestamp = implant_date + timedelta(days=day)
            r_data = generate_reading_over_time(p_data["risk_score"], day)
            reading = Reading(
                device_id=device.device_id,
                timestamp=timestamp,
                heart_rate=r_data["heart_rate"],
                blood_pressure=r_data["blood_pressure"],
                battery_level=r_data["battery_level"]
            )
            db.add(reading)

        # Generate outcome
        o_data = generate_outcome(device_type, p_data["risk_score"])
        outcome = Outcome(
            device_id=device.device_id,
            complication_occurred=o_data["complication_occurred"],
            device_replacement_needed=o_data["device_replacement_needed"],
            readmission_within_30_days=o_data["readmission_within_30_days"],
            time_to_failure=o_data["time_to_failure"]
        )
        db.add(outcome)

db.commit()
db.close()
print("Populated database")

# Export data to Excel

# Create SQLAlchemy engine
engine = create_engine(DATABASE_URL)

def export_to_excel(output_file="exported_data.xlsx"):
    tables = ["patients", "devices", "readings", "outcomes"]
    with pd.ExcelWriter(output_file, engine="openpyxl") as writer:
        for table in tables:
            # Read SQL table into DataFrame
            df = pd.read_sql_table(table, con=engine)
            # Write each DataFrame to a separate sheet
            df.to_excel(writer, sheet_name=table, index=False)
    print(f"Data exported to {output_file}")

export_to_excel()
