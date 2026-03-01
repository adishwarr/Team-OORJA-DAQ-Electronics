import math
from PyQt6.QtWidgets import QWidget
from PyQt6.QtGui import QPainter, QColor, QPen, QPolygonF, QRadialGradient, QBrush, QFont, QConicalGradient
from PyQt6.QtCore import Qt, QPointF, QRectF

class AnalogueGauge(QWidget):
    def __init__(self, title="GAUGE", min_val=0, max_val=100, units=""):
        super().__init__()
        self.title = title
        self.min_val = min_val
        self.max_val = max_val
        self.units = units
        self.current_value = min_val
        
        # Design Config
        self.accent_color = QColor(0, 200, 255)  # Cyan/Blue
        self.warning_color = QColor(255, 50, 50) # Red
        self.text_color = QColor(220, 220, 220)  # Off-white
        
        self.setMinimumSize(250, 250)

    def update_value(self, value):
        # Clamp value
        self.current_value = max(self.min_val, min(value, self.max_val))
        self.update()  # Triggers paintEvent

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        # 1. Setup Canvas (Scale to 200x200 logical units)
        w, h = self.width(), self.height()
        painter.translate(w / 2, h / 2)
        side = min(w, h)
        scale = side / 200.0
        painter.scale(scale, scale)

        # 2. Draw Components
        self.draw_face(painter)
        self.draw_ticks_and_labels(painter)
        self.draw_needle(painter)
        self.draw_digital_readout(painter)
        self.draw_glass_reflection(painter)

    def draw_face(self, painter):
        # Dark Background Gradient
        grad = QRadialGradient(0, 0, 100)
        grad.setColorAt(0.0, QColor(40, 40, 45))
        grad.setColorAt(1.0, QColor(10, 10, 15))
        painter.setBrush(QBrush(grad))
        painter.setPen(QPen(QColor(60, 60, 65), 2))
        painter.drawEllipse(-95, -95, 190, 190)

    def draw_ticks_and_labels(self, painter):
        # Configuration for the dial arc
        start_angle = 135  # Bottom Left
        end_angle = 405    # Bottom Right (wraps past 360)
        total_angle = end_angle - start_angle
        
        # Determine tick steps based on range size
        val_range = self.max_val - self.min_val
        major_step = val_range / 10 if val_range >= 10 else 1
        
        painter.setFont(QFont("Arial", 8, QFont.Weight.Bold))

        # We iterate through values to draw ticks
        # Using a fixed number of steps for cleaner loops
        steps = 10 # 10 Major intervals
        for i in range(steps + 1):
            # Calculate value for this tick
            val = self.min_val + (i * (val_range / steps))
            
            # Calculate angle (0 to 1)
            pct = i / steps
            angle_deg = start_angle + (pct * total_angle)
            
            # 1. Draw Ticks (Rotate painter)
            painter.save()
            painter.rotate(angle_deg + 90) # Offset for standard coord system
            
            # Highlight "Redline" ticks (top 20%)
            is_redline = val > (self.max_val - (val_range * 0.2))
            tick_color = self.warning_color if is_redline else QColor(150, 150, 150)
            
            painter.setPen(QPen(tick_color, 2))
            painter.drawLine(0, -85, 0, -95) # Draw line inward from rim
            painter.restore()

            # 2. Draw Text Labels (Trigonometry)
            # We use trig so text stays upright (doesn't rotate with dial)
            angle_rad = math.radians(angle_deg + 90)
            radius = 70 # Distance from center
            x = radius * math.cos(angle_rad)
            y = radius * math.sin(angle_rad)
            
            painter.setPen(self.text_color)
            # Create a rectangle centered on calculated point
            rect = QRectF(x - 15, y - 10, 30, 20)
            
            # Format number (int if whole, float if small range)
            label_text = f"{int(val)}" if val_range >= 10 else f"{val:.1f}"
            painter.drawText(rect, Qt.AlignmentFlag.AlignCenter, label_text)

    def draw_needle(self, painter):
        painter.save()

        # Map current value to angle
        val_range = self.max_val - self.min_val
        if val_range == 0: val_range = 1 # Prevent div/0
        
        pct = (self.current_value - self.min_val) / val_range
        angle = -225 + (pct * 270) # Map 0..1 to -225..45 degrees

        painter.rotate(angle)

        # Dynamic Color: Turn red if near max
        is_warning = pct > 0.8
        color = self.warning_color if is_warning else self.accent_color

        painter.setBrush(color)
        painter.setPen(Qt.PenStyle.NoPen)

        # Needle Shape
        needle = QPolygonF([
            QPointF(-3, 0),    # Base Left
            QPointF(0, -85),   # Tip
            QPointF(3, 0)      # Base Right
        ])
        painter.drawPolygon(needle)
        
        painter.restore()
        
        # Draw Center Cap (Pivot)
        painter.setBrush(QColor(30, 30, 30))
        painter.setPen(QPen(QColor(60, 60, 60), 1))
        painter.drawEllipse(-8, -8, 16, 16)

    def draw_digital_readout(self, painter):
        # Digital Value
        painter.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        painter.setPen(self.text_color)
        
        val_str = f"{self.current_value:.1f}" if isinstance(self.current_value, float) else str(self.current_value)
        painter.drawText(QRectF(-50, 30, 100, 30), Qt.AlignmentFlag.AlignCenter, val_str)

        # Title / Units
        painter.setFont(QFont("Arial", 7))
        painter.setPen(QColor(150, 150, 150))
        label = f"{self.title} {self.units}"
        painter.drawText(QRectF(-50, 55, 100, 20), Qt.AlignmentFlag.AlignCenter, label)

    def draw_glass_reflection(self, painter):
        # Adds a subtle "shine" to the top half to simulate glass
        grad = QConicalGradient(0, 0, -45)
        grad.setColorAt(0.0, QColor(255, 255, 255, 0))
        grad.setColorAt(0.1, QColor(255, 255, 255, 15)) # Slight glare
        grad.setColorAt(0.2, QColor(255, 255, 255, 0))
        
        painter.setBrush(QBrush(grad))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawEllipse(-90, -90, 180, 180)