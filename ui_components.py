"""
Componentes UI Avanzados
Widgets personalizados, gráficos y visualizaciones
"""
import tkinter as tk
from tkinter import ttk
import math

# -------------------------
# Gráfico de Barras ASCII
# -------------------------

class BarChart(tk.Canvas):
    """Widget de gráfico de barras simple"""
    
    def __init__(self, parent, width=400, height=200, **kwargs):
        super().__init__(parent, width=width, height=height, 
                        bg=kwargs.get('bg', '#1a1a2e'), 
                        highlightthickness=0)
        self.width = width
        self.height = height
        
    def plot(self, data, labels, colors=None, title=""):
        """
        Dibuja gráfico de barras
        data: list de valores
        labels: list de etiquetas
        colors: list de colores (opcional)
        """
        self.delete("all")
        
        if not data:
            return
        
        # Título
        if title:
            self.create_text(self.width//2, 15, text=title, 
                           fill="white", font=("Segoe UI", 12, "bold"))
        
        # Configuración
        margin = 40
        bar_width = (self.width - 2*margin) / len(data) * 0.7
        max_val = max(data) if max(data) > 0 else 1
        
        # Colores por defecto
        if not colors:
            colors = ["#00d9ff"] * len(data)
        
        # Dibujar barras
        for i, (val, label, color) in enumerate(zip(data, labels, colors)):
            x = margin + i * (self.width - 2*margin) / len(data)
            bar_height = (val / max_val) * (self.height - 80)
            y_top = self.height - margin - bar_height
            y_bottom = self.height - margin
            
            # Barra
            self.create_rectangle(x, y_top, x + bar_width, y_bottom,
                                fill=color, outline="")
            
            # Valor encima
            self.create_text(x + bar_width/2, y_top - 10,
                           text=f"{val:.1f}" if isinstance(val, float) else str(val),
                           fill="white", font=("Segoe UI", 9))
            
            # Etiqueta
            self.create_text(x + bar_width/2, y_bottom + 15,
                           text=label, fill="#a0a0a0", font=("Segoe UI", 8))

# -------------------------
# Gráfico de Líneas
# -------------------------

class LineChart(tk.Canvas):
    """Widget de gráfico de líneas"""
    
    def __init__(self, parent, width=500, height=250, **kwargs):
        super().__init__(parent, width=width, height=height,
                        bg=kwargs.get('bg', '#1a1a2e'),
                        highlightthickness=0)
        self.width = width
        self.height = height
    
    def plot(self, data_points, labels=None, title="", xlabel="", ylabel="", color="#00d9ff"):
        """
        Dibuja gráfico de líneas
        data_points: list de valores [y1, y2, y3, ...]
        labels: list de etiquetas para eje X
        """
        self.delete("all")
        
        if not data_points or len(data_points) < 2:
            self.create_text(self.width//2, self.height//2,
                           text="Sin datos suficientes",
                           fill="#a0a0a0", font=("Segoe UI", 11))
            return
        
        # Márgenes
        margin_left = 50
        margin_right = 30
        margin_top = 40
        margin_bottom = 50
        
        # Título
        if title:
            self.create_text(self.width//2, 20, text=title,
                           fill="white", font=("Segoe UI", 13, "bold"))
        
        # Calcular escala
        min_val = min(data_points)
        max_val = max(data_points)
        val_range = max_val - min_val if max_val != min_val else 1
        
        chart_width = self.width - margin_left - margin_right
        chart_height = self.height - margin_top - margin_bottom
        
        # Dibujar ejes
        # Eje Y
        self.create_line(margin_left, margin_top,
                        margin_left, self.height - margin_bottom,
                        fill="#555", width=2)
        
        # Eje X
        self.create_line(margin_left, self.height - margin_bottom,
                        self.width - margin_right, self.height - margin_bottom,
                        fill="#555", width=2)
        
        # Etiquetas eje Y
        for i in range(5):
            y_pos = margin_top + (chart_height * i / 4)
            val = max_val - (val_range * i / 4)
            self.create_text(margin_left - 10, y_pos,
                           text=f"{val:.1f}", fill="#a0a0a0",
                           font=("Segoe UI", 8), anchor="e")
            # Línea de grid
            self.create_line(margin_left, y_pos,
                           self.width - margin_right, y_pos,
                           fill="#333", dash=(2, 4))
        
        # Ylabel
        if ylabel:
            # Texto vertical (aproximado con rotación manual)
            self.create_text(15, self.height//2, text=ylabel,
                           fill="#a0a0a0", font=("Segoe UI", 9))
        
        # Xlabel
        if xlabel:
            self.create_text(self.width//2, self.height - 15,
                           text=xlabel, fill="#a0a0a0", font=("Segoe UI", 9))
        
        # Calcular puntos
        points = []
        for i, val in enumerate(data_points):
            x = margin_left + (i * chart_width / (len(data_points) - 1))
            y = self.height - margin_bottom - ((val - min_val) / val_range * chart_height)
            points.append((x, y))
            
            # Dibujar punto
            self.create_oval(x-4, y-4, x+4, y+4, fill=color, outline="white", width=2)
            
            # Etiqueta X
            if labels and i < len(labels):
                self.create_text(x, self.height - margin_bottom + 15,
                               text=labels[i], fill="#a0a0a0",
                               font=("Segoe UI", 8), angle=0)
        
        # Dibujar línea
        if len(points) > 1:
            for i in range(len(points) - 1):
                self.create_line(points[i][0], points[i][1],
                               points[i+1][0], points[i+1][1],
                               fill=color, width=3, smooth=True)

