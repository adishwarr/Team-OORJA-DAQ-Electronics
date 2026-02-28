import os
import sys
import tkinter as tk
import math
import random

# --- 1. BACKEND SELECTION ---
TEST_MODE = True

if TEST_MODE:
    print("RUNNING IN SIMULATION MODE (simulation.py)")
    try:
        import simulation as backend
    except ImportError:
        class MockBackend:
            def get_data(self):
                return {
                    'speed': random.randint(0, 100), 'rpm': random.randint(0, 5000),
                    'voltage': 72 + random.uniform(-2, 2), 'current': random.randint(10, 50),
                    'motor_temp': 45, 'bat_temp': 35, 'laps': 3, 'lat': 30.3456, 'lon': 76.3456
                }
        backend = MockBackend()
else:
    print(" RUNNING IN REAL MODE (backend.py)")
    try:
        import backend
    except ImportError:
        print(" Error: backend.py not found. Falling back to simulation.")
        import simulation as backend

# --- 2. PILLOW IMPORT ---
try:
    from PIL import Image, ImageTk
except ImportError:
    print("Warning: Pillow library not found. Logos may not render.")
    Image = None
    ImageTk = None

# --- 3. WINDOWS TCL/TK FIX ---
# Adjust this path if necessary for your specific Python installation
# base_path = r"C:\Users\abhin\AppData\Local\Programs\Python\Python313\tcl"
# if os.path.exists(base_path):
#     os.environ['TCL_LIBRARY'] = os.path.join(base_path, 'tcl8.6')
#     os.environ['TK_LIBRARY'] = os.path.join(base_path, 'tk8.6')

# --- 4. COLOR PALETTE ---
COL_BG       = "#111111"
COL_FACE     = "#000000"
COL_YELLOW   = "#f1c40f"  
COL_ORANGE   = "#e67e22"  
COL_RED      = "#e74c3c"  
COL_CYAN     = "#55C3D0"  
COL_WHITE    = "#FFFFFF"  
COL_OFFWHITE = "#ECF0F1"  
COL_GREEN    = "#2ecc71"
COL_PURPLE   = "#9b59b6"
COL_SHADOW   = "#000000"

