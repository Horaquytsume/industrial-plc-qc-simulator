import random
import tkinter as tk


# Limites de aceitação da inspeção de qualidade.
WEIGHT_MIN_G = 9.5
WEIGHT_MAX_G = 10.8
LENGTH_MIN_MM = 40.0
LENGTH_MAX_MM = 44.0


class IndustrialPLCQCApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Industrial Automation & QC Sorting Cell (PLC Simulator)")
        self.root.geometry("1050x700")
        self.root.config(bg="#0f172a")

        # Entradas e saídas simuladas do PLC.
        self.inputs = {
            "start_btn": False,
            "stop_btn": False,
            "estop_ok": True,
            "force_defective_next": False,
        }
        self.outputs = {
            "conveyor_motor": False,
            "press_solenoid": False,
            "reject_gate": False,
            "robot_sorting": False,
            "indicator_error": False,
        }

        self.plc_state = "IDLE"
        self.stop_requested = False
        self.total_count = 0
        self.accepted_count = 0
        self.rejected_count = 0
        self.step_timer = 0

        # Propriedades da peça atual.
        self.part_x = 50.0
        self.part_y = 134.0
        self.sort_start_x = self.part_x
        self.sort_start_y = self.part_y
        self.current_weight = 10.2
        self.current_length = 42.0
        self.qc_result = None

        self.create_ui()
        self.update_hmi()
        self.run_plc_scan()

    def create_ui(self):
        header = tk.Label(
            self.root,
            text="INDUSTRIAL AUTOMATION & QC SORTING CELL (SCADA / PLC)",
            font=("Arial", 14, "bold"),
            bg="#0f172a",
            fg="#38bdf8",
        )
        header.pack(pady=10)

        main_container = tk.Frame(self.root, bg="#0f172a")
        main_container.pack(fill=tk.BOTH, expand=True, padx=15, pady=5)

        # Coluna esquerda: planta virtual e controles.
        left_frame = tk.Frame(main_container, bg="#0f172a")
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5)

        canvas_container = tk.LabelFrame(
            left_frame,
            text=" Integrated Production & Quality Control Line ",
            bg="#1e293b",
            fg="#cbd5e1",
            font=("Arial", 10, "bold"),
        )
        canvas_container.pack(fill=tk.BOTH, expand=True, pady=5)

        self.canvas = tk.Canvas(
            canvas_container,
            width=580,
            height=240,
            bg="#020617",
            highlightthickness=0,
        )
        self.canvas.pack(padx=10, pady=10)
        self.draw_plant_graphics()

        ctrl_frame = tk.LabelFrame(
            left_frame,
            text=" Operator Station & Inputs ",
            bg="#1e293b",
            fg="#cbd5e1",
            font=("Arial", 10, "bold"),
        )
        ctrl_frame.pack(fill=tk.X, pady=5)

        self.btn_start = tk.Button(
            ctrl_frame,
            text="START",
            bg="#059669",
            fg="white",
            font=("Arial", 10, "bold"),
            command=lambda: self.trigger_btn("start"),
            width=12,
            relief=tk.FLAT,
        )
        self.btn_start.grid(row=0, column=0, padx=8, pady=10)

        self.btn_stop = tk.Button(
            ctrl_frame,
            text="STOP",
            bg="#e11d48",
            fg="white",
            font=("Arial", 10, "bold"),
            command=lambda: self.trigger_btn("stop"),
            width=12,
            relief=tk.FLAT,
        )
        self.btn_stop.grid(row=0, column=1, padx=8, pady=10)

        self.btn_estop = tk.Button(
            ctrl_frame,
            text="E-STOP: OK",
            bg="#f59e0b",
            fg="black",
            font=("Arial", 10, "bold"),
            command=self.toggle_estop,
            width=14,
            relief=tk.FLAT,
        )
        self.btn_estop.grid(row=0, column=2, padx=8, pady=10)

        self.btn_defect = tk.Button(
            ctrl_frame,
            text="Next Part: OK",
            bg="#334155",
            fg="white",
            font=("Arial", 10, "bold"),
            command=self.toggle_defective_mode,
            width=18,
            relief=tk.FLAT,
        )
        self.btn_defect.grid(row=0, column=3, padx=8, pady=10)

        # Coluna direita: diagnósticos e monitor de I/O.
        right_frame = tk.Frame(main_container, bg="#0f172a", width=350)
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, padx=5)

        qc_card = tk.LabelFrame(
            right_frame,
            text=" QC & Dimension Diagnostics ",
            bg="#1e293b",
            fg="#cbd5e1",
            font=("Arial", 10, "bold"),
        )
        qc_card.pack(fill=tk.X, pady=5)

        self.lbl_weight = tk.Label(
            qc_card,
            text="Part Weight: 10.2 g",
            bg="#1e293b",
            fg="#34d399",
            font=("Arial", 10, "bold"),
            anchor="w",
        )
        self.lbl_weight.pack(fill=tk.X, padx=10, pady=4)

        self.lbl_dim = tk.Label(
            qc_card,
            text="Dimension Length: 42.0 mm",
            bg="#1e293b",
            fg="#38bdf8",
            font=("Arial", 10, "bold"),
            anchor="w",
        )
        self.lbl_dim.pack(fill=tk.X, padx=10, pady=4)

        self.lbl_limits = tk.Label(
            qc_card,
            text=(
                f"Acceptable: {WEIGHT_MIN_G:.1f}–{WEIGHT_MAX_G:.1f} g; "
                f"{LENGTH_MIN_MM:.1f}–{LENGTH_MAX_MM:.1f} mm"
            ),
            bg="#1e293b",
            fg="#94a3b8",
            font=("Arial", 8),
            anchor="w",
        )
        self.lbl_limits.pack(fill=tk.X, padx=10, pady=3)

        self.lbl_verdict = tk.Label(
            qc_card,
            text="Inspection Result: AWAITING INSPECTION",
            bg="#1e293b",
            fg="#facc15",
            font=("Arial", 9, "bold"),
            anchor="w",
        )
        self.lbl_verdict.pack(fill=tk.X, padx=10, pady=4)

        stats_card = tk.LabelFrame(
            right_frame,
            text=" Production Counters ",
            bg="#1e293b",
            fg="#cbd5e1",
            font=("Arial", 10, "bold"),
        )
        stats_card.pack(fill=tk.X, pady=5)

        self.lbl_total = tk.Label(
            stats_card,
            text="Total Inspected: 0",
            bg="#1e293b",
            fg="white",
            font=("Arial", 9),
            anchor="w",
        )
        self.lbl_total.pack(fill=tk.X, padx=10, pady=3)

        self.lbl_accepted = tk.Label(
            stats_card,
            text="Accepted Parts: 0",
            bg="#1e293b",
            fg="#34d399",
            font=("Arial", 9),
            anchor="w",
        )
        self.lbl_accepted.pack(fill=tk.X, padx=10, pady=3)

        self.lbl_rejected = tk.Label(
            stats_card,
            text="Rejected Parts: 0",
            bg="#1e293b",
            fg="#f87171",
            font=("Arial", 9),
            anchor="w",
        )
        self.lbl_rejected.pack(fill=tk.X, padx=10, pady=3)

        self.lbl_status = tk.Label(
            stats_card,
            text="PLC State: IDLE",
            bg="#1e293b",
            fg="#f59e0b",
            font=("Arial", 10, "bold"),
            anchor="w",
        )
        self.lbl_status.pack(fill=tk.X, padx=10, pady=6)

        io_card = tk.LabelFrame(
            right_frame,
            text=" Digital I/O Status ",
            bg="#1e293b",
            fg="#cbd5e1",
            font=("Arial", 10, "bold"),
        )
        io_card.pack(fill=tk.BOTH, expand=True, pady=5)

        self.io_labels = {}
        io_items = [
            "DI_START",
            "DI_STOP",
            "DI_ESTOP_OK",
            "DI_QC_SENSOR",
            "DO_CONV_MOTOR",
            "DO_PRESS",
            "DO_REJECT_GATE",
            "DO_ROBOT_SORT",
            "DO_ERROR",
        ]
        for item in io_items:
            row = tk.Frame(io_card, bg="#1e293b")
            row.pack(fill=tk.X, padx=10, pady=2)
            tk.Label(
                row,
                text=item,
                bg="#1e293b",
                fg="#94a3b8",
                font=("Consolas", 9),
                anchor="w",
            ).pack(side=tk.LEFT)
            value_label = tk.Label(
                row,
                text="OFF",
                bg="#0f172a",
                fg="#ef4444",
                font=("Consolas", 9, "bold"),
                width=6,
            )
            value_label.pack(side=tk.RIGHT)
            self.io_labels[item] = value_label

    def draw_plant_graphics(self):
        self.canvas.create_rectangle(
            30, 160, 530, 175, fill="#334155", outline="#475569"
        )

        # Prensa pneumática.
        self.canvas.create_rectangle(
            140, 50, 200, 110, fill="#475569", outline="#64748b"
        )
        self.canvas.create_text(
            170, 80, text="PRESS", fill="#cbd5e1", font=("Arial", 8, "bold")
        )
        self.press_rod = self.canvas.create_rectangle(
            165, 110, 175, 135, fill="#94a3b8", outline=""
        )
        self.press_head = self.canvas.create_rectangle(
            150, 135, 190, 145, fill="#64748b", outline=""
        )

        # Estação de inspeção.
        self.canvas.create_rectangle(
            270, 100, 325, 165, fill="#0f172a", outline="#0ea5e9", width=2
        )
        self.canvas.create_text(
            297, 118, text="QC SCAN", fill="#38bdf8", font=("Arial", 7, "bold")
        )
        self.qc_status_text = self.canvas.create_text(
            297, 145, text="READY", fill="#facc15", font=("Consolas", 7)
        )

        # Peça em movimento.
        self.part_box = self.canvas.create_rectangle(
            0, 0, 36, 26, fill="#f59e0b", outline="#d97706"
        )
        self.part_label = self.canvas.create_text(
            18, 13, text="PART", fill="#ffffff", font=("Arial", 7, "bold")
        )
        self.update_part_coords(self.part_x, self.part_y)

        # Portão de rejeição e caixas de destino.
        self.reject_gate = self.canvas.create_rectangle(
            370, 120, 382, 160, fill="#ef4444", outline=""
        )
        self.canvas.create_rectangle(
            420, 185, 475, 220, fill="#065f46", outline="#10b981"
        )
        self.canvas.create_text(
            447, 202, text="ACCEPTED", fill="#a7f3d0", font=("Arial", 7, "bold")
        )
        self.canvas.create_rectangle(
            485, 185, 540, 220, fill="#7f1d1d", outline="#ef4444"
        )
        self.canvas.create_text(
            512, 202, text="REJECTED", fill="#fecaca", font=("Arial", 7, "bold")
        )

        # Braço robótico: posição neutra e base.
        self.robot_base = self.canvas.create_rectangle(
            450, 140, 480, 160, fill="#334155", outline=""
        )
        self.robot_arm = self.canvas.create_line(
            465, 140, 450, 100, fill="#cbd5e1", width=4
        )

    def update_part_coords(self, x, y):
        self.canvas.coords(self.part_box, x, y, x + 36, y + 26)
        self.canvas.coords(self.part_label, x + 18, y + 13)

    def trigger_btn(self, name):
        input_name = "start_btn" if name == "start" else "stop_btn"
        self.inputs[input_name] = True
        self.root.after(200, lambda: self.inputs.update({input_name: False}))

    def toggle_estop(self):
        self.inputs["estop_ok"] = not self.inputs["estop_ok"]
        if self.inputs["estop_ok"]:
            self.btn_estop.config(text="E-STOP: OK", bg="#f59e0b", fg="black")
        else:
            self.btn_estop.config(text="TRIPPED!", bg="#dc2626", fg="white")

    def toggle_defective_mode(self):
        # Cada acionamento agenda, no máximo, uma peça defeituosa.
        self.inputs["force_defective_next"] = not self.inputs["force_defective_next"]
        if self.inputs["force_defective_next"]:
            self.btn_defect.config(
                text="Next Part: DEFECTIVE", bg="#881337", fg="#fecaca"
            )
        else:
            self.btn_defect.config(text="Next Part: OK", bg="#334155", fg="white")

    def all_outputs_off(self):
        for output_name in self.outputs:
            self.outputs[output_name] = False

    def evaluate_part(self):
        return (
            WEIGHT_MIN_G <= self.current_weight <= WEIGHT_MAX_G
            and LENGTH_MIN_MM <= self.current_length <= LENGTH_MAX_MM
        )

    def finish_sorting(self):
        self.outputs["reject_gate"] = False
        self.outputs["robot_sorting"] = False
        self.step_timer = 0

        if self.stop_requested:
            self.plc_state = "IDLE"
            self.stop_requested = False
            self.outputs["conveyor_motor"] = False
        else:
            self.plc_state = "RUNNING"
            self.spawn_new_part()

    def run_plc_scan(self):
        if not self.inputs["estop_ok"]:
            self.plc_state = "ERROR"
            self.stop_requested = False
            self.all_outputs_off()
            self.outputs["indicator_error"] = True
        elif self.plc_state == "ERROR":
            # Rearmar a emergência retorna a célula ao estado parado.
            self.plc_state = "IDLE"
            self.stop_requested = False
            self.all_outputs_off()
        elif self.plc_state == "IDLE":
            self.all_outputs_off()
            if self.inputs["start_btn"]:
                self.plc_state = "RUNNING"
                self.spawn_new_part()
        elif self.plc_state == "RUNNING":
            self.outputs["indicator_error"] = False
            self.outputs["press_solenoid"] = False
            self.outputs["reject_gate"] = False
            self.outputs["robot_sorting"] = False

            if self.inputs["stop_btn"] or self.stop_requested:
                # Em movimento entre peças, a esteira para imediatamente.
                self.outputs["conveyor_motor"] = False
                self.plc_state = "IDLE"
                self.stop_requested = False
            elif 125 <= self.part_x <= 135:
                self.outputs["conveyor_motor"] = False
                self.plc_state = "PRESSING"
                self.step_timer = 0
            else:
                self.outputs["conveyor_motor"] = True
        elif self.plc_state == "PRESSING":
            self.outputs["conveyor_motor"] = False
            self.outputs["press_solenoid"] = True
            if self.inputs["stop_btn"]:
                self.stop_requested = True

            self.step_timer += 1
            if self.step_timer > 15:
                self.outputs["press_solenoid"] = False
                self.plc_state = "QC_INSPECTING"
                self.step_timer = 0
        elif self.plc_state == "QC_INSPECTING":
            self.outputs["press_solenoid"] = False
            if self.inputs["stop_btn"]:
                self.stop_requested = True

            if 255 <= self.part_x <= 265:
                self.outputs["conveyor_motor"] = False
                self.step_timer += 1
                if self.step_timer > 20:
                    self.qc_result = self.evaluate_part()
                    self.total_count += 1
                    self.sort_start_x = self.part_x
                    self.sort_start_y = self.part_y
                    self.step_timer = 0

                    if self.qc_result:
                        self.accepted_count += 1
                        self.plc_state = "ROBOT_SORTING"
                    else:
                        self.rejected_count += 1
                        self.plc_state = "REJECTING"
            else:
                self.outputs["conveyor_motor"] = True
        elif self.plc_state in ("REJECTING", "ROBOT_SORTING"):
            self.outputs["conveyor_motor"] = False
            self.outputs["press_solenoid"] = False
            self.outputs["reject_gate"] = self.plc_state == "REJECTING"
            self.outputs["robot_sorting"] = self.plc_state == "ROBOT_SORTING"
            if self.inputs["stop_btn"]:
                # Completa a classificação da peça atual antes de parar.
                self.stop_requested = True

            self.step_timer += 1
            if self.step_timer >= 20:
                self.finish_sorting()

        self.update_hmi()
        self.root.after(50, self.run_plc_scan)

    def spawn_new_part(self):
        self.part_x = 50.0
        self.part_y = 134.0
        self.qc_result = None

        force_defective = self.inputs["force_defective_next"]
        self.inputs["force_defective_next"] = False
        self.btn_defect.config(text="Next Part: OK", bg="#334155", fg="white")

        if force_defective:
            # Uma dimensão fora da tolerância já reprova a peça.
            if random.choice((True, False)):
                self.current_weight = round(random.uniform(7.2, 8.7), 1)
                self.current_length = round(random.uniform(40.2, 43.8), 1)
            else:
                self.current_weight = round(random.uniform(9.7, 10.6), 1)
                self.current_length = round(random.uniform(35.5, 38.5), 1)
        else:
            self.current_weight = round(random.uniform(10.1, 10.7), 1)
            self.current_length = round(random.uniform(41.8, 42.4), 1)

    def update_hmi(self):
        self.lbl_weight.config(text=f"Part Weight: {self.current_weight:.1f} g")
        self.lbl_dim.config(text=f"Dimension Length: {self.current_length:.1f} mm")
        self.lbl_total.config(text=f"Total Inspected: {self.total_count}")
        self.lbl_accepted.config(text=f"Accepted Parts: {self.accepted_count}")
        self.lbl_rejected.config(text=f"Rejected Parts: {self.rejected_count}")

        state_text = self.plc_state
        if self.stop_requested and self.plc_state not in ("IDLE", "ERROR"):
            state_text = "STOPPING AFTER PART"
        self.lbl_status.config(text=f"PLC State: {state_text}")

        if self.qc_result is None:
            verdict = "Inspection Result: AWAITING INSPECTION"
            verdict_color = "#facc15"
            qc_text = "INSPECT"
            qc_color = "#facc15"
        elif self.qc_result:
            verdict = "Inspection Result: PASSED (OK)"
            verdict_color = "#34d399"
            qc_text = "PASS"
            qc_color = "#34d399"
        else:
            verdict = "Inspection Result: REJECTED (FAIL)"
            verdict_color = "#f87171"
            qc_text = "FAIL"
            qc_color = "#f87171"
        self.lbl_verdict.config(text=verdict, fg=verdict_color)
        self.canvas.itemconfigure(self.qc_status_text, text=qc_text, fill=qc_color)

        # Movimento da esteira ou transferência da peça para sua caixa.
        if self.plc_state in ("REJECTING", "ROBOT_SORTING"):
            progress = min(self.step_timer / 20.0, 1.0)
            target_x = 495.0 if self.plc_state == "REJECTING" else 430.0
            target_y = 185.0
            self.part_x = self.sort_start_x + (target_x - self.sort_start_x) * progress
            self.part_y = self.sort_start_y + (target_y - self.sort_start_y) * progress
        elif self.outputs["conveyor_motor"]:
            self.part_x += 3
            self.part_y = 134.0

        self.update_part_coords(self.part_x, self.part_y)

        # Animação simples do braço robótico e do portão de rejeição.
        if self.outputs["robot_sorting"]:
            self.canvas.coords(
                self.robot_arm,
                465,
                140,
                self.part_x + 18,
                self.part_y + 13,
            )
        else:
            self.canvas.coords(self.robot_arm, 465, 140, 450, 100)

        if self.outputs["reject_gate"]:
            self.canvas.coords(self.reject_gate, 370, 145, 382, 185)
        else:
            self.canvas.coords(self.reject_gate, 370, 120, 382, 160)

        if self.outputs["press_solenoid"]:
            self.canvas.coords(self.press_rod, 165, 110, 175, 145)
            self.canvas.coords(self.press_head, 150, 145, 190, 155)
        else:
            self.canvas.coords(self.press_rod, 165, 110, 175, 135)
            self.canvas.coords(self.press_head, 150, 135, 190, 145)

        io_states = {
            "DI_START": self.inputs["start_btn"],
            "DI_STOP": self.inputs["stop_btn"],
            "DI_ESTOP_OK": self.inputs["estop_ok"],
            "DI_QC_SENSOR": 255 <= self.part_x <= 265,
            "DO_CONV_MOTOR": self.outputs["conveyor_motor"],
            "DO_PRESS": self.outputs["press_solenoid"],
            "DO_REJECT_GATE": self.outputs["reject_gate"],
            "DO_ROBOT_SORT": self.outputs["robot_sorting"],
            "DO_ERROR": self.outputs["indicator_error"],
        }
        for key, state in io_states.items():
            label = self.io_labels[key]
            if state:
                label.config(text="ON", bg="#065f46", fg="#34d399")
            else:
                label.config(text="OFF", bg="#0f172a", fg="#ef4444")


if __name__ == "__main__":
    root = tk.Tk()
    app = IndustrialPLCQCApp(root)
    root.mainloop()