# -------------------------
# Indicador Circular (Gauge)
# -------------------------

class CircularGauge(tk.Canvas):
    """Indicador circular de progreso"""
    
    def __init__(self, parent, size=150, **kwargs):
        super().__init__(parent, width=size, height=size,
                        bg=kwargs.get('bg', '#0a0a0a'),
                        highlightthickness=0)
        self.size = size
        self.center = size // 2
    
    def set_value(self, value, max_value=100, label="", color="#00d9ff"):
        """
        Dibuja indicador circular
        value: valor actual
        max_value: valor máximo
        label: texto central
        """
        self.delete("all")
        
        # Calcular porcentaje
        percent = (value / max_value * 100) if max_value > 0 else 0
        angle = (percent / 100) * 270  # 270 grados de arco
        
        radius = self.size // 2 - 15
        
        # Arco de fondo
        self.create_arc(15, 15, self.size-15, self.size-15,
                       start=135, extent=270, style="arc",
                       outline="#2e2e2e", width=15)
        
        # Arco de progreso
        self.create_arc(15, 15, self.size-15, self.size-15,
                       start=135, extent=angle, style="arc",
                       outline=color, width=15)
        
        # Texto central - porcentaje
        self.create_text(self.center, self.center - 10,
                        text=f"{percent:.0f}%",
                        fill="white", font=("Segoe UI", 20, "bold"))
        
        # Label
        if label:
            self.create_text(self.center, self.center + 20,
                           text=label, fill="#a0a0a0",
                           font=("Segoe UI", 10))

# -------------------------
# Card Component
# -------------------------

class InfoCard(tk.Frame):
    """Tarjeta de información estilizada"""
    
    def __init__(self, parent, title="", value="", subtitle="", 
                 icon="", bg_color="#1a1a2e", **kwargs):
        super().__init__(parent, bg=bg_color, bd=2, relief="solid", **kwargs)
        self.configure(padx=15, pady=15)
        
        # Icono y título
        header = tk.Frame(self, bg=bg_color)
        header.pack(fill="x")
        
        if icon:
            tk.Label(header, text=icon, bg=bg_color, fg="white",
                    font=("Segoe UI", 18)).pack(side="left", padx=(0, 8))
        
        tk.Label(header, text=title, bg=bg_color, fg="#a0a0a0",
                font=("Segoe UI", 10)).pack(side="left")
        
        # Valor principal
        tk.Label(self, text=value, bg=bg_color, fg="white",
                font=("Segoe UI", 24, "bold")).pack(pady=(10, 5))
        
        # Subtítulo
        if subtitle:
            tk.Label(self, text=subtitle, bg=bg_color, fg="#6c63ff",
                    font=("Segoe UI", 9, "italic")).pack()

# -------------------------
# Progress Bar Animado
# -------------------------

class AnimatedProgressBar(tk.Canvas):
    """Barra de progreso con animación"""
    
    def __init__(self, parent, width=300, height=30, **kwargs):
        super().__init__(parent, width=width, height=height,
                        bg=kwargs.get('bg', '#0a0a0a'),
                        highlightthickness=0)
        self.width = width
        self.height = height
        self.current_value = 0
        self.target_value = 0
    
    def set_progress(self, value, max_value=100, color="#00d9ff", label=""):
        """Establece progreso con animación"""
        self.target_value = (value / max_value) * 100 if max_value > 0 else 0
        self.animate(color, label)
    
    def animate(self, color, label):
        """Anima el progreso"""
        self.delete("all")
        
        # Fondo
        self.create_rectangle(5, 5, self.width-5, self.height-5,
                             fill="#2e2e2e", outline="")
        
        # Barra de progreso
        progress_width = (self.current_value / 100) * (self.width - 10)
        self.create_rectangle(5, 5, 5 + progress_width, self.height-5,
                             fill=color, outline="")
        
        # Texto
        self.create_text(self.width//2, self.height//2,
                        text=f"{self.current_value:.0f}% {label}",
                        fill="white", font=("Segoe UI", 10, "bold"))
        
        # Continuar animación si no llegó al objetivo
        if abs(self.current_value - self.target_value) > 0.5:
            self.current_value += (self.target_value - self.current_value) * 0.1
            self.after(30, lambda: self.animate(color, label))
        else:
            self.current_value = self.target_value