# --- 5. GAUGE WIDGET CLASS ---
class RacingGauge(tk.Canvas):
    def __init__(self, parent, width=300, height=300, min_val=0, max_val=100, 
                 major_step=10, minor_step=1, title="SPEED", unit="KM/H", 
                 danger_on_low=False): 
        super().__init__(parent, width=width, height=height, bg=COL_BG, highlightthickness=0)
        self.width = width
        self.height = height
        self.center_x = width // 2
        self.center_y = height // 2
        self.radius = min(width, height) // 2 - 25
        
        self.min_val = min_val
        self.max_val = max_val
        self.major_step = major_step
        self.minor_step = minor_step
        self.title = title
        self.unit = unit
        self.danger_on_low = danger_on_low 
        
        self.draw_static_face()
        self.draw_needle(min_val)

    def draw_3d_text(self, x, y, text, font, fill, shadow_offset=2):
        self.create_text(x + shadow_offset, y + shadow_offset, text=text, 
                         fill=COL_SHADOW, font=font)
        self.create_text(x, y, text=text, fill=fill, font=font)

    def draw_static_face(self):
        self.create_oval(self.center_x - self.radius - 5, self.center_y - self.radius - 5,
                         self.center_x + self.radius + 5, self.center_y + self.radius + 5,
                         fill="#050505", outline="")
        self.create_oval(self.center_x - self.radius, self.center_y - self.radius,
                         self.center_x + self.radius, self.center_y + self.radius,
                         outline=COL_CYAN, width=8) 
        self.create_oval(self.center_x - self.radius + 4, self.center_y - self.radius + 4,
                         self.center_x + self.radius - 4, self.center_y + self.radius - 4,
                         outline="#337788", width=3) 
        self.create_oval(self.center_x - self.radius + 8, self.center_y - self.radius + 8,
                         self.center_x + self.radius - 8, self.center_y + self.radius - 8,
                         fill=COL_FACE, outline="")

        total_angle = 270
        start_angle_deg = 135
        steps = int((self.max_val - self.min_val) / self.minor_step)
        for i in range(steps + 1):
            val = self.min_val + (i * self.minor_step)
            is_major = (val % self.major_step < 0.0001) or (abs(val % self.major_step - self.major_step) < 0.0001)
            percent = (val - self.min_val) / (self.max_val - self.min_val)
            angle_deg = start_angle_deg + (percent * total_angle)
            angle_rad = math.radians(angle_deg)
            
            threshold_low = self.min_val + (self.max_val - self.min_val) * 0.2
            threshold_high = self.min_val + (self.max_val - self.min_val) * 0.8
            color = "#444444"
            if self.danger_on_low:
                if val <= threshold_low: color = COL_RED
                elif is_major: color = COL_CYAN
            else:
                if val >= threshold_high: color = COL_RED
                elif is_major: color = COL_CYAN

            if is_major:
                tick_len = 20
                width = 3
                text_rad = self.radius - 45
                x_text = self.center_x + text_rad * math.cos(angle_rad)
                y_text = self.center_y + text_rad * math.sin(angle_rad)
                self.draw_3d_text(x_text, y_text, str(int(val)), ("Segoe UI", 12, "bold"), COL_WHITE, 1)
            else:
                tick_len = 10
                width = 1

            x_out = self.center_x + (self.radius - 15) * math.cos(angle_rad)
            y_out = self.center_y + (self.radius - 15) * math.sin(angle_rad)
            x_in = self.center_x + (self.radius - 15 - tick_len) * math.cos(angle_rad)
            y_in = self.center_y + (self.radius - 15 - tick_len) * math.sin(angle_rad)
            self.create_line(x_out, y_out, x_in, y_in, fill=color, width=width)

        self.draw_3d_text(self.center_x, self.center_y - self.radius * 0.55, 
                          self.title, ("Segoe UI", 14, "bold"), COL_CYAN, 2)
        self.draw_3d_text(self.center_x, self.center_y + self.radius * 0.5, 
                          self.unit, ("Segoe UI", 10), "#aaaaaa", 1)

    def draw_needle(self, value):
        self.delete("needle")
        self.delete("readout")
        value = max(self.min_val, min(value, self.max_val))
        span = 270
        percent = (value - self.min_val) / (self.max_val - self.min_val)
        angle_deg = 135 + (percent * span)
        angle_rad = math.radians(angle_deg)
        
        needle_col = COL_CYAN 
        threshold_low = self.min_val + (self.max_val - self.min_val) * 0.2
        threshold_high = self.min_val + (self.max_val - self.min_val) * 0.8
        if self.danger_on_low:
            if value <= threshold_low: needle_col = COL_RED
        else:
            if value >= threshold_high: needle_col = COL_RED
        
        tip_len = self.radius - 20
        base_w = 8
        shadow_off = 4
        
        x_tip_s = self.center_x + shadow_off + tip_len * math.cos(angle_rad)   
        y_tip_s = self.center_y + shadow_off + tip_len * math.sin(angle_rad)
        x_base1_s = self.center_x + shadow_off + base_w * math.cos(angle_rad + math.pi/2)
        y_base1_s = self.center_y + shadow_off + base_w * math.sin(angle_rad + math.pi/2)
        x_base2_s = self.center_x + shadow_off + base_w * math.cos(angle_rad - math.pi/2)
        y_base2_s = self.center_y + shadow_off + base_w * math.sin(angle_rad - math.pi/2)
        self.create_polygon(x_tip_s, y_tip_s, x_base1_s, y_base1_s, x_base2_s, y_base2_s, 
                            fill="#000000", outline="", tags="needle") 

        x_tip = self.center_x + tip_len * math.cos(angle_rad)   
        y_tip = self.center_y + tip_len * math.sin(angle_rad)
        x_base1 = self.center_x + base_w * math.cos(angle_rad + math.pi/2)
        y_base1 = self.center_y + base_w * math.sin(angle_rad + math.pi/2)
        x_base2 = self.center_x + base_w * math.cos(angle_rad - math.pi/2)
        y_base2 = self.center_y + base_w * math.sin(angle_rad - math.pi/2)
        self.create_polygon(x_tip, y_tip, x_base1, y_base1, x_base2, y_base2, 
                            fill=needle_col, outline=needle_col, tags="needle")
        self.create_oval(self.center_x - 12, self.center_y - 12,
                         self.center_x + 12, self.center_y + 12,
                         fill="#222222", outline=needle_col, width=2, tags="needle")

        display_val = f"{value:.1f}" if self.max_val <= 10 else f"{int(value)}"
        self.create_text(self.center_x + 2, self.center_y + 42, 
                         text=display_val, fill="#000000", 
                         font=("Consolas", 26, "bold"), tags="readout")
        self.create_text(self.center_x, self.center_y + 40, 
                         text=display_val, fill=needle_col, 
                         font=("Consolas", 26, "bold"), tags="readout")

