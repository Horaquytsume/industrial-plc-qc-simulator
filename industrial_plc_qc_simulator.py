import tkinter as tk
from tkinter import ttk
import random
import time

class IndustrialPLCQCApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Industrial Automation & QC Sorting Cell (PLC Simulator)")
        self.root.geometry("1050x700")
        self.root.config(bg="#0f172a") # Dark slate background

        # --- PLC Memory Tags & State ---
        self.inputs = {
            "start_btn": False,
            "stop_btn": False,
            "esto_btn": True,          # True = Safe (OK), False = Tripped
            "force_defective": False   # Toggle to force next part defective
        }

        self.outputs = {
            "conveyor_motor": False,
            "press_solenoid": False,
            "reject_gate": False,
            "robot_sorting": False,
            "indicator_error": False
        }

        self.plc_state = "IDLE"
        self.total_count = 0
        self.accepted_count = 0
        self.rejected_count = 0
        self.step_timer = 0
        
        # Part Physics & Inspection properties
        self.part_x = 50
        self.current_weight = 10.2
        self.current_length = 42.0
        self.current_is_defective = False

        # Build User Interface
        self.create_ui()

        # Start PLC scan loop (50ms scan time)
        self.run_plc_scan()

    def create_ui(self):
        header = tk.Label(self.root, text="INDUSTRIAL AUTOMATION & QC SORTING CELL (SCADA / PLC)", 
                          font=("Arial", 14, "bold"), bg="#0f172a", fg="#38bdf8")
        header.pack(pady=10)

        main_container = tk.Frame(self.root, bg="#0f172a")
        main_container.pack(fill=tk.BOTH, expand=True, padx=15, pady=5)

        # Left Column: Plant Canvas & Operator Controls
        left_frame = tk.Frame(main_container, bg="#0f172a")
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5)

        # Canvas for Plant Animation
        canvas_container = tk.LabelFrame(left_frame, text=" Integrated Production & Quality Control Line ", 
                                         bg="#1e293b", fg="#cbd5e1", font=("Arial", 10, "bold"))
        canvas_container.pack(fill=tk.BOTH, expand=True, pady=5)

        self.canvas = tk.Canvas(canvas_container, width=580, height=240, bg="#020617", highlightthickness=0)
        self.canvas.pack(padx=10, pady=10)
        self.draw_plant_graphics()

        # Operator Control Panel Frame
        ctrl_frame = tk.LabelFrame(left_frame, text=" Operator Station & Inputs ", 
                                   bg="#1e293b", fg="#cbd5e1", font=("Arial", 10, "bold"))
        ctrl_frame.pack(fill=tk.X, pady=5)

        # Control Buttons
        self.btn_start = tk.Button(ctrl_frame, text="START", bg="#059669", fg="white", font=("Arial", 10, "bold"),
                                   command=lambda: self.trigger_btn('start'), width=12, relief=tk.FLAT)
        self.btn_start.grid(row=0, column=0, padx=8, pady=10)

        self.btn_stop = tk.Button(ctrl_frame, text="STOP", bg="#e11d48", fg="white", font=("Arial", 10, "bold"),
                                  command=lambda: self.trigger_btn('stop'), width=12, relief=tk.FLAT)
        self.btn_stop.grid(row=0, column=1, padx=8, pady=10)

        self.btn_estop = tk.Button(ctrl_frame, text="E-STOP: OK", bg="#f59e0b", fg="black", font=("Arial", 10, "bold"),
                                   command=self.toggle_estop, width=14, relief=tk.FLAT)
        self.btn_estop.grid(row=0, column=2, padx=8, pady=10)

        self.btn_defect = tk.Button(ctrl_frame, text="Next Part: OK", bg="#334155", fg="white", font=("Arial", 10, "bold"),
                                    command=self.toggle_defective_mode, width=18, relief=tk.FLAT)
        self.btn_defect.grid(row=0, column=3, padx=8, pady=10)

        # Right Column: QC Diagnostics & I/O Table
        right_frame = tk.Frame(main_container, bg="#0f172a", width=350)
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, padx=5)

        # QC Telemetry Card
        qc_card = tk.LabelFrame(right_frame, text=" QC & Dimension Diagnostics ", 
                                bg="#1e293b", fg="#cbd5e1", font=("Arial", 10, "bold"))
        qc_card.pack(fill=tk.X, pady=5)

        self.lbl_weight = tk.Label(qc_card, text="Part Weight: 10.2 g", bg="#1e293b", fg="#34d399", font=("Arial", 10, "bold"), anchor="w")
        self.lbl_weight.pack(fill=tk.X, padx=10, pady=4)

        self.lbl_dim = tk.Label(qc_card, text="Dimension Length: 42.0 mm", bg="#1e293b", fg="#38bdf8", font=("Arial", 10, "bold"), anchor="w")
        self.lbl_dim.pack(fill=tk.X, padx=10, pady=4)

        self.lbl_verdict = tk.Label(qc_card, text="Inspection Result: PASSED (OK)", bg="#1e293b", fg="#34d399", font=("Arial", 10, "bold"), anchor="w")
        self.lbl_verdict.pack(fill=tk.X, padx=10, pady=4)

        # Counters Card
        stats_card = tk.LabelFrame(right_frame, text=" Production Counters ", 
                                   bg="#1e293b", fg="#cbd5e1", font=("Arial", 10, "bold"))
        stats_card.pack(fill=tk.X, pady=5)

        self.lbl_total = tk.Label(stats_card, text="Total Inspected: 0", bg="#1e293b", fg="white", font=("Arial", 9), anchor="w")
        self.lbl_total.pack(fill=tk.X, padx=10, pady=3)

        self.lbl_accepted = tk.Label(stats_card, text="Accepted Parts: 0", bg="#1e293b", fg="#34d399", font=("Arial", 9), anchor="w")
        self.lbl_accepted.pack(fill=tk.X, padx=10, pady=3)

        self.lbl_rejected = tk.Label(stats_card, text="Rejected Parts: 0", bg="#1e293b", fg="#f87171", font=("Arial", 9), anchor="w")
        self.lbl_rejected.pack(fill=tk.X, padx=10, pady=3)

        self.lbl_status = tk.Label(stats_card, text="PLC State: STOPPED", bg="#1e293b", fg="#f59e0b", font=("Arial", 10, "bold"), anchor="w")
        self.lbl_status.pack(fill=tk.X, padx=10, pady=6)

        # I/O Monitor Table
        io_card = tk.LabelFrame(right_frame, text=" Digital I/O Status ", 
                                bg="#1e293b", fg="#cbd5e1", font=("Arial", 10, "bold"))
        io_card.pack(fill=tk.BOTH, expand=True, pady=5)

        self.io_labels = {}
        io_items = ["DI_CONV_RUN", "DI_QC_SENSOR", "DO_REJECT_GATE", "DO_ROBOT_SORT"]
        for idx, item in enumerate(io_items):
            row_f = tk.Frame(io_card, bg="#1e293b")
            row_f.pack(fill=tk.X, padx=10, pady=3)
            tk.Label(row_f, text=item, bg="#1e293b", fg="#94a3b8", font=("Consolas", 9), anchor="w").pack(side=tk.LEFT)
            lbl_val = tk.Label(row_f, text="OFF", bg="#0f172a", fg="#ef4444", font=("Consolas", 9, "bold"), width=6)
            lbl_val.pack(side=tk.RIGHT)
            self.io_labels[item] = lbl_val

    def draw_plant_graphics(self):
        # Conveyor roller line
        self.canvas.create_rectangle(30, 160, 530, 175, fill="#334155", outline="#475569")
        
        # Pneumatic Press Station
        self.canvas.create_rectangle(140, 50, 200, 110, fill="#475569", outline="#64748b")
        self.canvas.create_text(170, 80, text="PRESS", fill="#cbd5e1", font=("Arial", 8, "bold"))
        self.press_rod = self.canvas.create_rectangle(165, 110, 175, 135, fill="#94a3b8", outline="")
        self.press_head = self.canvas.create_rectangle(150, 135, 190, 145, fill="#64748b", outline="")

        # QC Scanner Station
        self.canvas.create_rectangle(270, 100, 325, 165, fill="#0f172a", outline="#0ea5e9", width=2)
        self.canvas.create_text(297, 118, text="QC SCAN", fill="#38bdf8", font=("Arial", 7, "bold"))
        self.qc_status_text = self.canvas.create_text(297, 145, text="READY", fill="#facc15", font=("Consolas", 7))

        # Moving Part (Resistor)
        self.part_group = []
        self.part_box = self.canvas.create_rectangle(0, 0, 36, 26, fill="#f59e0b", outline="#d97706")
        self.part_label = self.canvas.create_text(18, 13, text="100Ω", fill="#ffffff", font=("Arial", 7, "bold"))
        self.update_part_coords(50, 134)

        # Rejection Gate
        self.reject_gate = self.canvas.create_rectangle(370, 120, 382, 160, fill="#ef4444", outline="")

        # Acceptance & Rejection Bins
        self.canvas.create_rectangle(420, 185, 475, 220, fill="#065f46", outline="#10b981")
        self.canvas.create_text(447, 202, text="ACCEPTED", fill="#a7f3d0", font=("Arial", 7, "bold"))

        self.canvas.create_rectangle(485, 185, 540, 220, fill="#7f1d1d", outline="#ef4444")
        self.canvas.create_text(512, 202, text="REJECTED", fill="#fecaca", font=("Arial", 7, "bold"))

        # Articulated Robot Arm
        self.robot_base = self.canvas.create_rectangle(450, 140, 480, 160, fill="#334155", outline="")
        self.robot_arm = self.canvas.create_line(465, 140, 450, 100, fill="#cbd5e1", width=4)

    def update_part_coords(self, x, y):
        self.canvas.coords(self.part_box, x, y, x + 36, y + 26)
        self.canvas.coords(self.part_label, x + 18, y + 13)

    def trigger_btn(self, name):
        if name == 'start':
            self.inputs["start_btn"] = True
            self.root.after(200, lambda: self.inputs.update({"start_btn": False}))
        elif name == 'stop':
            self.inputs["stop_btn"] = True
            self.root.after(200, lambda: self.inputs.update({"stop_btn": False}))

    def toggle_estop(self):
        self.inputs["esto_btn"] = not self.inputs["esto_btn"]
        if self.inputs["esto_btn"]:
            self.btn_estop.config(text="E-STOP: OK", bg="#f59e0b")
        else:
            self.btn_estop.config(text="TRIPPED!", bg="#dc2626", fg="white")

    def toggle_defective_mode(self):
        self.inputs["force_defective"] = not self.inputs["force_defective"]
        if self.inputs["force_defective"]:
            self.btn_defect.config(text="Next Part: DEFECTIVE", bg="#881337", fg="#fecaca")
        else:
            self.btn_defect.config(text="Next Part: OK", bg="#334155", fg="white")

    def run_plc_scan(self):
        if not self.inputs["esto_btn"]:
            self.plc_state = "ERROR"
            for out in self.outputs:
                self.outputs[out] = False
            self.outputs["indicator_error"] = True
        else:
            if self.plc_state == "IDLE":
                self.outputs["indicator_error"] = False
                self.outputs["conveyor_motor"] = False
                if self.inputs["start_btn"]:
                    self.plc_state = "RUNNING"
                    self.spawn_new_part()

            elif self.plc_state == "RUNNING":
                self.outputs["conveyor_motor"] = True
                self.outputs["press_solenoid"] = False
                self.outputs["reject_gate"] = False
                self.outputs["robot_sorting"] = False

                # Reach Press station (~130px)
                if 125 <= self.part_x <= 135:
                    self.plc_state = "PRESSING"
                    self.outputs["conveyor_motor"] = False
                    self.step_timer = 0

                if self.inputs["stop_btn"]:
                    self.plc_state = "IDLE"
                    self.outputs["conveyor_motor"] = False

            elif self.plc_state == "PRESSING":
                self.outputs["press_solenoid"] = True
                self.step_timer += 1
                if self.step_timer > 15:
                    self.plc_state = "QC_INSPECTING"
                    self.outputs["press_solenoid"] = False
                    self.step_timer = 0

            elif self.plc_state == "QC_INSPECTING":
                self.outputs["conveyor_motor"] = True
                # Reach QC Scanner station (~260px)
                if 255 <= self.part_x <= 265:
                    self.outputs["conveyor_motor"] = False
                    self.step_timer += 1
                    if self.step_timer > 20:
                        self.total_count += 1
                        if self.current_is_defective:
                            self.rejected_count += 1
                            self.plc_state = "REJECTING"
                        else:
                            self.accepted_count += 1
                            self.plc_state = "ROBOT_SORTING"
                        self.step_timer = 0

            elif self.plc_state == "REJECTING":
                self.outputs["reject_gate"] = True
                self.step_timer += 1
                if self.step_timer > 20:
                    self.outputs["reject_gate"] = False
                    self.plc_state = "RUNNING"
                    self.step_timer = 0
                    self.spawn_new_part()

            elif self.plc_state == "ROBOT_SORTING":
                self.outputs["robot_sorting"] = True
                self.step_timer += 1
                if self.step_timer > 20:
                    self.outputs["robot_sorting"] = False
                    self.plc_state = "RUNNING"
                    self.step_timer = 0
                    self.spawn_new_part()

            elif self.plc_state == "ERROR":
                if self.inputs["esto_btn"]:
                    self.plc_state = "IDLE"

        self.update_hmi()
        self.root.after(50, self.run_plc_scan)

    def spawn_new_part(self):
        self.part_x = 50
        self.current_is_defective = self.inputs["force_defective"]
        if self.current_is_defective:
            self.current_weight = round(7.2 + random.uniform(0, 1.5), 1)
            self.current_length = round(35.5 + random.uniform(0, 3.0), 1)
        else:
            self.current_weight = round(10.1 + random.uniform(0, 0.6), 1)
            self.current_length = round(42.0 + random.uniform(0, 0.4), 1)

    def update_hmi(self):
        self.lbl_status.config(text=f"PLC State: {self.plc_state}")
        self.lbl_weight.config(text=f"Part Weight: {self.current_weight} g")
        self.lbl_dim.config(text=f"Dimension Length: {self.current_length} mm")

        if self.current_is_defective:
            self.lbl_verdict.config(text="Inspection Result: REJECTED (FAIL)", fg="#f87171")
        else:
            self.lbl_verdict.config(text="Inspection Result: PASSED (OK)", fg="#34d399")

        self.lbl_total.config(text=f"Total Inspected: {self.total_count}")
        self.lbl_accepted.config(text=f"Accepted Parts: {self.accepted_count}")
        self.lbl_rejected.config(text=f"Rejected Parts: {self.rejected_count}")

        # Conveyor part movement
        if self.outputs["conveyor_motor"]:
            self.part_x += 3
            if self.part_x > 540:
                self.spawn_new_part()
        self.update_part_coords(self.part_x, 134)

        # Pneumatic Press Animation
        if self.outputs["press_solenoid"]:
            self.canvas.coords(self.press_rod, 165, 110, 175, 145)
            self.canvas.coords(self.press_head, 150, 145, 190, 155)
        else:
            self.canvas.coords(self.press_rod, 165, 110, 175, 135)
            self.canvas.coords(self.press_head, 150, 135, 190, 145)

        # I/O Indicator Table Updates
        io_states = {
            "DI_CONV_RUN": self.outputs["conveyor_motor"],
            "DI_QC_SENSOR": (255 <= self.part_x <= 265),
            "DO_REJECT_GATE": self.outputs["reject_gate"],
            "DO_ROBOT_SORT": self.outputs["robot_sorting"]
        }

        for key, state in io_states.items():
            lbl = self.io_labels[key]
            if state:
                lbl.config(text="ON", bg="#065f46", fg="#34d399")
            else:
                lbl.config(text="OFF", bg="#0f172a", fg="#ef4444")

if __name__ == "__main__":
    root = tk.Tk()
    app = IndustrialPLCQCApp(root)
    root.mainloop()