# -------------------------
# Timeline Component
# -------------------------

class Timeline(tk.Canvas):
    """Línea de tiempo para mostrar progresión"""
    
    def __init__(self, parent, width=600, height=150, **kwargs):
        super().__init__(parent, width=width, height=height,
                        bg=kwargs.get('bg', '#0a0a0a'),
                        highlightthickness=0)
        self.width = width
        self.height = height
    
    def draw_timeline(self, events):
        """
        Dibuja línea de tiempo
        events: list de dict [
            {"semana": 1, "titulo": "Inicio", "destacado": True},
            {"semana": 4, "titulo": "Deload", "destacado": False},
            ...
        ]
        """
        self.delete("all")
        
        if not events:
            return
        
        margin = 50
        timeline_y = self.height // 2
        
        # Línea principal
        self.create_line(margin, timeline_y, self.width - margin, timeline_y,
                        fill="#555", width=3)
        
        # Eventos
        max_semana = max(e["semana"] for e in events)
        
        for event in events:
            x = margin + ((event["semana"] - 1) / max_semana) * (self.width - 2*margin)
            
            # Círculo
            color = "#00d9ff" if event.get("destacado") else "#6c63ff"
            radius = 12 if event.get("destacado") else 8
            
            self.create_oval(x - radius, timeline_y - radius,
                           x + radius, timeline_y + radius,
                           fill=color, outline="white", width=2)
            
            # Número de semana
            self.create_text(x, timeline_y, text=str(event["semana"]),
                           fill="white", font=("Segoe UI", 8, "bold"))
            
            # Título
            self.create_text(x, timeline_y + 30, text=event["titulo"],
                           fill="#a0a0a0", font=("Segoe UI", 9),
                           width=80)

# -------------------------
# Stats Grid
# -------------------------

class StatsGrid(tk.Frame):
    """Grid de estadísticas con formato uniforme"""
    
    def __init__(self, parent, **kwargs):
        super().__init__(parent, bg=kwargs.get('bg', '#0a0a0a'))
        self.stats = []
    
    def add_stat(self, label, value, icon="", color="white"):
        """Agrega una estadística al grid"""
        self.stats.append({
            "label": label,
            "value": value,
            "icon": icon,
            "color": color
        })
        self.render()
    
    def render(self):
        """Renderiza todas las estadísticas"""
        # Limpiar
        for widget in self.winfo_children():
            widget.destroy()
        
        # Renderizar en grid 2 columnas
        for i, stat in enumerate(self.stats):
            row = i // 2
            col = i % 2
            
            stat_frame = tk.Frame(self, bg="#1a1a2e", bd=1, relief="solid")
            stat_frame.grid(row=row, column=col, padx=8, pady=8, sticky="nsew")
            
            # Icono
            if stat["icon"]:
                tk.Label(stat_frame, text=stat["icon"], bg="#1a1a2e",
                        fg=stat["color"], font=("Segoe UI", 16)).pack(pady=(8,0))
            
            # Valor
            tk.Label(stat_frame, text=stat["value"], bg="#1a1a2e",
                    fg="white", font=("Segoe UI", 20, "bold")).pack(pady=5)
            
            # Label
            tk.Label(stat_frame, text=stat["label"], bg="#1a1a2e",
                    fg="#a0a0a0", font=("Segoe UI", 9)).pack(pady=(0,8))

# -------------------------
# Notification Badge
# -------------------------

class NotificationBadge(tk.Frame):
    """Badge de notificación"""
    
    def __init__(self, parent, message, type="info", **kwargs):
        """
        type: "info", "success", "warning", "error"
        """
        colors = {
            "info": "#0ea5e9",
            "success": "#10b981",
            "warning": "#f59e0b",
            "error": "#ef4444"
        }
        
        icons = {
            "info": "ℹ️",
            "success": "✅",
            "warning": "⚠️",
            "error": "❌"
        }
        
        bg_color = colors.get(type, colors["info"])
        
        super().__init__(parent, bg=bg_color, bd=0, **kwargs)
        self.configure(padx=15, pady=10)
        
        # Icono
        tk.Label(self, text=icons.get(type, "ℹ️"), bg=bg_color,
                font=("Segoe UI", 14)).pack(side="left", padx=(0, 10))
        
        # Mensaje
        tk.Label(self, text=message, bg=bg_color, fg="white",
                font=("Segoe UI", 10), wraplength=400,
                justify="left").pack(side="left")

