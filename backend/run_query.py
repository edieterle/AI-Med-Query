from sqlalchemy import text
from db import engine

with engine.connect() as conn:
    result = conn.execute(text("""
        SELECT p.patient_id, AVG(r.heart_rate) AS avg_hr
        FROM patients p
        JOIN devices d ON p.patient_id = d.patient_id
        JOIN readings r ON d.device_id = r.device_id
        GROUP BY p.patient_id                           
    """))

for row in result:
    print(row.patient_id, row.avg_hr)
