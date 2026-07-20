import json
from datetime import datetime
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

from openpyxl import Workbook

import database
from copilot_logic import AnalysisResult, analyze_case
from pdf_utils import create_analysis_report, create_patient_report


class DentalAIApp:
    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.root.title('DentalAI Manager')
        self.root.geometry('1200x850')
        try:
            self.root.state('zoomed')
        except tk.TclError:
            pass

        database.init_db()
        self._build_menu()
        self._build_main_ui()
        self.load_patients()

    def _build_menu(self) -> None:
        menu_bar = tk.Menu(self.root)
        self.root.config(menu=menu_bar)
        file_menu = tk.Menu(menu_bar, tearoff=0)
        menu_bar.add_cascade(label='Archivo', menu=file_menu)
        file_menu.add_command(label='Salir', command=self.root.destroy)

    def _build_main_ui(self) -> None:
        tk.Label(self.root, text='DentalAI Manager', font=('Segoe UI', 20, 'bold')).pack(pady=5)
        tk.Label(self.root, text='Gestión clínica + IA dental', font=('Segoe UI', 11)).pack()
        self.counter_label = tk.Label(self.root, text='Pacientes registrados: 0', font=('Segoe UI', 10, 'bold'))
        self.counter_label.pack(pady=5)

        tk.Label(self.root, text='Buscar paciente').pack()
        self.search_entry = tk.Entry(self.root, width=40)
        self.search_entry.pack(pady=5)
        self.search_entry.bind('<KeyRelease>', lambda _event: self.load_patients())

        columns = ('ID', 'Nombre', 'Edad', 'Tratamiento', 'Próxima cita')
        self.table = ttk.Treeview(self.root, columns=columns, show='headings', height=9)
        widths = {'ID': 50, 'Nombre': 260, 'Edad': 80, 'Tratamiento': 280, 'Próxima cita': 140}
        for column in columns:
            self.table.heading(column, text=column)
            self.table.column(column, width=widths[column], anchor='center')
        self.table.pack(pady=10)
        self.table.bind('<Double-1>', lambda _event: self.edit_patient())

        buttons = tk.Frame(self.root)
        buttons.pack(pady=5)
        actions = [
            ('Ver pacientes', self.load_patients),
            ('Añadir paciente', self.add_patient_window),
            ('Modificar paciente', self.edit_patient),
            ('Eliminar paciente', self.delete_patient),
            ('Exportar a Excel', self.export_excel),
            ('Cargar JSON', self.import_json),
            ('DentalAI Copilot', self.open_copilot),
            ('Historial IA', self.open_history),
            ('Generar informe clínico', self.generate_patient_report),
            ('Mostrar estadísticas', self.show_stats),
            ('Salir', self.root.destroy),
        ]
        for index, (text, command) in enumerate(actions):
            tk.Button(buttons, text=text, width=28, command=command).grid(
                row=index // 2, column=index % 2, padx=6, pady=3
            )

    def selected_patient(self) -> dict[str, object] | None:
        selection = self.table.selection()
        if not selection:
            return None
        values = self.table.item(selection[0], 'values')
        return {
            'id': int(values[0]),
            'nombre': values[1],
            'edad': int(values[2]),
            'tratamiento': values[3],
            'proxima_cita': values[4],
        }

    def load_patients(self) -> None:
        self.table.delete(*self.table.get_children())
        rows = database.list_patients(self.search_entry.get().strip())
        for row in rows:
            self.table.insert('', 'end', values=tuple(row))
        self.counter_label.config(text=f'Pacientes registrados: {len(rows)}')

    def _patient_form(self, title: str, patient: dict[str, object] | None = None) -> None:
        window = tk.Toplevel(self.root)
        window.title(title)
        window.geometry('380x390')
        fields = {}
        labels = [('nombre', 'Nombre'), ('edad', 'Edad'), ('tratamiento', 'Tratamiento'), ('proxima_cita', 'Próxima cita')]
        for key, label in labels:
            tk.Label(window, text=label).pack()
            entry = tk.Entry(window, width=35)
            entry.pack(pady=5)
            if patient:
                entry.insert(0, str(patient.get(key, '')))
            fields[key] = entry

        def save() -> None:
            nombre = fields['nombre'].get().strip()
            tratamiento = fields['tratamiento'].get().strip()
            cita = fields['proxima_cita'].get().strip()
            try:
                edad = int(fields['edad'].get().strip())
                if edad < 0:
                    raise ValueError
            except ValueError:
                messagebox.showwarning('Aviso', 'La edad debe ser un número válido.')
                return
            if not nombre or not tratamiento:
                messagebox.showwarning('Aviso', 'Nombre y tratamiento son obligatorios.')
                return
            if patient:
                database.update_patient(int(patient['id']), nombre, edad, tratamiento, cita)
            else:
                database.add_patient(nombre, edad, tratamiento, cita)
            self.load_patients()
            window.destroy()

        tk.Button(window, text='Guardar', width=20, command=save).pack(pady=15)

    def add_patient_window(self) -> None:
        self._patient_form('Añadir paciente')

    def edit_patient(self) -> None:
        patient = self.selected_patient()
        if not patient:
            messagebox.showwarning('Aviso', 'Selecciona un paciente.')
            return
        self._patient_form('Modificar paciente', patient)

    def delete_patient(self) -> None:
        patient = self.selected_patient()
        if not patient:
            messagebox.showwarning('Aviso', 'Selecciona un paciente.')
            return
        if messagebox.askyesno('Confirmar eliminación', f"¿Eliminar a {patient['nombre']}?"):
            database.delete_patient(int(patient['id']))
            self.load_patients()

    def import_json(self) -> None:
        path = filedialog.askopenfilename(filetypes=[('JSON', '*.json')])
        if not path:
            return
        try:
            with open(path, 'r', encoding='utf-8') as file:
                records = json.load(file)
            if not isinstance(records, list):
                raise ValueError('El JSON debe contener una lista de pacientes.')
            imported = database.import_patients(records)
        except (OSError, json.JSONDecodeError, ValueError) as error:
            messagebox.showerror('Error', str(error))
            return
        self.load_patients()
        messagebox.showinfo('JSON', f'Se han importado {imported} pacientes.')

    def export_excel(self) -> None:
        path = filedialog.asksaveasfilename(
            defaultextension='.xlsx', filetypes=[('Excel', '*.xlsx')], initialfile='pacientes.xlsx'
        )
        if not path:
            return
        workbook = Workbook()
        sheet = workbook.active
        sheet.title = 'Pacientes'
        sheet.append(['ID', 'Nombre', 'Edad', 'Tratamiento', 'Próxima cita'])
        for row in database.list_patients():
            sheet.append(tuple(row))
        workbook.save(path)
        messagebox.showinfo('Excel', 'Archivo creado correctamente.')

    def generate_patient_report(self) -> None:
        patient = self.selected_patient()
        if not patient:
            messagebox.showwarning('Aviso', 'Selecciona un paciente.')
            return
        path = filedialog.asksaveasfilename(
            defaultextension='.pdf', filetypes=[('PDF', '*.pdf')],
            initialfile=f"informe_{patient['nombre']}.pdf"
        )
        if not path:
            return
        create_patient_report(path, patient, datetime.now().strftime('%d/%m/%Y'))
        messagebox.showinfo('PDF', 'Informe guardado correctamente.')

    def show_stats(self) -> None:
        stats = database.patient_stats()
        messagebox.showinfo(
            'Estadísticas',
            f"Pacientes registrados: {stats['total']}\n"
            f"Edad promedio: {stats['avg_age']:.1f}\n"
            f"Menores de edad: {stats['minors']}\n"
            f"Mayores de edad: {stats['adults']}\n"
            f"Tratamiento más frecuente: {stats['frequent_treatment']}",
        )

    def open_copilot(self) -> None:
        patient = self.selected_patient()
        patient_name = str(patient['nombre']) if patient else 'Paciente no seleccionado'
        window = tk.Toplevel(self.root)
        window.title('DentalAI Copilot')
        window.geometry('760x760')

        tk.Label(window, text='DentalAI Copilot', font=('Segoe UI', 18, 'bold')).pack(pady=(15, 2))
        tk.Label(window, text=f'Paciente: {patient_name}', font=('Segoe UI', 10, 'bold')).pack(pady=(0, 10))
        form = tk.Frame(window)
        form.pack(fill='x', padx=35)

        tk.Label(form, text='Síntomas principales').pack(anchor='w')
        symptoms = tk.Text(form, height=4, wrap='word')
        symptoms.pack(fill='x', pady=(2, 8))
        tk.Label(form, text='Duración de los síntomas').pack(anchor='w')
        duration = tk.Entry(form, width=45)
        duration.pack(anchor='w', pady=(2, 8))
        tk.Label(form, text='Dolor de 0 a 10').pack(anchor='w')
        pain = tk.Entry(form, width=15)
        pain.pack(anchor='w', pady=(2, 8))
        tk.Label(form, text='Antecedentes relevantes').pack(anchor='w')
        background = tk.Text(form, height=3, wrap='word')
        background.pack(fill='x', pady=(2, 8))

        options = tk.Frame(form)
        options.pack(anchor='w')
        fever = tk.BooleanVar(value=False)
        swelling = tk.BooleanVar(value=False)
        tk.Checkbutton(options, text='Fiebre', variable=fever).pack(side='left', padx=(0, 15))
        tk.Checkbutton(options, text='Inflamación', variable=swelling).pack(side='left')

        result_box = tk.Text(window, height=12, wrap='word', state='disabled')
        result_box.pack(fill='both', expand=True, padx=35, pady=10)
        current_result: AnalysisResult | None = None

        def show_result(text: str) -> None:
            result_box.config(state='normal')
            result_box.delete('1.0', 'end')
            result_box.insert('1.0', text)
            result_box.config(state='disabled')

        def analyze() -> None:
            nonlocal current_result
            symptoms_text = symptoms.get('1.0', 'end').strip()
            if not symptoms_text:
                messagebox.showwarning('Aviso', 'Escribe primero los síntomas.')
                return
            pain_text = pain.get().strip()
            if pain_text:
                try:
                    pain_value = int(pain_text)
                    if not 0 <= pain_value <= 10:
                        raise ValueError
                except ValueError:
                    messagebox.showwarning('Aviso', 'El dolor debe ser un número entre 0 y 10.')
                    return
            else:
                pain_value = None
            current_result = analyze_case(
                symptoms_text, duration.get(), pain_value,
                background.get('1.0', 'end').strip(), fever.get(), swelling.get()
            )
            show_result(
                f"ANÁLISIS CLÍNICO ORIENTATIVO\n\nPaciente:\n{patient_name}\n\n"
                f"Valoración:\n{current_result.valoracion}\n\nPrioridad:\n{current_result.prioridad}\n\n"
                f"Pruebas sugeridas:\n{current_result.pruebas}\n\nSeñales de alarma:\n{current_result.alarmas}\n\n"
                f"Información pendiente:\n{current_result.informacion_faltante}\n\n"
                "Aviso:\nResultado orientativo. Requiere validación profesional."
            )

        def save_analysis() -> None:
            if current_result is None:
                messagebox.showwarning('Aviso', 'Analiza primero el caso.')
                return
            pain_text = pain.get().strip()
            analysis_id = database.add_analysis({
                'paciente': patient_name,
                'fecha': datetime.now().strftime('%d/%m/%Y %H:%M'),
                'sintomas': symptoms.get('1.0', 'end').strip(),
                'duracion': duration.get().strip(),
                'dolor': int(pain_text) if pain_text.isdigit() else None,
                'antecedentes': background.get('1.0', 'end').strip(),
                'fiebre': fever.get(),
                'inflamacion': swelling.get(),
                'valoracion': current_result.valoracion,
                'prioridad': current_result.prioridad,
                'pruebas': current_result.pruebas,
                'alarmas': current_result.alarmas,
                'estado': 'Pendiente',
            })
            messagebox.showinfo('Análisis guardado', f'Análisis #{analysis_id} guardado correctamente.')

        actions = tk.Frame(window)
        actions.pack(pady=(0, 15))
        tk.Button(actions, text='Analizar caso', width=22, command=analyze).pack(side='left', padx=6)
        tk.Button(actions, text='Guardar análisis', width=22, command=save_analysis).pack(side='left', padx=6)

    def open_history(self) -> None:
        window = tk.Toplevel(self.root)
        window.title('Historial de análisis IA')
        window.geometry('1100x680')
        tk.Label(window, text='Historial de análisis IA', font=('Segoe UI', 18, 'bold')).pack(pady=(14, 4))
        summary = tk.Label(window, font=('Segoe UI', 10, 'bold'))
        summary.pack(pady=(0, 8))
        filters = tk.Frame(window)
        filters.pack(fill='x', padx=20)
        tk.Label(filters, text='Estado:').pack(side='left')
        state_var = tk.StringVar(value='Todos')
        state_combo = ttk.Combobox(filters, textvariable=state_var, values=('Todos', 'Pendiente', 'Validado', 'Rechazado'), state='readonly', width=16)
        state_combo.pack(side='left', padx=8)
        tk.Label(filters, text='Paciente:').pack(side='left', padx=(20, 0))
        patient_search = tk.Entry(filters, width=28)
        patient_search.pack(side='left', padx=8)

        columns = ('ID', 'Paciente', 'Fecha', 'Prioridad', 'Estado')
        history = ttk.Treeview(window, columns=columns, show='headings', height=16)
        widths = {'ID': 60, 'Paciente': 260, 'Fecha': 170, 'Prioridad': 110, 'Estado': 130}
        for column in columns:
            history.heading(column, text=column)
            history.column(column, width=widths[column], anchor='center')
        history.tag_configure('Pendiente', background='#fff4cc')
        history.tag_configure('Validado', background='#dcfce7')
        history.tag_configure('Rechazado', background='#fee2e2')
        history.pack(fill='both', expand=True, padx=20, pady=8)

        def reload_history(*_args) -> None:
            history.delete(*history.get_children())
            for row in database.list_analyses(state_var.get(), patient_search.get().strip()):
                history.insert('', 'end', values=tuple(row), tags=(row['estado'],))
            counts = database.analysis_counts()
            summary.config(text=f"Total: {counts['Total']} | Pendientes: {counts['Pendiente']} | Validados: {counts['Validado']} | Rechazados: {counts['Rechazado']}")

        def selected_analysis_id() -> int | None:
            selection = history.selection()
            if not selection:
                messagebox.showwarning('Aviso', 'Selecciona un análisis.')
                return None
            return int(history.item(selection[0], 'values')[0])

        def change_state(new_state: str) -> None:
            analysis_id = selected_analysis_id()
            if analysis_id is None:
                return
            if messagebox.askyesno('Confirmar cambio', f"¿Cambiar el análisis #{analysis_id} a '{new_state}'?"):
                database.update_analysis_state(analysis_id, new_state)
                reload_history()

        def show_detail() -> None:
            analysis_id = selected_analysis_id()
            if analysis_id is None:
                return
            row = database.get_analysis(analysis_id)
            if row is None:
                messagebox.showerror('Error', 'No se ha encontrado el análisis.')
                return
            detail = tk.Toplevel(window)
            detail.title(f'Detalle análisis #{analysis_id}')
            detail.geometry('760x680')
            tk.Label(detail, text=f'Análisis IA #{analysis_id}', font=('Segoe UI', 16, 'bold')).pack(pady=(12, 4))
            fields = [
                ('Paciente', row['paciente']), ('Fecha', row['fecha']), ('Síntomas', row['sintomas']),
                ('Duración', row['duracion'] or 'No indicada'), ('Dolor', row['dolor'] if row['dolor'] is not None else 'No indicado'),
                ('Antecedentes', row['antecedentes'] or 'No indicados'), ('Fiebre', 'Sí' if row['fiebre'] else 'No'),
                ('Inflamación', 'Sí' if row['inflamacion'] else 'No'), ('Valoración', row['valoracion']),
                ('Prioridad', row['prioridad']), ('Pruebas sugeridas', row['pruebas'] or 'No indicadas'),
                ('Señales de alarma', row['alarmas'] or 'No indicadas'), ('Estado', row['estado']),
            ]
            text = tk.Text(detail, wrap='word', padx=15, pady=15)
            text.pack(fill='both', expand=True, padx=15, pady=8)
            for label, value in fields:
                text.insert('end', f'{label}:\n{value}\n\n')
            text.config(state='disabled')

            def export_pdf() -> None:
                path = filedialog.asksaveasfilename(
                    defaultextension='.pdf', filetypes=[('PDF', '*.pdf')],
                    initialfile=f"analisis_IA_{row['paciente']}_{analysis_id}.pdf"
                )
                if path:
                    create_analysis_report(path, analysis_id, fields)
                    messagebox.showinfo('PDF', 'Análisis exportado correctamente.')

            actions = tk.Frame(detail)
            actions.pack(pady=(0, 12))
            tk.Button(actions, text='Exportar a PDF', width=20, command=export_pdf).pack(side='left', padx=6)
            tk.Button(actions, text='Cerrar', width=16, command=detail.destroy).pack(side='left', padx=6)

        actions = tk.Frame(window)
        actions.pack(pady=10)
        tk.Button(actions, text='Ver detalle', width=17, command=show_detail).pack(side='left', padx=4)
        tk.Button(actions, text='Validar', width=17, command=lambda: change_state('Validado')).pack(side='left', padx=4)
        tk.Button(actions, text='Rechazar', width=17, command=lambda: change_state('Rechazado')).pack(side='left', padx=4)
        tk.Button(actions, text='Marcar pendiente', width=17, command=lambda: change_state('Pendiente')).pack(side='left', padx=4)
        tk.Button(actions, text='Actualizar', width=17, command=reload_history).pack(side='left', padx=4)
        state_combo.bind('<<ComboboxSelected>>', reload_history)
        patient_search.bind('<KeyRelease>', reload_history)
        history.bind('<Double-1>', lambda _event: show_detail())
        reload_history()


def main() -> None:
    root = tk.Tk()
    DentalAIApp(root)
    root.mainloop()


if __name__ == '__main__':
    main()
