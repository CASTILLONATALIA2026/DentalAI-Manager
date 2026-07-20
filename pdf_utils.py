from pathlib import Path
from typing import Iterable

from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas


def _write_wrapped(pdf: canvas.Canvas, text: str, x: float, y: float, max_chars: int = 90, leading: int = 14) -> float:
    words = str(text).split()
    line = ''
    for word in words:
        candidate = f'{line} {word}'.strip()
        if len(candidate) > max_chars:
            pdf.drawString(x, y, line)
            y -= leading
            line = word
        else:
            line = candidate
    pdf.drawString(x, y, line)
    return y - leading


def create_patient_report(path: str, patient: dict[str, object], date_text: str) -> None:
    pdf = canvas.Canvas(path, pagesize=A4)
    width, height = A4
    margin = 60
    y = height - 60
    pdf.setTitle(f"Informe clínico - {patient['nombre']}")
    pdf.setFont('Helvetica-Bold', 18)
    pdf.drawString(margin, y, 'DENTALAI MANAGER')
    y -= 25
    pdf.setFont('Helvetica-Bold', 13)
    pdf.drawString(margin, y, 'INFORME CLÍNICO')
    y -= 12
    pdf.line(margin, y, width - margin, y)
    y -= 25
    pdf.setFont('Helvetica', 10)
    pdf.drawString(margin, y, f'Fecha: {date_text}')

    sections = [
        ('DATOS DEL PACIENTE', f"Paciente: {patient['nombre']}\nEdad: {patient['edad']} años\nPróxima cita: {patient.get('proxima_cita') or 'No indicada'}"),
        ('TRATAMIENTO', str(patient['tratamiento'])),
        ('OBSERVACIONES', 'Paciente en seguimiento clínico.'),
        ('RECOMENDACIÓN', 'Continuar revisiones periódicas.'),
    ]
    for title, content in sections:
        y -= 32
        pdf.setFont('Helvetica-Bold', 11)
        pdf.drawString(margin, y, title)
        y -= 20
        pdf.setFont('Helvetica', 11)
        for line in content.splitlines():
            y = _write_wrapped(pdf, line, margin, y)

    pdf.setFont('Helvetica-Oblique', 9)
    pdf.drawCentredString(width / 2, 40, 'Documento generado por DentalAI Manager')
    pdf.save()


def create_analysis_report(path: str, analysis_id: int, fields: Iterable[tuple[str, object]]) -> None:
    pdf = canvas.Canvas(path, pagesize=A4)
    width, height = A4
    margin = 55
    y = height - 55
    pdf.setTitle(f'Análisis IA #{analysis_id}')
    pdf.setFont('Helvetica-Bold', 17)
    pdf.drawString(margin, y, 'DENTALAI MANAGER')
    y -= 24
    pdf.setFont('Helvetica-Bold', 13)
    pdf.drawString(margin, y, f'ANÁLISIS IA #{analysis_id}')
    y -= 14
    pdf.line(margin, y, width - margin, y)
    y -= 25

    for label, value in fields:
        if y < 90:
            pdf.showPage()
            y = height - 55
        pdf.setFont('Helvetica-Bold', 10)
        pdf.drawString(margin, y, f'{label}:')
        y -= 15
        pdf.setFont('Helvetica', 10)
        y = _write_wrapped(pdf, str(value), margin + 10, y)
        y -= 6

    pdf.setFont('Helvetica-Oblique', 8)
    pdf.drawCentredString(width / 2, 35, 'Resultado orientativo sujeto a validación profesional')
    pdf.save()
