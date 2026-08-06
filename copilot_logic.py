from dataclasses import dataclass


@dataclass(frozen=True)
class AnalysisResult:
    valoracion: str
    prioridad: str
    pruebas: str
    alarmas: str
    informacion_faltante: str


def analyze_case(
    symptoms: str,
    duration: str,
    pain: int | None,
    background: str,
    fever: bool,
    swelling: bool,
) -> AnalysisResult:
    text = symptoms.lower().strip()
    priority = 'Baja'
    assessment = 'No se ha identificado una situación concreta con los datos aportados.'
    tests = 'Exploración clínica general.'
    alarms = 'No se han detectado señales de alarma.'

    if fever and swelling:
        priority = 'Urgente'
        assessment = 'Posible proceso infeccioso odontógeno.'
        tests = 'Exploración clínica prioritaria y radiografía diagnóstica.'
        alarms = 'Fiebre e inflamación. Valorar atención urgente si existe inflamación facial o dificultad para tragar.'
    elif swelling and pain is not None and pain >= 7:
        priority = 'Alta'
        assessment = 'Dolor intenso acompañado de inflamación. Requiere valoración prioritaria.'
        tests = 'Exploración clínica y radiografía diagnóstica.'
        alarms = 'Dolor intenso e inflamación.'
    elif 'dolor' in text and pain is not None and pain >= 7:
        priority = 'Alta'
        assessment = 'Dolor dental intenso que requiere valoración prioritaria.'
        tests = 'Exploración clínica y radiografía diagnóstica.'
        alarms = 'Dolor intenso.'
    elif 'caries profunda' in text:
        priority = 'Alta'
        assessment = 'Posible lesión de caries profunda.'
        tests = 'Exploración clínica, radiografía periapical y valoración pulpar.'
    elif 'sangrado' in text:
        priority = 'Media'
        assessment = 'Posibles signos de inflamación gingival o periodontal.'
        tests = 'Valoración periodontal y revisión de higiene oral.'
    elif 'sensibilidad' in text:
        priority = 'Media'
        assessment = 'Posible hipersensibilidad dental.'
        tests = 'Exploración clínica y valoración de desgaste, retracción o caries.'
    elif 'caries' in text:
        priority = 'Media'
        assessment = 'Posible lesión de caries.'
        tests = 'Exploración clínica y radiografía si procede.'
    elif 'sarro' in text or 'placa' in text:
        priority = 'Baja'
        assessment = 'Posible acumulación de placa o cálculo dental.'
        tests = 'Valoración periodontal e higiene profesional.'

    missing: list[str] = []
    if not duration.strip():
        missing.append('duración de los síntomas')
    if pain is None:
        missing.append('intensidad del dolor')
    if not background.strip():
        missing.append('antecedentes relevantes')

    missing_text = ', '.join(missing).capitalize() if missing else 'Ninguna.'
    return AnalysisResult(assessment, priority, tests, alarms, missing_text)