# --- 6. BAR WIDGET CLASS ---
class StatBar(tk.Frame):
    def __init__(self, parent, label, min_val, max_val, unit, color):
        super().__init__(parent, bg=COL_BG)
        self.min_val = min_val
        self.max_val = max_val
        self.unit = unit
        self.color = color
        self.bar_width = 250  
        self.top_frame = tk.Frame(self, bg=COL_BG)
        self.top_frame.pack(side="top", fill="x")
        self.lbl = tk.Label(self.top_frame, text=f"{label}", fg=COL_WHITE, bg=COL_BG, font=("Consolas", 10, "bold"))
        self.lbl.pack(side="left")
        self.val_lbl = tk.Label(self.top_frame, text="0.0", fg=color, bg=COL_BG, font=("Consolas", 10, "bold"))
        self.val_lbl.pack(side="right")
        self.canvas = tk.Canvas(self, width=self.bar_width, height=15, bg="#000000", highlightthickness=1, highlightbackground=COL_OFFWHITE)
        self.canvas.pack(side="top", pady=(2, 0))
        self.canvas.create_rectangle(0, 0, self.bar_width, 15, fill="#1a1a1a", outline="")
        self.bar = self.canvas.create_rectangle(0, 0, 0, 15, fill=color, outline="")

    def update_bar(self, value):
        percent = (value - self.min_val) / (self.max_val - self.min_val)
        percent = max(0, min(1, percent))
        self.canvas.coords(self.bar, 0, 0, int(percent * self.bar_width), 15)
        self.val_lbl.config(text=f"{value:.1f} {self.unit}")

# --- 7. ANIMATED BACKGROUND CLASS ---
class AnimatedBackground(tk.Canvas):
    def __init__(self, master, color_base="#003333", count=60):
        super().__init__(master, bg=COL_BG, highlightthickness=0)
        self.streaks = [] 
        self.count = count
        self.color_base = color_base
        self.current_speed_val = 0
        self.width = 1600
        self.height = 900
        self.bind("<Configure>", self._on_resize)
        for _ in range(self.count):
            self._add_streak(initial=True)
        self._animate()

    def _on_resize(self, event):
        self.width = event.width
        self.height = event.height

    def _add_streak(self, initial=False):
        w = random.randint(50, 200)
        h = random.randint(1, 3)
        x = random.randint(0, self.width) if initial else -w - random.randint(0, 200)
        y = random.randint(0, self.height)
        speed_factor = random.uniform(0.5, 2.0)
        line_id = self.create_line(x, y, x + w, y, fill=self.color_base, width=h, tags="streak")
        self.streaks.append([line_id, speed_factor, w, y])

    def set_speed(self, speed):
        self.current_speed_val = max(0, min(100, speed))

    def _get_color(self, speed_norm):
        if speed_norm > 0.8: return "#55FFFF"
        if speed_norm > 0.5: return "#008888"
        return "#003333"

    def _animate(self):
        norm_speed = self.current_speed_val / 100.0
        global_speed = 2 + (norm_speed * 40) 
        color = self._get_color(norm_speed)
        
        for s in self.streaks:
            line_id, factor, w, y = s
            move_x = global_speed * factor
            self.move(line_id, move_x, 0)
            coords = self.coords(line_id)
            if not coords: continue
            
            if coords[0] > self.width:
                new_w = random.randint(50, 200) + (norm_speed * 100)
                new_y = random.randint(0, self.height)
                new_x = -new_w - random.randint(0, 300)
                self.coords(line_id, new_x, new_y, new_x + new_w, new_y)
                self.itemconfig(line_id, fill=color)
                s[2] = new_w; s[3] = new_y
            else:
                self.itemconfig(line_id, fill=color)
        self.after(20, self._animate)
        