# -------------------------
# Week Calendar Widget
# -------------------------

class WeekCalendar(tk.Frame):
    """Calendario semanal con días completados"""
    
    def __init__(self, parent, **kwargs):
        super().__init__(parent, bg=kwargs.get('bg', '#0a0a0a'))
        self.dias = ["L", "M", "X", "J", "V", "S", "D"]
        self.completados = [False] * 7
    
    def set_completados(self, dias_completados):
        """
        dias_completados: list de índices [0-6] o booleanos
        """
        if isinstance(dias_completados, list):
            if all(isinstance(x, bool) for x in dias_completados):
                self.completados = dias_completados
            else:
                self.completados = [False] * 7
                for idx in dias_completados:
                    if 0 <= idx < 7:
                        self.completados[idx] = True
        self.render()
    
    def render(self):
        """Dibuja el calendario"""
        for widget in self.winfo_children():
            widget.destroy()
        
        for i, (dia, completado) in enumerate(zip(self.dias, self.completados)):
            color_bg = "#10b981" if completado else "#2e2e2e"
            color_fg = "white" if completado else "#6b7280"
            
            day_frame = tk.Frame(self, bg=color_bg, width=50, height=50,
                               bd=1, relief="solid")
            day_frame.pack(side="left", padx=4)
            day_frame.pack_propagate(False)
            
            tk.Label(day_frame, text=dia, bg=color_bg, fg=color_fg,
                    font=("Segoe UI", 14, "bold")).pack(expand=True)

# -------------------------
# Tabla de Ejercicios
# -------------------------

class ExerciseTable(tk.Frame):
    """Tabla para mostrar ejercicios con cargas"""
    
    def __init__(self, parent, **kwargs):
        super().__init__(parent, bg=kwargs.get('bg', '#0a0a0a'))
        
    def load_exercises(self, ejercicios):
        """
        ejercicios: list de dict [
            {"nombre": "Press banca", "kg": 50, "reps": 10, "series": 4},
            ...
        ]
        """
        # Limpiar
        for widget in self.winfo_children():
            widget.destroy()
        
        # Header
        header = tk.Frame(self, bg="#1a1a2e")
        header.pack(fill="x", pady=(0, 5))
        
        tk.Label(header, text="Ejercicio", bg="#1a1a2e", fg="#00d9ff",
                font=("Segoe UI", 11, "bold"), width=25, anchor="w").pack(side="left", padx=5)
        tk.Label(header, text="Carga", bg="#1a1a2e", fg="#00d9ff",
                font=("Segoe UI", 11, "bold"), width=10).pack(side="left", padx=5)
        tk.Label(header, text="Reps", bg="#1a1a2e", fg="#00d9ff",
                font=("Segoe UI", 11, "bold"), width=8).pack(side="left", padx=5)
        tk.Label(header, text="Series", bg="#1a1a2e", fg="#00d9ff",
                font=("Segoe UI", 11, "bold"), width=8).pack(side="left", padx=5)
        
        # Rows
        for i, ejer in enumerate(ejercicios):
            bg = "#16213e" if i % 2 == 0 else "#1a1a2e"
            row = tk.Frame(self, bg=bg)
            row.pack(fill="x", pady=2)
            
            tk.Label(row, text=ejer.get("nombre", ""), bg=bg, fg="white",
                    font=("Segoe UI", 10), width=25, anchor="w").pack(side="left", padx=5)
            
            # Carga (kg o intensidad)
            if "kg" in ejer:
                carga_text = f"{ejer['kg']}kg"
            elif "intensidad" in ejer:
                carga_text = ejer['intensidad']
            else:
                carga_text = "-"
            
            tk.Label(row, text=carga_text, bg=bg, fg="#4ade80",
                    font=("Segoe UI", 10, "bold"), width=10).pack(side="left", padx=5)
            
            reps_text = str(ejer.get("reps", "-"))
            tk.Label(row, text=reps_text, bg=bg, fg="white",
                    font=("Segoe UI", 10), width=8).pack(side="left", padx=5)
            
            series_text = str(ejer.get("series", "-"))
            tk.Label(row, text=series_text, bg=bg, fg="white",
                    font=("Segoe UI", 10), width=8).pack(side="left", padx=5)