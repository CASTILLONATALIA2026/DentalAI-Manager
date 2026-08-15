
import json
from datetime import datetime
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from typing import Callable

import customtkinter as ctk
from openpyxl import Workbook

import database
from copilot_logic import AnalysisResult, analyze_case
from pdf_utils import create_analysis_report, create_patient_report


ctk.set_appearance_mode("light")
ctk.set_default_color_theme("blue")


class DentalAIApp(ctk.CTk):
    """DentalAI Manager v2: interfaz moderna conectada al motor existente."""

    def __init__(self) -> None:
        super().__init__()
        self.title("DentalAI Manager")
        self.geometry("1280x820")
        self.minsize(1050, 700)
        self.after(100, lambda: self.state("zoomed"))

        database.init_db()
        self.current_patient_id: int | None = None
        self.current_screen = "dashboard"

        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self._configure_treeview_style()
        self._build_sidebar()
        self.content = ctk.CTkFrame(self, fg_color="#F4F7FB", corner_radius=0)
        self.content.grid(row=0, column=1, sticky="nsew")
        self.content.grid_columnconfigure(0, weight=1)
        self.content.grid_rowconfigure(0, weight=1)

        self.show_dashboard()

    def _configure_treeview_style(self) -> None:
        style = ttk.Style(self)
        try:
            style.theme_use("clam")
        except tk.TclError:
            pass
        style.configure(
            "Dental.Treeview",
            background="white",
            fieldbackground="white",
            foreground="#1F2937",
            rowheight=32,
            borderwidth=0,
            font=("Segoe UI", 10),
        )
        style.configure(
            "Dental.Treeview.Heading",
            background="#E8EFF7",
            foreground="#0F4C81",
            relief="flat",
            font=("Segoe UI", 10, "bold"),
        )
        style.map("Dental.Treeview", background=[("selected", "#CFE3F5")])

    def _build_sidebar(self) -> None:
        sidebar = ctk.CTkFrame(self, width=235, corner_radius=0, fg_color="#0F4C81")
        sidebar.grid(row=0, column=0, sticky="nsew")
        sidebar.grid_propagate(False)

        ctk.CTkLabel(
            sidebar,
            text="🦷 DentalAI",
            font=("Segoe UI", 25, "bold"),
            text_color="white",
        ).pack(pady=(34, 2))
        ctk.CTkLabel(
            sidebar,
            text="Manager",
            font=("Segoe UI", 15),
            text_color="#D9ECFF",
        ).pack(pady=(0, 28))

        menu: list[tuple[str, Callable[[], None]]] = [
            ("Dashboard", self.show_dashboard),
            ("Pacientes", self.show_patients),
            ("Prescripciones", self.show_prescriptions),
            ("IA Clínica", self.show_copilot),
            ("Historial IA", self.show_history),
            ("Estadísticas", self.show_statistics),
        ]
        self.nav_buttons: dict[str, ctk.CTkButton] = {}
        for label, command in menu:
            button = ctk.CTkButton(
                sidebar,
                text=label,
                command=command,
                width=188,
                height=43,
                corner_radius=8,
                fg_color="transparent",
                hover_color="#1E6498",
                anchor="w",
                font=("Segoe UI", 13),
            )
            button.pack(padx=22, pady=5)
            self.nav_buttons[label] = button

        ctk.CTkButton(
            sidebar,
            text="Salir",
            command=self.destroy,
            width=188,
            height=40,
            fg_color="#C0392B",
            hover_color="#A93226",
        ).pack(side="bottom", padx=22, pady=(0, 18))
        ctk.CTkLabel(
            sidebar,
            text="Desarrollado por\nNatalia Castillo",
            font=("Segoe UI", 11, "italic"),
            text_color="#D9ECFF",
        ).pack(side="bottom", pady=16)

    def _clear_content(self) -> None:
        for widget in self.content.winfo_children():
            widget.destroy()

    def _page(self, title: str, subtitle: str = "") -> ctk.CTkFrame:
        self._clear_content()
        page = ctk.CTkFrame(self.content, fg_color="#F4F7FB", corner_radius=0)
        page.grid(row=0, column=0, sticky="nsew")
        page.grid_columnconfigure(0, weight=1)
        page.grid_rowconfigure(2, weight=1)
        ctk.CTkLabel(
            page,
            text=title,
            font=("Segoe UI", 29, "bold"),
            text_color="#1F2937",
        ).grid(row=0, column=0, sticky="w", padx=34, pady=(28, 4))
        if subtitle:
            ctk.CTkLabel(
                page,
                text=subtitle,
                font=("Segoe UI", 14),
                text_color="#6B7280",
            ).grid(row=1, column=0, sticky="w", padx=34, pady=(0, 18))
        return page

    def _stat_card(self, parent: ctk.CTkFrame, column: int, title: str, value: object) -> None:
        card = ctk.CTkFrame(
            parent,
            height=128,
            corner_radius=14,
            fg_color="white",
            border_width=1,
            border_color="#DDE5EE",
        )
        card.grid(row=0, column=column, padx=9, sticky="nsew")
        card.grid_propagate(False)
        ctk.CTkLabel(card, text=title, font=("Segoe UI", 14), text_color="#6B7280").pack(
            anchor="w", padx=20, pady=(20, 7)
        )
        ctk.CTkLabel(card, text=str(value), font=("Segoe UI", 30, "bold"), text_color="#0F4C81").pack(
            anchor="w", padx=20
        )

    # ---------------- Dashboard ----------------
    def show_dashboard(self) -> None:
        self.current_screen = "dashboard"
        page = self._page("Panel principal", "Resumen general de la clínica")
        counts = database.analysis_counts()
        patients = database.list_patients()
        stats = database.patient_stats()

        cards = ctk.CTkFrame(page, fg_color="transparent")
        cards.grid(row=2, column=0, sticky="new", padx=25, pady=(0, 18))
        cards.grid_columnconfigure((0, 1, 2, 3), weight=1)
        self._stat_card(cards, 0, "Pacientes", len(patients))
        self._stat_card(cards, 1, "Análisis pendientes", counts["Pendiente"])
        self._stat_card(cards, 2, "Validados", counts["Validado"])
        self._stat_card(cards, 3, "Rechazados", counts["Rechazado"])

        lower = ctk.CTkFrame(page, fg_color="transparent")
        lower.grid(row=3, column=0, sticky="nsew", padx=34, pady=(0, 28))
        lower.grid_columnconfigure((0, 1), weight=1)

        actions = ctk.CTkFrame(lower, fg_color="white", corner_radius=14, border_width=1, border_color="#DDE5EE")
        actions.grid(row=0, column=0, sticky="nsew", padx=(0, 10))
        ctk.CTkLabel(actions, text="Accesos rápidos", font=("Segoe UI", 18, "bold"), text_color="#1F2937").pack(
            anchor="w", padx=22, pady=(20, 14)
        )
        ctk.CTkButton(actions, text="+ Nuevo paciente", command=self.open_patient_form, height=42).pack(
            fill="x", padx=22, pady=6
        )
        ctk.CTkButton(actions, text="Abrir IA Clínica", command=self.show_copilot, height=42).pack(
            fill="x", padx=22, pady=6
        )
        ctk.CTkButton(actions, text="Ver historial IA", command=self.show_history, height=42).pack(
            fill="x", padx=22, pady=6
        )
        ctk.CTkButton(actions, text="Ver pacientes", command=self.show_patients, height=42).pack(
            fill="x", padx=22, pady=(6, 22)
        )

        summary = ctk.CTkFrame(lower, fg_color="white", corner_radius=14, border_width=1, border_color="#DDE5EE")
        summary.grid(row=0, column=1, sticky="nsew", padx=(10, 0))
        ctk.CTkLabel(summary, text="Resumen clínico", font=("Segoe UI", 18, "bold"), text_color="#1F2937").pack(
            anchor="w", padx=22, pady=(20, 14)
        )
        lines = [
            f"Edad promedio: {stats['avg_age']:.1f}",
            f"Menores de edad: {stats['minors']}",
            f"Mayores de edad: {stats['adults']}",
            f"Tratamiento más frecuente: {stats['frequent_treatment']}",
        ]
        for line in lines:
            ctk.CTkLabel(summary, text=line, font=("Segoe UI", 14), text_color="#374151").pack(
                anchor="w", padx=22, pady=7
            )

    # ---------------- Pacientes ----------------
    def show_patients(self) -> None:
        self.current_screen = "patients"
        page = self._page("Pacientes", "Gestión completa de pacientes")

        toolbar = ctk.CTkFrame(page, fg_color="transparent")
        toolbar.grid(row=2, column=0, sticky="ew", padx=34, pady=(0, 12))
        toolbar.grid_columnconfigure(0, weight=1)

        search_var = tk.StringVar()
        search_entry = ctk.CTkEntry(
            toolbar,
            textvariable=search_var,
            placeholder_text="Buscar paciente...",
            height=40,
        )
        search_entry.grid(row=0, column=0, sticky="ew", padx=(0, 12))

        ctk.CTkButton(
            toolbar,
            text="Nuevo",
            command=self.open_patient_form,
            width=110,
            height=40,
        ).grid(row=0, column=1, padx=4)

        ctk.CTkButton(
            toolbar,
            text="Editar",
            command=lambda: self._edit_selected_patient(tree),
            width=110,
            height=40,
        ).grid(row=0, column=2, padx=4)

        ctk.CTkButton(
            toolbar,
            text="Eliminar",
            command=lambda: self._delete_selected_patient(tree),
            width=110,
            height=40,
            fg_color="#C0392B",
            hover_color="#A93226",
        ).grid(row=0, column=3, padx=4)

        table_frame = ctk.CTkFrame(
            page,
            fg_color="white",
            corner_radius=12,
            border_width=1,
            border_color="#DDE5EE",
        )
        table_frame.grid(row=3, column=0, sticky="nsew", padx=34, pady=(0, 12))
        table_frame.grid_columnconfigure(0, weight=1)
        table_frame.grid_rowconfigure(0, weight=1)

        columns = (
            "ID",
            "Nombre",
            "Edad",
            "Teléfono",
            "Email",
            "Tratamiento",
            "Próxima cita",
            "Observaciones",
        )
        widths = {
            "ID": 60,
            "Nombre": 200,
            "Edad": 70,
            "Teléfono": 130,
            "Email": 220,
            "Tratamiento": 220,
            "Próxima cita": 140,
            "Observaciones": 280,
        }

        tree = ttk.Treeview(
            table_frame,
            columns=columns,
            show="headings",
            style="Dental.Treeview",
        )
        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, width=widths[col], anchor="center")

        tree.grid(row=0, column=0, sticky="nsew", padx=12, pady=12)

        scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=tree.yview)
        scrollbar.grid(row=0, column=1, sticky="ns", pady=12, padx=(0, 10))
        tree.configure(yscrollcommand=scrollbar.set)

        def reload(*_args: object) -> None:
            tree.delete(*tree.get_children())
            for row in database.list_patients(search_var.get().strip()):
                tree.insert("", "end", values=tuple(row))

        search_var.trace_add("write", reload)
        tree.bind("<Double-1>", lambda _event: self._edit_selected_patient(tree))
        reload()

        detail_frame = ctk.CTkFrame(
            page,
            fg_color="white",
            corner_radius=12,
            border_width=1,
            border_color="#DDE5EE",
        )
        detail_frame.grid(
            row=4,
            column=0,
            sticky="ew",
            padx=34,
            pady=(0, 12),
        )

        detail_label = ctk.CTkLabel(
            detail_frame,
            text="Selecciona un paciente para ver sus datos",
            anchor="w",
            justify="left",
            font=("Segoe UI", 13),
            text_color="#374151",
        )
        detail_label.pack(fill="x", padx=18, pady=16)

        quick_actions = ctk.CTkFrame(detail_frame, fg_color="transparent")
        quick_actions.pack(fill="x", padx=18, pady=(0, 16))

        ctk.CTkButton(
            quick_actions,
            text="IA Clínica",
            width=130,
            command=lambda: self._open_selected_patient_copilot(tree),
        ).pack(side="left", padx=(0, 8))

        ctk.CTkButton(
            quick_actions,
            text="Historial IA",
            width=130,
            command=lambda: self._open_selected_patient_history(tree),
        ).pack(side="left", padx=8)

        ctk.CTkButton(
            quick_actions,
            text="Informe PDF",
            width=130,
            command=lambda: self.generate_patient_report(tree),
        ).pack(side="left", padx=8)

        def update_detail(_event=None) -> None:
            selection = tree.selection()
            if not selection:
                detail_label.configure(
                    text="Selecciona un paciente para ver sus datos"
                )
                return

            values = tree.item(selection[0], "values")
            detail_label.configure(
                text=(
                    f"Paciente: {values[1]}\n"
                    f"Edad: {values[2]} años\n"
                    f"Teléfono: {values[3] or 'No indicado'}\n"
                    f"Email: {values[4] or 'No indicado'}\n"
                    f"Tratamiento: {values[5]}\n"
                    f"Próxima cita: {values[6] or 'No indicada'}\n"
                    f"Observaciones: {values[7] or 'Sin observaciones'}"
                )
            )

        tree.bind("<<TreeviewSelect>>", update_detail)

        footer = ctk.CTkFrame(page, fg_color="transparent")
        footer.grid(row=5, column=0, sticky="ew", padx=34, pady=(0, 24))

        ctk.CTkButton(
            footer,
            text="Exportar Excel",
            command=self.export_excel,
            width=145,
        ).pack(side="left", padx=(0, 8))

        ctk.CTkButton(
            footer,
            text="Importar JSON",
            command=lambda: self.import_json(reload),
            width=145,
        ).pack(side="left", padx=8)

        ctk.CTkButton(
            footer,
            text="Informe PDF",
            command=lambda: self.generate_patient_report(tree),
            width=145,
        ).pack(side="left", padx=8)

    def _open_selected_patient_copilot(self, tree: ttk.Treeview) -> None:
        patient = self._selected_patient_from_tree(tree)
        if not patient:
            return
        self.show_copilot(str(patient["nombre"]))

    def _open_selected_patient_history(self, tree: ttk.Treeview) -> None:
        patient = self._selected_patient_from_tree(tree)
        if not patient:
            return
        self.show_history(str(patient["nombre"]))

    def _selected_patient_from_tree(self, tree: ttk.Treeview) -> dict[str, object] | None:
        selection = tree.selection()
        if not selection:
            messagebox.showwarning("Aviso", "Selecciona un paciente.")
            return None

        values = tree.item(selection[0], "values")
        return {
            "id": int(values[0]),
            "nombre": values[1],
            "edad": int(values[2]),
            "telefono": values[3],
            "email": values[4],
            "tratamiento": values[5],
            "proxima_cita": values[6],
            "observaciones": values[7],
        }

    def open_patient_form(self, patient: dict[str, object] | None = None) -> None:
        window = ctk.CTkToplevel(self)
        window.title("Modificar paciente" if patient else "Nuevo paciente")
        window.geometry("470x520")
        window.minsize(430, 460)
        window.transient(self)
        window.grab_set()

        ctk.CTkLabel(
            window,
            text="Modificar paciente" if patient else "Nuevo paciente",
            font=("Segoe UI", 22, "bold"),
        ).pack(pady=(24, 18))

        fields: dict[str, ctk.CTkEntry] = {}
        labels = [
            ("nombre", "Nombre"),
            ("edad", "Edad"),
            ("telefono", "Teléfono"),
            ("email", "Email"),
            ("tratamiento", "Tratamiento"),
            ("proxima_cita", "Próxima cita"),
        ]

        form = ctk.CTkScrollableFrame(window, fg_color="transparent")
        form.pack(fill="both", expand=True, padx=34, pady=(0, 20))

        for key, label in labels:
            ctk.CTkLabel(form, text=label, anchor="w").pack(
                fill="x",
                pady=(7, 3),
            )
            entry = ctk.CTkEntry(form, height=38)
            entry.pack(fill="x")

            if patient:
                entry.insert(0, str(patient.get(key, "")))

            fields[key] = entry

        ctk.CTkLabel(form, text="Observaciones", anchor="w").pack(
            fill="x",
            pady=(7, 3),
        )
        observaciones = ctk.CTkTextbox(form, height=90)
        observaciones.pack(fill="x")

        if patient:
            observaciones.insert(
                "1.0",
                str(patient.get("observaciones", "")),
            )

        def save() -> None:
            nombre = fields["nombre"].get().strip()
            tratamiento = fields["tratamiento"].get().strip()
            cita = fields["proxima_cita"].get().strip()
            telefono = fields["telefono"].get().strip()
            email = fields["email"].get().strip()
            observaciones_text = observaciones.get("1.0", "end").strip()

            try:
                edad = int(fields["edad"].get().strip())
                if edad < 0:
                    raise ValueError
            except ValueError:
                messagebox.showwarning(
                    "Aviso",
                    "La edad debe ser un número válido.",
                    parent=window,
                )
                return

            if not nombre or not tratamiento:
                messagebox.showwarning(
                    "Aviso",
                    "Nombre y tratamiento son obligatorios.",
                    parent=window,
                )
                return

            if patient:
                database.update_patient(
                    int(patient["id"]),
                    nombre,
                    edad,
                    tratamiento,
                    cita,
                    telefono,
                    email,
                    observaciones_text,
                )
            else:
                database.add_patient(
                    nombre,
                    edad,
                    tratamiento,
                    cita,
                    telefono,
                    email,
                    observaciones_text,
                )

            window.destroy()

            if self.current_screen == "patients":
                self.show_patients()
            else:
                self.show_dashboard()

        ctk.CTkButton(
            form,
            text="Guardar",
            command=save,
            height=42,
        ).pack(fill="x", pady=(18, 12))

    def _edit_selected_patient(self, tree: ttk.Treeview) -> None:
        patient = self._selected_patient_from_tree(tree)
        if patient:
            self.open_patient_form(patient)

    def _delete_selected_patient(self, tree: ttk.Treeview) -> None:
        patient = self._selected_patient_from_tree(tree)
        if not patient:
            return
        if messagebox.askyesno("Confirmar", f"¿Eliminar a {patient['nombre']}?"):
            database.delete_patient(int(patient["id"]))
            self.show_patients()

    def import_json(self, callback: Callable[[], None] | None = None) -> None:
        path = filedialog.askopenfilename(filetypes=[("JSON", "*.json")])
        if not path:
            return
        try:
            with open(path, "r", encoding="utf-8") as file:
                records = json.load(file)
            if not isinstance(records, list):
                raise ValueError("El JSON debe contener una lista de pacientes.")
            imported = database.import_patients(records)
        except (OSError, json.JSONDecodeError, ValueError) as error:
            messagebox.showerror("Error", str(error))
            return
        if callback:
            callback()
        messagebox.showinfo("JSON", f"Se han importado {imported} pacientes.")

    def export_excel(self) -> None:
        path = filedialog.asksaveasfilename(
            defaultextension=".xlsx",
            filetypes=[("Excel", "*.xlsx")],
            initialfile="pacientes.xlsx",
        )
        if not path:
            return

        workbook = Workbook()
        sheet = workbook.active
        sheet.title = "Pacientes"
        sheet.append(
            [
                "ID",
                "Nombre",
                "Edad",
                "Teléfono",
                "Email",
                "Tratamiento",
                "Próxima cita",
                "Observaciones",
            ]
        )

        for row in database.list_patients():
            sheet.append(tuple(row))

        workbook.save(path)
        messagebox.showinfo("Excel", "Archivo creado correctamente.")

    def generate_patient_report(self, tree: ttk.Treeview) -> None:
        patient = self._selected_patient_from_tree(tree)
        if not patient:
            return
        path = filedialog.asksaveasfilename(
            defaultextension=".pdf",
            filetypes=[("PDF", "*.pdf")],
            initialfile=f"informe_{patient['nombre']}.pdf",
        )
        if path:
            create_patient_report(path, patient, datetime.now().strftime("%d/%m/%Y"))
            messagebox.showinfo("PDF", "Informe guardado correctamente.")

    # ---------------- Prescripciones ----------------
    def show_prescriptions(self) -> None:
        self.current_screen = "prescriptions"
        page = self._page(
            "Prescripciones",
            "Creación y seguimiento de prescripciones",
        )

        wrapper = ctk.CTkFrame(page, fg_color="transparent")
        wrapper.grid(row=2, column=0, sticky="nsew", padx=34, pady=(0, 24))
        wrapper.grid_columnconfigure((0, 1), weight=1)
        wrapper.grid_rowconfigure(0, weight=1)

        # Panel izquierdo: nueva prescripción
        form = ctk.CTkScrollableFrame(
            wrapper,
            fg_color="white",
            corner_radius=14,
            border_width=1,
            border_color="#DDE5EE",
        )
        form.grid(row=0, column=0, sticky="nsew", padx=(0, 10))

        # Panel derecho: historial
        history = ctk.CTkFrame(
            wrapper,
            fg_color="white",
            corner_radius=14,
            border_width=1,
            border_color="#DDE5EE",
        )
        history.grid(row=0, column=1, sticky="nsew", padx=(10, 0))
        history.grid_columnconfigure(0, weight=1)
        history.grid_rowconfigure(1, weight=1)

        ctk.CTkLabel(
            form,
            text="Nueva prescripción",
            font=("Segoe UI", 20, "bold"),
            text_color="#1F2937",
        ).pack(anchor="w", padx=22, pady=(22, 14))

        patient_names = [row["nombre"] for row in database.list_patients()]
        patient_var = tk.StringVar(
            value=patient_names[0] if patient_names else "Paciente no seleccionado"
        )

        def field_label(text: str) -> None:
            ctk.CTkLabel(form, text=text, anchor="w").pack(
                fill="x", padx=22, pady=(0, 4)
            )

        field_label("Paciente")
        patient_combo = ctk.CTkComboBox(
            form,
            values=patient_names or ["Paciente no seleccionado"],
            variable=patient_var,
        )
        patient_combo.pack(fill="x", padx=22, pady=(0, 12))

        field_label("Medicamento")
        medication = ctk.CTkEntry(form, placeholder_text="Ej. Amoxicilina")
        medication.pack(fill="x", padx=22, pady=(0, 12))

        field_label("Dosis")
        dose = ctk.CTkEntry(form, placeholder_text="Ej. 500 mg")
        dose.pack(fill="x", padx=22, pady=(0, 12))

        field_label("Frecuencia")
        frequency = ctk.CTkEntry(form, placeholder_text="Ej. Cada 8 horas")
        frequency.pack(fill="x", padx=22, pady=(0, 12))

        field_label("Duración")
        duration = ctk.CTkEntry(form, placeholder_text="Ej. 7 días")
        duration.pack(fill="x", padx=22, pady=(0, 12))

        field_label("Indicaciones")
        instructions = ctk.CTkTextbox(form, height=90)
        instructions.pack(fill="x", padx=22, pady=(0, 12))

        # Historial
        ctk.CTkLabel(
            history,
            text="Historial de prescripciones",
            font=("Segoe UI", 20, "bold"),
            text_color="#1F2937",
        ).grid(row=0, column=0, sticky="w", padx=22, pady=(22, 14))

        table_frame = ctk.CTkFrame(history, fg_color="transparent")
        table_frame.grid(row=1, column=0, sticky="nsew", padx=18, pady=(0, 12))
        table_frame.grid_columnconfigure(0, weight=1)
        table_frame.grid_rowconfigure(0, weight=1)

        columns = ("ID", "Paciente", "Fecha", "Medicamento", "Dosis", "Estado")
        widths = {
            "ID": 45,
            "Paciente": 135,
            "Fecha": 125,
            "Medicamento": 145,
            "Dosis": 80,
            "Estado": 85,
        }

        prescription_tree = ttk.Treeview(
            table_frame,
            columns=columns,
            show="headings",
            style="Dental.Treeview",
        )
        for col in columns:
            prescription_tree.heading(col, text=col)
            prescription_tree.column(col, width=widths[col], anchor="center")

        prescription_tree.grid(row=0, column=0, sticky="nsew")
        scrollbar = ttk.Scrollbar(
            table_frame, orient="vertical", command=prescription_tree.yview
        )
        scrollbar.grid(row=0, column=1, sticky="ns")
        prescription_tree.configure(yscrollcommand=scrollbar.set)

        def reload_prescriptions() -> None:
            prescription_tree.delete(*prescription_tree.get_children())
            for row in database.list_prescriptions():
                prescription_tree.insert(
                    "",
                    "end",
                    values=(
                        row["id"],
                        row["paciente"],
                        row["fecha"],
                        row["medicamento"],
                        row["dosis"],
                        row["estado"],
                    ),
                )

        def selected_prescription_id() -> int | None:
            selection = prescription_tree.selection()
            if not selection:
                messagebox.showwarning("Aviso", "Selecciona una prescripción.")
                return None
            values = prescription_tree.item(selection[0], "values")
            return int(values[0])

        def save_prescription() -> None:
            patient = patient_var.get().strip()
            med = medication.get().strip()
            med_dose = dose.get().strip()
            med_frequency = frequency.get().strip()
            med_duration = duration.get().strip()
            notes = instructions.get("1.0", "end").strip()

            if not patient or patient == "Paciente no seleccionado":
                messagebox.showwarning("Aviso", "Selecciona un paciente.")
                return
            if not med or not med_dose or not med_frequency or not med_duration:
                messagebox.showwarning(
                    "Aviso",
                    "Completa medicamento, dosis, frecuencia y duración.",
                )
                return

            database.add_prescription(
                {
                    "paciente": patient,
                    "fecha": datetime.now().strftime("%d/%m/%Y %H:%M"),
                    "medicamento": med,
                    "dosis": med_dose,
                    "frecuencia": med_frequency,
                    "duracion": med_duration,
                    "indicaciones": notes,
                    "estado": "Activa",
                }
            )
            reload_prescriptions()
            medication.delete(0, "end")
            dose.delete(0, "end")
            frequency.delete(0, "end")
            duration.delete(0, "end")
            instructions.delete("1.0", "end")
            messagebox.showinfo(
                "Prescripción", "Prescripción guardada correctamente."
            )

        def show_prescription_detail() -> None:
            prescription_id = selected_prescription_id()
            if prescription_id is None:
                return
            row = database.get_prescription(prescription_id)
            if row is None:
                messagebox.showerror(
                    "Error", "No se ha encontrado la prescripción."
                )
                return

            window = ctk.CTkToplevel(self)
            window.title(f"Detalle prescripción #{prescription_id}")
            window.geometry("650x650")
            window.minsize(560, 520)
            window.transient(self)

            container = ctk.CTkScrollableFrame(window, fg_color="#F4F7FB")
            container.pack(fill="both", expand=True, padx=18, pady=18)

            ctk.CTkLabel(
                container,
                text=f"Prescripción #{prescription_id}",
                font=("Segoe UI", 24, "bold"),
                text_color="#1F2937",
            ).pack(anchor="w", pady=(6, 14))

            fields = [
                ("Paciente", row["paciente"]),
                ("Fecha", row["fecha"]),
                ("Medicamento", row["medicamento"]),
                ("Dosis", row["dosis"]),
                ("Frecuencia", row["frecuencia"]),
                ("Duración", row["duracion"]),
                ("Indicaciones", row["indicaciones"] or "Sin indicaciones"),
                ("Estado", row["estado"]),
            ]
            for title, value in fields:
                card = ctk.CTkFrame(
                    container,
                    fg_color="white",
                    corner_radius=10,
                    border_width=1,
                    border_color="#DDE5EE",
                )
                card.pack(fill="x", pady=(0, 10))
                ctk.CTkLabel(
                    card,
                    text=title,
                    font=("Segoe UI", 13, "bold"),
                    text_color="#1F2937",
                ).pack(anchor="w", padx=16, pady=(12, 4))
                ctk.CTkLabel(
                    card,
                    text=str(value),
                    justify="left",
                    anchor="w",
                    wraplength=540,
                    text_color="#374151",
                ).pack(fill="x", padx=16, pady=(0, 12))

            ctk.CTkButton(
                container, text="Cerrar", command=window.destroy, width=120
            ).pack(anchor="w", pady=(6, 12))

        def change_prescription_state(new_state: str) -> None:
            prescription_id = selected_prescription_id()
            if prescription_id is None:
                return
            database.update_prescription_state(prescription_id, new_state)
            reload_prescriptions()

        ctk.CTkButton(
            form,
            text="Guardar prescripción",
            height=40,
            command=save_prescription,
        ).pack(fill="x", padx=22, pady=(4, 22))

        actions = ctk.CTkFrame(history, fg_color="transparent")
        actions.grid(row=2, column=0, sticky="ew", padx=18, pady=(0, 18))

        ctk.CTkButton(
            actions, text="Ver detalle", command=show_prescription_detail, width=110
        ).pack(side="left", padx=(0, 6))
        ctk.CTkButton(
            actions,
            text="Activa",
            command=lambda: change_prescription_state("Activa"),
            width=80,
        ).pack(side="left", padx=6)
        ctk.CTkButton(
            actions,
            text="Finalizada",
            command=lambda: change_prescription_state("Finalizada"),
            width=95,
        ).pack(side="left", padx=6)
        ctk.CTkButton(
            actions,
            text="Cancelar",
            command=lambda: change_prescription_state("Cancelada"),
            width=90,
            fg_color="#C0392B",
            hover_color="#A93226",
        ).pack(side="left", padx=6)

        prescription_tree.bind(
            "<Double-1>", lambda _event: show_prescription_detail()
        )
        reload_prescriptions()

    # ---------------- Copilot ----------------
    def show_copilot(self, selected_patient: str | None = None) -> None:
        page = self._page("IA Clínica", "Análisis orientativo sujeto a validación profesional")
        wrapper = ctk.CTkFrame(page, fg_color="transparent")
        wrapper.grid(row=2, column=0, sticky="nsew", padx=34, pady=(0, 24))
        wrapper.grid_columnconfigure((0, 1), weight=1)
        wrapper.grid_rowconfigure(0, weight=1)

        form = ctk.CTkFrame(wrapper, fg_color="white", corner_radius=14, border_width=1, border_color="#DDE5EE")
        form.grid(row=0, column=0, sticky="nsew", padx=(0, 10))
        result_frame = ctk.CTkFrame(wrapper, fg_color="white", corner_radius=14, border_width=1, border_color="#DDE5EE")
        result_frame.grid(row=0, column=1, sticky="nsew", padx=(10, 0))

        patient_names = [row["nombre"] for row in database.list_patients()]
        default_patient = (
            selected_patient
            if selected_patient in patient_names
            else (
                patient_names[0]
                if patient_names
                else "Paciente no seleccionado"
            )
        )

        patient_var = tk.StringVar(value=default_patient)
        ctk.CTkLabel(form, text="Paciente", anchor="w").pack(fill="x", padx=22, pady=(22, 4))
        patient_combo = ctk.CTkComboBox(form, values=patient_names or ["Paciente no seleccionado"], variable=patient_var)
        patient_combo.pack(fill="x", padx=22)

        ctk.CTkLabel(form, text="Síntomas principales", anchor="w").pack(fill="x", padx=22, pady=(14, 4))
        symptoms = ctk.CTkTextbox(form, height=90)
        symptoms.pack(fill="x", padx=22)
        ctk.CTkLabel(form, text="Duración", anchor="w").pack(fill="x", padx=22, pady=(12, 4))
        duration = ctk.CTkEntry(form)
        duration.pack(fill="x", padx=22)
        ctk.CTkLabel(form, text="Dolor (0-10)", anchor="w").pack(fill="x", padx=22, pady=(12, 4))
        pain = ctk.CTkEntry(form)
        pain.pack(fill="x", padx=22)
        ctk.CTkLabel(form, text="Antecedentes relevantes", anchor="w").pack(fill="x", padx=22, pady=(12, 4))
        background = ctk.CTkTextbox(form, height=75)
        background.pack(fill="x", padx=22)

        flags = ctk.CTkFrame(form, fg_color="transparent")
        flags.pack(fill="x", padx=22, pady=12)
        fever = tk.BooleanVar(value=False)
        swelling = tk.BooleanVar(value=False)
        ctk.CTkCheckBox(flags, text="Fiebre", variable=fever).pack(side="left", padx=(0, 18))
        ctk.CTkCheckBox(flags, text="Inflamación", variable=swelling).pack(side="left")

        result_box = ctk.CTkTextbox(result_frame, wrap="word")
        result_box.pack(fill="both", expand=True, padx=18, pady=18)
        result_box.configure(state="disabled")
        current_result: AnalysisResult | None = None

        def display(text: str) -> None:
            result_box.configure(state="normal")
            result_box.delete("1.0", "end")
            result_box.insert("1.0", text)
            result_box.configure(state="disabled")

        def analyze() -> None:
            nonlocal current_result
            symptom_text = symptoms.get("1.0", "end").strip()
            if not symptom_text:
                messagebox.showwarning("Aviso", "Escribe primero los síntomas.")
                return
            pain_text = pain.get().strip()
            if pain_text:
                try:
                    pain_value = int(pain_text)
                    if not 0 <= pain_value <= 10:
                        raise ValueError
                except ValueError:
                    messagebox.showwarning("Aviso", "El dolor debe ser un número entre 0 y 10.")
                    return
            else:
                pain_value = None
            current_result = analyze_case(
                symptom_text,
                duration.get(),
                pain_value,
                background.get("1.0", "end").strip(),
                fever.get(),
                swelling.get(),
            )
            display(
                f"ANÁLISIS CLÍNICO ORIENTATIVO\n\nPaciente:\n{patient_var.get()}\n\n"
                f"Valoración:\n{current_result.valoracion}\n\nPrioridad:\n{current_result.prioridad}\n\n"
                f"Pruebas sugeridas:\n{current_result.pruebas}\n\nSeñales de alarma:\n{current_result.alarmas}\n\n"
                f"Información pendiente:\n{current_result.informacion_faltante}\n\n"
                "Aviso: resultado orientativo. Requiere validación profesional."
            )

        def save_analysis() -> None:
            if current_result is None:
                messagebox.showwarning("Aviso", "Analiza primero el caso.")
                return
            pain_text = pain.get().strip()
            analysis_id = database.add_analysis({
                "paciente": patient_var.get(),
                "fecha": datetime.now().strftime("%d/%m/%Y %H:%M"),
                "sintomas": symptoms.get("1.0", "end").strip(),
                "duracion": duration.get().strip(),
                "dolor": int(pain_text) if pain_text.isdigit() else None,
                "antecedentes": background.get("1.0", "end").strip(),
                "fiebre": fever.get(),
                "inflamacion": swelling.get(),
                "valoracion": current_result.valoracion,
                "prioridad": current_result.prioridad,
                "pruebas": current_result.pruebas,
                "alarmas": current_result.alarmas,
                "estado": "Pendiente",
            })
            messagebox.showinfo("Análisis guardado", f"Análisis #{analysis_id} guardado correctamente.")

        buttons = ctk.CTkFrame(form, fg_color="transparent")
        buttons.pack(fill="x", padx=22, pady=(0, 22))
        ctk.CTkButton(buttons, text="Analizar", command=analyze).pack(side="left", expand=True, fill="x", padx=(0, 6))
        ctk.CTkButton(buttons, text="Guardar análisis", command=save_analysis).pack(side="left", expand=True, fill="x", padx=(6, 0))

    # ---------------- Historial ----------------
    def show_history(self, selected_patient: str | None = None) -> None:
        page = self._page(
            "Historial IA",
            "Revisión, validación y exportación de análisis",
        )

        controls = ctk.CTkFrame(page, fg_color="transparent")
        controls.grid(row=2, column=0, sticky="ew", padx=34, pady=(0, 12))
        controls.grid_columnconfigure(2, weight=1)

        state_var = tk.StringVar(value="Todos")
        patient_var = tk.StringVar(value=selected_patient or "")

        ctk.CTkLabel(controls, text="Estado:").grid(
            row=0,
            column=0,
            padx=(0, 6),
        )
        state_combo = ctk.CTkComboBox(
            controls,
            values=["Todos", "Pendiente", "Validado", "Rechazado"],
            variable=state_var,
            width=160,
        )
        state_combo.grid(row=0, column=1, padx=(0, 12))

        search = ctk.CTkEntry(
            controls,
            textvariable=patient_var,
            placeholder_text="Buscar paciente...",
        )
        search.grid(row=0, column=2, sticky="ew")

        table_frame = ctk.CTkFrame(
            page,
            fg_color="white",
            corner_radius=12,
            border_width=1,
            border_color="#DDE5EE",
        )
        table_frame.grid(row=3, column=0, sticky="nsew", padx=34, pady=(0, 12))
        table_frame.grid_columnconfigure(0, weight=1)
        table_frame.grid_rowconfigure(0, weight=1)

        columns = ("ID", "Paciente", "Fecha", "Prioridad", "Estado")
        widths = {
            "ID": 60,
            "Paciente": 260,
            "Fecha": 180,
            "Prioridad": 120,
            "Estado": 130,
        }

        tree = ttk.Treeview(
            table_frame,
            columns=columns,
            show="headings",
            style="Dental.Treeview",
        )
        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, width=widths[col], anchor="center")

        tree.tag_configure("Pendiente", background="#FFF4CC")
        tree.tag_configure("Validado", background="#DCFCE7")
        tree.tag_configure("Rechazado", background="#FEE2E2")
        tree.grid(row=0, column=0, sticky="nsew", padx=12, pady=12)

        scrollbar = ttk.Scrollbar(
            table_frame,
            orient="vertical",
            command=tree.yview,
        )
        scrollbar.grid(row=0, column=1, sticky="ns", pady=12, padx=(0, 10))
        tree.configure(yscrollcommand=scrollbar.set)

        def reload(*_args: object) -> None:
            tree.delete(*tree.get_children())
            for row in database.list_analyses(
                state_var.get(),
                patient_var.get().strip(),
            ):
                tree.insert(
                    "",
                    "end",
                    values=tuple(row),
                    tags=(row["estado"],),
                )

        def selected_id() -> int | None:
            selection = tree.selection()
            if not selection:
                messagebox.showwarning("Aviso", "Selecciona un análisis.")
                return None
            return int(tree.item(selection[0], "values")[0])

        def change_state(new_state: str) -> None:
            analysis_id = selected_id()
            if analysis_id is None:
                return
            database.update_analysis_state(analysis_id, new_state)
            reload()

        def detail() -> None:
            analysis_id = selected_id()
            if analysis_id is None:
                return

            row = database.get_analysis(analysis_id)
            if row is None:
                messagebox.showerror(
                    "Error",
                    "No se ha encontrado el análisis.",
                )
                return

            window = ctk.CTkToplevel(self)
            window.title(f"Detalle análisis #{analysis_id}")
            window.geometry("860x760")
            window.minsize(760, 620)
            window.transient(self)

            container = ctk.CTkScrollableFrame(
                window,
                fg_color="#F4F7FB",
            )
            container.pack(
                fill="both",
                expand=True,
                padx=18,
                pady=18,
            )

            header = ctk.CTkFrame(
                container,
                fg_color="white",
                corner_radius=14,
                border_width=1,
                border_color="#DDE5EE",
            )
            header.pack(fill="x", pady=(0, 14))

            ctk.CTkLabel(
                header,
                text=f"Análisis IA #{analysis_id}",
                font=("Segoe UI", 24, "bold"),
                text_color="#1F2937",
            ).pack(anchor="w", padx=20, pady=(18, 4))

            ctk.CTkLabel(
                header,
                text=f"Paciente: {row['paciente']}",
                font=("Segoe UI", 15, "bold"),
                text_color="#0F4C81",
            ).pack(anchor="w", padx=20)

            ctk.CTkLabel(
                header,
                text=f"Fecha: {row['fecha']}",
                font=("Segoe UI", 12),
                text_color="#6B7280",
            ).pack(anchor="w", padx=20, pady=(4, 14))

            badges = ctk.CTkFrame(header, fg_color="transparent")
            badges.pack(fill="x", padx=20, pady=(0, 18))

            priority_color = {
                "Urgente": ("#FEE2E2", "#991B1B"),
                "Alta": ("#FFEDD5", "#9A3412"),
                "Media": ("#FEF3C7", "#92400E"),
                "Baja": ("#DCFCE7", "#166534"),
            }.get(row["prioridad"], ("#FFF4CC", "#7A5B00"))

            state_color = {
                "Pendiente": ("#FFF4CC", "#7A5B00"),
                "Validado": ("#DCFCE7", "#166534"),
                "Rechazado": ("#FEE2E2", "#991B1B"),
            }.get(row["estado"], ("#E8F1FA", "#0F4C81"))

            ctk.CTkLabel(
                badges,
                text=f"Prioridad: {row['prioridad']}",
                fg_color=priority_color[0],
                text_color=priority_color[1],
                corner_radius=8,
                padx=12,
                pady=6,
            ).pack(side="left", padx=(0, 8))

            ctk.CTkLabel(
                badges,
                text=f"Estado: {row['estado']}",
                fg_color=state_color[0],
                text_color=state_color[1],
                corner_radius=8,
                padx=12,
                pady=6,
            ).pack(side="left")

            def section(
                title: str,
                content: object,
                alert: bool = False,
            ) -> None:
                frame = ctk.CTkFrame(
                    container,
                    fg_color="#FFF4F4" if alert else "white",
                    corner_radius=12,
                    border_width=1,
                    border_color="#F0B8B8" if alert else "#DDE5EE",
                )
                frame.pack(fill="x", pady=(0, 12))

                ctk.CTkLabel(
                    frame,
                    text=title,
                    font=("Segoe UI", 14, "bold"),
                    text_color="#A93226" if alert else "#1F2937",
                ).pack(anchor="w", padx=18, pady=(14, 6))

                ctk.CTkLabel(
                    frame,
                    text=str(content),
                    justify="left",
                    anchor="w",
                    wraplength=760,
                    text_color="#374151",
                ).pack(fill="x", padx=18, pady=(0, 14))

            section("Síntomas", row["sintomas"])
            section("Duración", row["duracion"] or "No indicada")
            section(
                "Dolor",
                row["dolor"] if row["dolor"] is not None else "No indicado",
            )
            section(
                "Antecedentes",
                row["antecedentes"] or "No indicados",
            )
            section(
                "Signos asociados",
                f"Fiebre: {'Sí' if row['fiebre'] else 'No'}\n"
                f"Inflamación: {'Sí' if row['inflamacion'] else 'No'}",
            )
            section(
                "Valoración clínica orientativa",
                row["valoracion"] or "Sin valoración",
            )
            section(
                "Pruebas sugeridas",
                row["pruebas"] or "No indicadas",
            )
            section(
                "Señales de alarma",
                row["alarmas"] or "No indicadas",
                alert=bool(row["alarmas"]),
            )

            fields = [
                ("Paciente", row["paciente"]),
                ("Fecha", row["fecha"]),
                ("Síntomas", row["sintomas"]),
                ("Duración", row["duracion"] or "No indicada"),
                (
                    "Dolor",
                    row["dolor"]
                    if row["dolor"] is not None
                    else "No indicado",
                ),
                ("Antecedentes", row["antecedentes"] or "No indicados"),
                ("Fiebre", "Sí" if row["fiebre"] else "No"),
                ("Inflamación", "Sí" if row["inflamacion"] else "No"),
                ("Valoración", row["valoracion"] or "Sin valoración"),
                ("Prioridad", row["prioridad"]),
                ("Pruebas sugeridas", row["pruebas"] or "No indicadas"),
                ("Señales de alarma", row["alarmas"] or "No indicadas"),
                ("Estado", row["estado"]),
            ]

            def export_pdf() -> None:
                path = filedialog.asksaveasfilename(
                    defaultextension=".pdf",
                    filetypes=[("PDF", "*.pdf")],
                    initialfile=(
                        f"analisis_IA_{row['paciente']}_{analysis_id}.pdf"
                    ),
                )
                if not path:
                    return

                create_analysis_report(path, analysis_id, fields)
                messagebox.showinfo(
                    "PDF",
                    "Análisis exportado correctamente.",
                )

            actions = ctk.CTkFrame(container, fg_color="transparent")
            actions.pack(fill="x", pady=(4, 16))

            ctk.CTkButton(
                actions,
                text="Exportar PDF",
                command=export_pdf,
                width=150,
                height=40,
            ).pack(side="left")

            ctk.CTkButton(
                actions,
                text="Cerrar",
                command=window.destroy,
                width=120,
                height=40,
                fg_color="#6B7280",
                hover_color="#4B5563",
            ).pack(side="left", padx=10)

        state_combo.configure(command=lambda _value: reload())
        patient_var.trace_add("write", reload)
        tree.bind("<Double-1>", lambda _event: detail())
        reload()

        actions = ctk.CTkFrame(page, fg_color="transparent")
        actions.grid(row=4, column=0, sticky="w", padx=34, pady=(0, 24))

        ctk.CTkButton(
            actions,
            text="Ver detalle",
            command=detail,
            width=130,
        ).pack(side="left", padx=(0, 6))

        ctk.CTkButton(
            actions,
            text="Validar",
            command=lambda: change_state("Validado"),
            width=110,
        ).pack(side="left", padx=6)

        ctk.CTkButton(
            actions,
            text="Rechazar",
            command=lambda: change_state("Rechazado"),
            width=110,
            fg_color="#C0392B",
            hover_color="#A93226",
        ).pack(side="left", padx=6)

        ctk.CTkButton(
            actions,
            text="Pendiente",
            command=lambda: change_state("Pendiente"),
            width=110,
        ).pack(side="left", padx=6)

    # ---------------- Estadísticas ----------------
    def show_statistics(self) -> None:
        page = self._page("Estadísticas", "Indicadores actuales de la base de datos")
        stats = database.patient_stats()
        counts = database.analysis_counts()
        cards = ctk.CTkFrame(page, fg_color="transparent")
        cards.grid(row=2, column=0, sticky="new", padx=25, pady=(0, 16))
        cards.grid_columnconfigure((0, 1, 2), weight=1)
        self._stat_card(cards, 0, "Pacientes", stats["total"])
        self._stat_card(cards, 1, "Edad promedio", f"{stats['avg_age']:.1f}")
        self._stat_card(cards, 2, "Análisis totales", counts["Total"])

        details = ctk.CTkFrame(page, fg_color="white", corner_radius=14, border_width=1, border_color="#DDE5EE")
        details.grid(row=3, column=0, sticky="new", padx=34, pady=10)
        rows = [
            ("Menores de edad", stats["minors"]),
            ("Mayores de edad", stats["adults"]),
            ("Tratamiento más frecuente", stats["frequent_treatment"]),
            ("Análisis pendientes", counts["Pendiente"]),
            ("Análisis validados", counts["Validado"]),
            ("Análisis rechazados", counts["Rechazado"]),
        ]
        for label, value in rows:
            line = ctk.CTkFrame(details, fg_color="transparent")
            line.pack(fill="x", padx=24, pady=8)
            ctk.CTkLabel(line, text=label, font=("Segoe UI", 14), text_color="#374151").pack(side="left")
            ctk.CTkLabel(line, text=str(value), font=("Segoe UI", 14, "bold"), text_color="#0F4C81").pack(side="right")


def main() -> None:
    app = DentalAIApp()
    app.mainloop()


if __name__ == "__main__":
    main()