# --- 8. MAIN DASHBOARD APP ---
class RacingDash:
    def __init__(self, root):
        self.root = root
        self.root.title("Dashboard") 
        self.root.configure(bg=COL_BG)

        # --- HEADER ---
        self.header_frame = tk.Frame(root, bg=COL_BG, pady=10, height=100)
        self.header_frame.pack(side="top", fill="x", padx=20)
        self.header_frame.pack_propagate(False)

        self.logo_frame = tk.Frame(self.header_frame, bg=COL_BG, width=200)
        self.logo_frame.pack(side="left", fill="y")
        try:
            image_path = "dashboard\\frontend\\components\\team_oorja_b-removebg-preview.png"
            if Image and os.path.exists(image_path):
                raw_img = Image.open(image_path)
                target_h = 180
                aspect = raw_img.width / raw_img.height
                target_w = int(target_h * aspect)
                resized_img = raw_img.resize((target_w, target_h), Image.Resampling.LANCZOS)
                self.logo_photo = ImageTk.PhotoImage(resized_img)
                logo_lbl = tk.Label(self.logo_frame, image=self.logo_photo, bg=COL_BG)
                logo_lbl.pack(side="left", anchor="w")
        except Exception as e:
            print(f"Error loading logo: {e}")

        # 1. LAP BOX (Updated Color)
        self.lap_frame_outer = tk.Frame(self.header_frame, bg=COL_BG, width=200)
        self.lap_frame_outer.pack(side="right", fill="y")
        self.lap_box = tk.Frame(self.lap_frame_outer, bg="#000000", 
                                highlightbackground=COL_CYAN, highlightthickness=2, 
                                padx=15, pady=2)
        self.lap_box.pack(side="right", anchor="e")
        tk.Label(self.lap_box, text="LAP", fg="#888", bg="#000000", font=("Segoe UI", 10, "bold")).pack(side="left", padx=(0, 10))
        self.lap_val_lbl = tk.Label(self.lap_box, text="0", fg=COL_CYAN, bg="#000000", font=("Impact", 32))
        self.lap_val_lbl.pack(side="left")

        self.title_container = tk.Frame(self.header_frame, bg=COL_BG)
        self.title_container.place(relx=0.5, rely=0.0, anchor="n")
        title_txt = "TEAM OORJA TELEMETRY"
        self.title_lbl_s = tk.Label(self.title_container, text=title_txt, fg="#222222", bg=COL_BG, font=("Impact", 36))
        self.title_lbl_s.pack()
        self.title_lbl = tk.Label(self.title_container, text=title_txt, fg=COL_OFFWHITE, bg=COL_BG, font=("Impact", 36))
        self.title_lbl.place(x=-2, y=-2)

        # 2. SYSTEM LOADS (Updated Colors: Off-White Text & Boundary)
        # CHANGED: fg=COL_OFFWHITE (was COL_CYAN) to match the boundary
        self.power_frame = tk.LabelFrame(root, text="SYSTEM LOADS", fg=COL_OFFWHITE, bg=COL_BG, font=("Arial", 11, "bold"), 
                                         padx=10, pady=5, 
                                         highlightthickness=1, highlightbackground=COL_OFFWHITE) 
        self.power_frame.pack(side="top", fill="x", padx=20, pady=5)
        
        self.bar_v = StatBar(self.power_frame, "Voltage", 60, 90, "V", COL_WHITE)
        self.bar_v.pack(side="left", expand=True, padx=5)
        self.bar_a = StatBar(self.power_frame, "Current", 0, 100, "A", COL_YELLOW)
        self.bar_a.pack(side="left", expand=True, padx=5)
        self.bar_w = StatBar(self.power_frame, "Power", 0, 5000, "W", COL_ORANGE)
        self.bar_w.pack(side="left", expand=True, padx=5)
        self.bar_mt = StatBar(self.power_frame, "Motor Temp", 20, 120, "°C", COL_RED)
        self.bar_mt.pack(side="left", expand=True, padx=5)
        self.bar_bt = StatBar(self.power_frame, "Batt Temp", 20, 90, "°C", COL_PURPLE)
        self.bar_bt.pack(side="left", expand=True, padx=5)

        # --- CENTER CONTAINER ---
        self.center_container = tk.Frame(root, bg=COL_BG)
        self.center_container.pack(expand=True, fill="both")

        # Background Animation
        self.bg_anim = AnimatedBackground(self.center_container)
        self.bg_anim.place(x=0, y=0, relwidth=1, relheight=1)

        # Gauges
        self.dial_frame = tk.Frame(self.center_container, bg=COL_BG)
        self.dial_frame.place(relx=0.5, rely=0.5, anchor="center")
        
        tk.Misc.lower(self.bg_anim)

        self.rpm_gauge = RacingGauge(self.dial_frame, width=360, height=360, 
                                     min_val=0, max_val=5, major_step=1, minor_step=0.1,
                                     title="RPM", unit="x1000", danger_on_low=False)
        self.rpm_gauge.grid(row=0, column=0, padx=15) 

        self.speed_gauge = RacingGauge(self.dial_frame, width=480, height=480, 
                                       min_val=0, max_val=100, major_step=10, minor_step=2,
                                       title="SPEED", unit="KM/H", danger_on_low=False)
        self.speed_gauge.grid(row=0, column=1, padx=15)

        self.soc_gauge = RacingGauge(self.dial_frame, width=360, height=360, 
                                     min_val=0, max_val=100, major_step=10, minor_step=5,
                                     title="BATTERY", unit="SOC %", danger_on_low=True)
        self.soc_gauge.grid(row=0, column=2, padx=15)

        # --- FOOTER ---
        self.bottom_frame = tk.Frame(root, bg=COL_BG)
        self.bottom_frame.pack(side="bottom", fill="x", padx=20, pady=10)

        # 3. GPS CONTAINER (Updated Color)
        self.gps_container = tk.Frame(self.bottom_frame, bg="#000000", padx=15, pady=8, 
                                      highlightbackground=COL_CYAN, highlightthickness=2)
        self.gps_container.pack(side="left", padx=10)

        self.gps_tag = tk.Label(self.gps_container, text="GPS ", fg=COL_CYAN, bg="#000000", 
                               font=("Consolas", 16, "bold"))
        self.gps_tag.pack(side="left")

        self.gps_val = tk.Label(self.gps_container, text="WAITING FOR SIGNAL...", fg=COL_WHITE, 
                               bg="#000000", font=("Consolas", 16))
        self.gps_val.pack(side="left", padx=(5, 0))

        self.status_lbl = tk.Label(self.bottom_frame, text="DISCONNECTED", fg="black", bg=COL_RED, 
                                  font=("Segoe UI", 10, "bold"), padx=15)
        self.status_lbl.pack(side="right", padx=10)

        # --- BACKEND ---
        try:
            self.telemetry = backend.TelemetryHandler(port='COM3') 
        except AttributeError:
             self.telemetry = backend
        
        # --- MANUAL LAP CONTROL SETUP ---
        self.manual_lap = 0  # Initialize lap counter to 0

        # Bind Key Events for Lap Control
        self.root.bind('=', self.increase_lap)       # Standard '+' key (usually shares key with =)
        self.root.bind('<plus>', self.increase_lap)  # Numpad '+' (sometimes)
        self.root.bind('<KP_Add>', self.increase_lap)# Numpad '+' explicit

        self.root.bind('-', self.decrease_lap)           # Standard '-' key
        self.root.bind('<minus>', self.decrease_lap)     # Numpad '-' (sometimes)
        self.root.bind('<KP_Subtract>', self.decrease_lap)# Numpad '-' explicit

        self.update_telemetry()

    def increase_lap(self, event=None):
        self.manual_lap += 1
        # Quick flash effect to show input was registered
        self.lap_val_lbl.config(fg=COL_WHITE)
        self.root.after(100, lambda: self.lap_val_lbl.config(fg=COL_CYAN))

    def decrease_lap(self, event=None):
        # THIS CHECK ENSURES WE CAN GO TO 0, BUT NOT -1
        if self.manual_lap > 0: 
            self.manual_lap -= 1
            # Quick flash effect (Red for decrease warning)
            self.lap_val_lbl.config(fg=COL_RED)
            self.root.after(100, lambda: self.lap_val_lbl.config(fg=COL_CYAN))

    def update_telemetry(self):
        data = self.telemetry.get_data()

        if data:
            speed_val = float(data.get('speed', 0))
            self.speed_gauge.draw_needle(speed_val)
            self.rpm_gauge.draw_needle(float(data.get('rpm', 0)) / 1000.0)
            
            # Update Background
            self.bg_anim.set_speed(speed_val)
            
            volts = float(data.get('voltage', 0))
            soc_est = max(0, min(100, (volts - 60.0) / (84.0 - 60.0) * 100))
            self.soc_gauge.draw_needle(soc_est)

            self.bar_v.update_bar(volts)
            self.bar_a.update_bar(float(data.get('current', 0)))
            
            power_watts = volts * float(data.get('current', 0))
            self.bar_w.update_bar(power_watts)
            
            self.bar_mt.update_bar(float(data.get('motor_temp', 0)))
            self.bar_bt.update_bar(float(data.get('bat_temp', 0)))

            # --- UPDATED LAP LOGIC ---
            # We now use the manual counter instead of backend data
            self.lap_val_lbl.config(text=str(self.manual_lap))

            try:
                lat = float(data.get('lat', 0))
                lon = float(data.get('lon', 0))
                self.gps_val.config(text=f"{lat:.4f}, {lon:.4f}")
            except (ValueError, TypeError):
                self.gps_val.config(text=f"{data.get('lat')}, {data.get('lon')}")

            self.status_lbl.config(text="CONNECTED", bg=COL_GREEN)
        
        self.root.after(50, self.update_telemetry)

if __name__ == "__main__":
    root = tk.Tk()
    root.geometry("1600x950") 
    app = RacingDash(root)
    root.mainloop()
