from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import database

class PatientCreate(BaseModel):
    nombre: str
    edad: int
    tratamiento: str
    proxima_cita: str = ""
    telefono: str = ""
    email: str = ""
    observaciones: str = ""


app = FastAPI(
    title="DentalAI API",
    description="API REST para DentalAI Manager",
    version="1.0.0",
)


@app.get("/")
def root():
    return {
        "message": "DentalAI API funcionando correctamente"
    }


@app.get("/patients")
def get_patients():
    rows = database.list_patients()
    return [dict(row) for row in rows]

@app.get("/patients/{patient_id}")
def get_patient(patient_id: int):
    rows = database.list_patients()

    for row in rows:
        if row["id"] == patient_id:
            return dict(row)


    raise HTTPException(
        status_code=404,
        detail="Paciente no encontrado"
    )    

@app.post("/patients", status_code=201)
def create_patient(patient: PatientCreate):
    patient_id = database.add_patient(
        patient.nombre,
        patient.edad,
        patient.tratamiento,
        patient.proxima_cita,
        patient.telefono,
        patient.email,
        patient.observaciones,
    )

    return {
        "message": "Paciente creado correctamente",
        "id": patient_id,
    }

@app.put("/patients/{patient_id}")
def update_patient(patient_id: int, patient: PatientCreate):
    database.update_patient(
        patient_id,
        patient.nombre,
        patient.edad,
        patient.tratamiento,
        patient.proxima_cita,
        patient.telefono,
        patient.email,
        patient.observaciones,
    )

    return {
        "message": "Paciente actualizado correctamente",
        "id": patient_id
    }

@app.delete("/patients/{patient_id}")
def delete_patient(patient_id: int):
    rows = database.list_patients()

    exists = any(
        row["id"] == patient_id
        for row in rows
    )

    if not exists:
        raise HTTPException(
            status_code=404,
            detail="Paciente no encontrado"
        )

    database.delete_patient(patient_id)

    return {
        "message": "Paciente eliminado correctamente",
        "id": patient_id
    }