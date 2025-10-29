import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import random
import json
import os
from PIL import Image, ImageTk
from datetime import datetime

# Importar módulos
from nutrition_engine import generar_plan_nutricional_completo
from learning_engine import (
    registrar_feedback_rutina, 
    registrar_feedback_dieta,
    calcular_scores_rutinas,
    generar_recomendacion_inteligente,
    registrar_medicion,
    obtener_estadisticas_personales,
    cargar_feedback
)

HISTORIAL_FILE = "historial.json"

# -------------------------
# Utilidades
# -------------------------
def cargar_historial():
    if not os.path.exists(HISTORIAL_FILE):
        return []
    try:
        with open(HISTORIAL_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return []

def guardar_en_historial(registro):
    data = cargar_historial()
    data.append(registro)
    with open(HISTORIAL_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def imc_bin_from_values(peso, estatura):
    try:
        imc = peso / ((estatura/100) ** 2)
    except Exception:
        return None, None
    if imc < 18.5:
        return imc, "bajo"
    if imc < 25:
        return imc, "normal"
    if imc < 30:
        return imc, "sobrepeso"
    return imc, "obesidad"

# -------------------------
# Generador de plan con ML
# -------------------------
EXERCISES = {
    "Fuerza": [("Mancuernas - Tren superior", 30), ("Sentadillas - Piernas", 30), ("Press banca - Pecho", 25), ("Peso muerto - Espalda", 25)],
    "Cardio": [("Cinta / Trote suave", 25), ("Bicicleta estática", 30), ("Elíptica", 25), ("Saltar cuerda (intervalos)", 15)],
    "Hipertrofia": [("Curl bíceps + series", 20), ("Peso muerto pesado", 30), ("Dominadas / Pull-ups", 15)],
    "Fullbody": [("Circuito fullbody", 40), ("Burpees + plancha", 25), ("Flexiones + zancadas", 30)],
    "HIIT": [("Sprint intercalado (10x30s)", 20), ("Burpees explosivos", 15), ("Saltos de caja", 20)],
    "Yoga": [("Estiramientos y movilidad", 30), ("Secuencia de posturas básicas", 25)]
}

def generar_plan_detallado_ml(imc, imc_bin, edad, motivo, genero, peso, estatura):
    """Genera plan usando algoritmo de aprendizaje"""
    if edad is None:
        dias = 4
    elif edad < 25:
        dias = random.choice([5,6])
    elif edad <= 40:
        dias = random.choice([4,5])
    else:
        dias = random.choice([3,4])
    
    # Usar ML para calcular scores
    perfil = {
        "imc_bin": imc_bin,
        "motivo": motivo,
        "edad": edad,
        "genero": genero,
        "peso_kg": peso,
        "estatura_cm": estatura
    }
    
    scores = calcular_scores_rutinas(perfil)
    rutinas_disponibles = list(scores.keys())
    pesos = list(scores.values())
    
    # Filtrar rutinas con score > 0
    rutinas_validas = [(r, p) for r, p in zip(rutinas_disponibles, pesos) if p > 0]
    if not rutinas_validas:
        rutinas_validas = list(EXERCISES.keys())[:3]
        rutinas_base = rutinas_validas
        pesos_norm = [1/len(rutinas_validas)] * len(rutinas_validas)
    else:
        rutinas_base = [r[0] for r in rutinas_validas]
        pesos_norm = [r[1] for r in rutinas_validas]
    
    dias_semana = ["Lunes","Martes","Miércoles","Jueves","Viernes","Sábado","Domingo"]
    entreno_indices = sorted(random.sample(range(7), dias))
    plan = {}
    
    for i, dia in enumerate(dias_semana):
        if i in entreno_indices:
            rutina_dia = random.choices(rutinas_base, weights=pesos_norm, k=1)[0]
            opciones = EXERCISES.get(rutina_dia, [])
            primary = random.choice(opciones) if opciones else ("Entrenamiento general", 30)
            
            complement_pool = [("Core / Abdominales", 15), ("Estiramientos", 10)]
            if rutina_dia in ["Fuerza", "Hipertrofia"]:
                complement_pool.append(("Cardio suave", 10))
            else:
                complement_pool.append(("Circuito ligero", 10))
            complement = random.choice(complement_pool)
            
            plan[dia] = {"rutina_tipo": rutina_dia, "primary": primary, "complement": complement}
        else:
            plan[dia] = {"rutina_tipo": "Descanso", "primary": ("Descanso / Recuperación", 0), "complement": None}
    
    enfoque = {
        "bajo": "Fuerza progresiva (ganancia muscular)",
        "normal": "Equilibrado (Cardio + Fuerza)",
        "sobrepeso": "Cardio moderado + fuerza ligera",
        "obesidad": "Cardio ligero y movilidad"
    }.get(imc_bin, "Equilibrado")
    
    return enfoque, plan, dias, 7-dias

# -------------------------
# Interfaz gráfica
# -------------------------
class GymApp:
    def __init__(self, root):
        self.root = root
        self.root.title("GymApp Pro - Con IA Adaptativa")
        self.root.geometry("900x750")
        self.root.configure(bg="#0a0a0a")
        
        self.genero = None
        self.edad = None
        self.estatura = None
        self.peso = None
        self.motivo = None
        self.user_id = None
        
        # Para tracking
        self.rutina_actual = None
        self.dieta_actual = None
        
        self.img_hombre = None
        self.img_mujer = None
        
        self.mostrar_menu_principal()
    
    # ========== MENU PRINCIPAL ==========
    def mostrar_menu_principal(self):
        self.limpiar_pantalla()
        
        # Banner superior
        banner = tk.Frame(self.root, bg="#1a1a2e", height=100)
        banner.pack(fill="x")
        
        tk.Label(banner, text="🏋️ GymApp Pro", fg="#00d9ff", bg="#1a1a2e",
                 font=("Segoe UI", 28, "bold")).pack(pady=10)
        tk.Label(banner, text="Sistema Inteligente con Aprendizaje Adaptativo", 
                 fg="#a0a0a0", bg="#1a1a2e", font=("Segoe UI", 11, "italic")).pack()
        
        # Estadísticas globales
        data_fb = cargar_feedback()
        stats = data_fb.get("estadisticas", {})
        
        stats_frame = tk.Frame(self.root, bg="#16213e")
        stats_frame.pack(fill="x", pady=15)
        
        tk.Label(stats_frame, text=f"📊 Total Usuarios: {stats.get('total_feedbacks_rutinas', 0) + stats.get('total_feedbacks_dietas', 0)}", 
                 bg="#16213e", fg="white", font=("Segoe UI", 10)).pack(side="left", padx=20)
        tk.Label(stats_frame, text=f"⭐ Satisfacción Promedio: {stats.get('promedio_calificacion_rutinas', 0)}/5.0",
                 bg="#16213e", fg="#ffd700", font=("Segoe UI", 10)).pack(side="left", padx=20)
        
        # Opciones principales
        opciones_frame = tk.Frame(self.root, bg="#0a0a0a")
        opciones_frame.pack(expand=True, pady=30)
        
        tk.Button(opciones_frame, text="🆕 Crear Nueva Rutina/Dieta", width=30, height=3,
                  bg="#00d9ff", fg="black", font=("Segoe UI", 13, "bold"),
                  command=self.mostrar_pantalla_genero).pack(pady=10)
        
        tk.Button(opciones_frame, text="📈 Ver Mi Progreso", width=30, height=2,
                  bg="#6c63ff", fg="white", font=("Segoe UI", 12, "bold"),
                  command=self.mostrar_progreso_personal).pack(pady=10)
        
        tk.Button(opciones_frame, text="💬 Dar Feedback de Rutina/Dieta", width=30, height=2,
                  bg="#f368e0", fg="white", font=("Segoe UI", 12, "bold"),
                  command=self.mostrar_seleccion_feedback).pack(pady=10)
        
        tk.Button(opciones_frame, text="📊 Estadísticas Globales", width=30, height=2,
                  bg="#48dbfb", fg="black", font=("Segoe UI", 12, "bold"),
                  command=self.mostrar_estadisticas_globales).pack(pady=10)
    
    # ========== PANTALLAS DE REGISTRO ==========
    def mostrar_pantalla_genero(self):
        self.limpiar_pantalla()
        tk.Label(self.root, text="Selecciona tu género", fg="white", bg="#0a0a0a",
                 font=("Segoe UI", 20, "bold")).pack(pady=18)
        
        frame = tk.Frame(self.root, bg="#0a0a0a")
        frame.pack(pady=10)
        
        try:
            img_h = Image.open("musculoso.jpg").resize((120,120))
            img_m = Image.open("esstarla.jpg").resize((120,120))
            self.img_hombre = ImageTk.PhotoImage(img_h)
            self.img_mujer = ImageTk.PhotoImage(img_m)
        except:
            self.img_hombre = None
            self.img_mujer = None
        
        if self.img_hombre:
            self.btn_hombre = tk.Button(frame, text="Hombre", image=self.img_hombre, compound="top",
                                        width=150, height=160, bg="#083b3b", fg="white",
                                        font=("Segoe UI", 11, "bold"),
                                        command=lambda: self.seleccionar_genero("Hombre"))
        else:
            self.btn_hombre = tk.Button(frame, text="Hombre", width=15, height=3, bg="#083b3b", fg="white",
                                        font=("Segoe UI", 11, "bold"),
                                        command=lambda: self.seleccionar_genero("Hombre"))
        self.btn_hombre.pack(side="left", padx=25)
        
        if self.img_mujer:
            self.btn_mujer = tk.Button(frame, text="Mujer", image=self.img_mujer, compound="top",
                                       width=150, height=160, bg="#6b0b5b", fg="white",
                                       font=("Segoe UI", 11, "bold"),
                                       command=lambda: self.seleccionar_genero("Mujer"))
        else:
            self.btn_mujer = tk.Button(frame, text="Mujer", width=15, height=3, bg="#6b0b5b", fg="white",
                                       font=("Segoe UI", 11, "bold"),
                                       command=lambda: self.seleccionar_genero("Mujer"))
        self.btn_mujer.pack(side="left", padx=25)
        
        self.btn_siguiente = tk.Button(self.root, text="Siguiente", width=18, height=2,
                                       bg="#2e2e2e", fg="white", font=("Segoe UI", 11, "bold"),
                                       command=self.mostrar_pantalla_edad)
    
    def seleccionar_genero(self, genero):
        self.genero = genero
        if genero == "Hombre":
            self.btn_hombre.config(bg="#00ffcc")
            self.btn_mujer.config(bg="#2e2e2e")
        else:
            self.btn_mujer.config(bg="#ff7adf")
            self.btn_hombre.config(bg="#2e2e2e")
        self.btn_siguiente.pack(pady=18)
    
    def mostrar_pantalla_edad(self):
        self.limpiar_pantalla()
        tk.Label(self.root, text="Indica tu edad", fg="white", bg="#0a0a0a",
                 font=("Segoe UI", 18, "bold")).pack(pady=12)
        
        self.edad_var = tk.IntVar(value=25)
        scale = ttk.Scale(self.root, from_=12, to=80, orient="horizontal",
                          variable=self.edad_var,
                          command=lambda v: self.actualizar_valor(self.edad_var, self.lbl_edad, "años"))
        scale.pack(pady=8, ipadx=120)
        self.lbl_edad = tk.Label(self.root, text="25 años", fg="white", bg="#0a0a0a")
        self.lbl_edad.pack(pady=6)
        
        tk.Button(self.root, text="Siguiente", width=16, height=2, bg="#00d9ff", fg="black",
                  font=("Segoe UI", 11, "bold"), command=self.guardar_edad).pack(pady=16)
    
    def actualizar_valor(self, var, label, unidad):
        val = int(var.get())
        label.config(text=f"{val} {unidad}")
    
    def guardar_edad(self):
        self.edad = int(self.edad_var.get())
        self.mostrar_pantalla_estatura()
    
    def mostrar_pantalla_estatura(self):
        self.limpiar_pantalla()
        tk.Label(self.root, text="Estatura y peso", fg="white", bg="#0a0a0a",
                 font=("Segoe UI", 18, "bold")).pack(pady=12)
        
        tk.Label(self.root, text="Estatura (cm):", fg="white", bg="#0a0a0a").pack()
        self.estatura_var = tk.IntVar(value=170)
        s1 = ttk.Scale(self.root, from_=130, to=210, orient="horizontal",
                       variable=self.estatura_var,
                       command=lambda v: self.actualizar_valor(self.estatura_var, self.lbl_estatura, "cm"))
        s1.pack(pady=6, ipadx=120)
        self.lbl_estatura = tk.Label(self.root, text="170 cm", fg="white", bg="#0a0a0a")
        self.lbl_estatura.pack(pady=6)
        
        tk.Label(self.root, text="Peso (kg):", fg="white", bg="#0a0a0a").pack()
        self.peso_var = tk.IntVar(value=70)
        s2 = ttk.Scale(self.root, from_=35, to=150, orient="horizontal",
                       variable=self.peso_var,
                       command=lambda v: self.actualizar_valor(self.peso_var, self.lbl_peso, "kg"))
        s2.pack(pady=6, ipadx=120)
        self.lbl_peso = tk.Label(self.root, text="70 kg", fg="white", bg="#0a0a0a")
        self.lbl_peso.pack(pady=6)
        
        tk.Button(self.root, text="Siguiente", width=16, height=2, bg="#00d9ff", fg="black",
                  font=("Segoe UI", 11, "bold"), command=self.guardar_estatura_peso).pack(pady=16)
    
    def guardar_estatura_peso(self):
        self.estatura = int(self.estatura_var.get())
        self.peso = int(self.peso_var.get())
        self.mostrar_pantalla_motivo()
    
    def mostrar_pantalla_motivo(self):
        self.limpiar_pantalla()
        tk.Label(self.root, text="¿Cuál es tu motivo?", fg="white", bg="#0a0a0a",
                 font=("Segoe UI", 18, "bold")).pack(pady=12)
        
        frame = tk.Frame(self.root, bg="#0a0a0a")
        frame.pack(pady=10)
        
        tk.Button(frame, text="Salud", width=12, height=2, bg="#0fb9b1", fg="white",
                  font=("Segoe UI", 11, "bold"), command=lambda: self.seleccionar_motivo("Salud")).pack(side="left", padx=10)
        tk.Button(frame, text="Rutina", width=12, height=2, bg="#ff9f1c", fg="white",
                  font=("Segoe UI", 11, "bold"), command=lambda: self.seleccionar_motivo("Rutina")).pack(side="left", padx=10)
        tk.Button(frame, text="Nuevo", width=12, height=2, bg="#ff4d9a", fg="white",
                  font=("Segoe UI", 11, "bold"), command=lambda: self.seleccionar_motivo("Nuevo")).pack(side="left", padx=10)
    
    def seleccionar_motivo(self, m):
        self.motivo = m
        self.user_id = f"{self.genero}_{self.edad}_{datetime.now().timestamp()}"
        self.mostrar_recomendacion_ia()
    
    # ========== RECOMENDACIÓN CON IA ==========
    def mostrar_recomendacion_ia(self):
        self.limpiar_pantalla()
        
        imc, imc_bin = imc_bin_from_values(self.peso, self.estatura)
        
        tk.Label(self.root, text="🤖 Analizando tu perfil con IA...", fg="#00d9ff", bg="#0a0a0a",
                 font=("Segoe UI", 20, "bold")).pack(pady=15)
        
        # Generar recomendación inteligente
        perfil = {
            "imc_bin": imc_bin,
            "motivo": self.motivo,
            "edad": self.edad,
            "genero": self.genero,
            "peso_kg": self.peso,
            "estatura_cm": self.estatura
        }
        
        recomendacion = generar_recomendacion_inteligente(perfil)
        
        # Mostrar análisis
        info_frame = tk.Frame(self.root, bg="#1a1a2e", bd=2, relief="solid")
        info_frame.pack(fill="x", padx=30, pady=15)
        
        tk.Label(info_frame, text="📊 Tu Perfil", bg="#1a1a2e", fg="#ffd700",
                 font=("Segoe UI", 14, "bold")).pack(pady=8)
        tk.Label(info_frame, text=f"IMC: {imc:.1f} ({imc_bin}) | Edad: {self.edad} | Motivo: {self.motivo}",
                 bg="#1a1a2e", fg="white", font=("Segoe UI", 11)).pack(pady=4)
        
        # Recomendación de rutina
        rutina_frame = tk.Frame(self.root, bg="#0f4c75", bd=2, relief="solid")
        rutina_frame.pack(fill="x", padx=30, pady=10)
        
        tk.Label(rutina_frame, text=f"💪 Rutina Recomendada: {recomendacion['rutina_recomendada']}", 
                 bg="#0f4c75", fg="#4ade80", font=("Segoe UI", 13, "bold")).pack(pady=8)
        tk.Label(rutina_frame, text=f"Confianza: {recomendacion['confianza_rutina']}%",
                 bg="#0f4c75", fg="#fbbf24", font=("Segoe UI", 10)).pack()
        tk.Label(rutina_frame, text=recomendacion['explicacion_rutina'],
                 bg="#0f4c75", fg="white", font=("Segoe UI", 10), wraplength=700).pack(pady=8, padx=15)
        
        # Recomendación de dieta
        dieta_frame = tk.Frame(self.root, bg="#2d5016", bd=2, relief="solid")
        dieta_frame.pack(fill="x", padx=30, pady=10)
        
        tk.Label(dieta_frame, text=f"🥗 Plan Nutricional: {recomendacion['dieta_recomendada']}", 
                 bg="#2d5016", fg="#4ade80", font=("Segoe UI", 13, "bold")).pack(pady=8)
        tk.Label(dieta_frame, text=f"Confianza: {recomendacion['confianza_dieta']}%",
                 bg="#2d5016", fg="#fbbf24", font=("Segoe UI", 10)).pack()
        tk.Label(dieta_frame, text=recomendacion['explicacion_dieta'],
                 bg="#2d5016", fg="white", font=("Segoe UI", 10), wraplength=700).pack(pady=8, padx=15)
        
        # Botones
        btn_frame = tk.Frame(self.root, bg="#0a0a0a")
        btn_frame.pack(pady=20)
        
        tk.Button(btn_frame, text="✅ Generar Rutina", bg="#00d9ff", fg="black", width=18, height=2,
                  font=("Segoe UI", 11, "bold"), command=self.mostrar_rutina_final).pack(side="left", padx=8)
        tk.Button(btn_frame, text="🥗 Generar Dieta", bg="#43a047", fg="white", width=18, height=2,
                  font=("Segoe UI", 11, "bold"), command=self.mostrar_plan_nutricional).pack(side="left", padx=8)
    
    # ========== RUTINA Y DIETA (Código anterior adaptado) ==========
    def mostrar_rutina_final(self):
        self.limpiar_pantalla()
        
        imc, imc_bin = imc_bin_from_values(self.peso, self.estatura)
        enfoque, plan, dias_entreno, descansos = generar_plan_detallado_ml(
            imc, imc_bin, self.edad, self.motivo, self.genero, self.peso, self.estatura
        )
        
        self.rutina_actual = plan
        
        tk.Label(self.root, text="💪 Tu Rutina Personalizada", fg="white", bg="#0a0a0a",
                 font=("Segoe UI", 18, "bold")).pack(pady=8)
        
        info = f"IMC: {imc:.1f} | Enfoque: {enfoque} | Días: {dias_entreno}"
        tk.Label(self.root, text=info, fg="#aaddff", bg="#0a0a0a", font=("Segoe UI", 10)).pack(pady=4)
        
        canvas = tk.Canvas(self.root, bg="#0a0a0a", highlightthickness=0, height=450)
        canvas.pack(fill="both", expand=True, padx=12, pady=8)
        frame_cards = tk.Frame(canvas, bg="#0a0a0a")
        canvas.create_window((0,0), window=frame_cards, anchor="nw")
        
        for i, dia in enumerate(["Lunes","Martes","Miércoles","Jueves","Viernes","Sábado","Domingo"]):
            info_dia = plan[dia]
            card_bg = "#1b1b1b" if info_dia["rutina_tipo"]=="Descanso" else "#0f4c75"
            fg = "#9aa" if info_dia["rutina_tipo"]=="Descanso" else "white"
            
            card = tk.Frame(frame_cards, bg=card_bg, bd=1, relief="ridge", padx=10, pady=8)
            card.grid(row=i//2, column=i%2, padx=8, pady=8, sticky="nsew")
            
            tk.Label(card, text=dia, bg=card_bg, fg="#ffd", font=("Segoe UI", 12, "bold")).pack(anchor="w")
            tk.Label(card, text=f"Tipo: {info_dia['rutina_tipo']}", bg=card_bg, fg=fg, 
                     font=("Segoe UI", 10, "italic")).pack(anchor="w", pady=(4,0))
            
            p = info_dia["primary"]
            tk.Label(card, text=f"- {p[0]} ({p[1]} min)", bg=card_bg, fg=fg, 
                     font=("Segoe UI", 10)).pack(anchor="w", pady=(6,0))
            
            comp = info_dia.get("complement")
            if comp:
                tk.Label(card, text=f"- {comp[0]} ({comp[1]} min)", bg=card_bg, fg=fg, 
                         font=("Segoe UI", 10)).pack(anchor="w")
        
        frame_cards.update_idletasks()
        canvas.config(scrollregion=canvas.bbox("all"))
        
        btn_frame = tk.Frame(self.root, bg="#0a0a0a")
        btn_frame.pack(pady=10)
        
        tk.Button(btn_frame, text="💬 Dar Feedback", bg="#f368e0", fg="white", width=18,
                  font=("Segoe UI", 10, "bold"), 
                  command=lambda: self.mostrar_feedback_rutina(plan)).pack(side="left", padx=5)
        tk.Button(btn_frame, text="Ver Dieta", bg="#43a047", fg="white", width=15,
                  font=("Segoe UI", 10, "bold"), command=self.mostrar_plan_nutricional).pack(side="left", padx=5)
        tk.Button(btn_frame, text="← Inicio", bg="#374151", fg="white", width=12,
                  font=("Segoe UI", 10, "bold"), command=self.mostrar_menu_principal).pack(side="left", padx=5)
    
    def mostrar_plan_nutricional(self):
        self.limpiar_pantalla()
        
        imc, imc_bin = imc_bin_from_values(self.peso, self.estatura)
        dias_entreno = 5 if self.edad < 25 else 4 if self.edad <= 40 else 3
        
        plan_nutri = generar_plan_nutricional_completo(
            self.peso, self.estatura, self.edad, self.genero,
            self.motivo, imc_bin, dias_entreno
        )
        
        self.dieta_actual = plan_nutri
        
        tk.Label(self.root, text="📊 Tu Plan Nutricional", fg="white", bg="#0a0a0a",
                 font=("Segoe UI", 18, "bold")).pack(pady=10)
        
        canvas = tk.Canvas(self.root, bg="#0a0a0a", highlightthickness=0, height=500)
        scrollbar = tk.Scrollbar(self.root, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg="#0a0a0a")
        
        scrollable_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True, padx=10)
        scrollbar.pack(side="right", fill="y")
        
        # Metabolismo
        metab = plan_nutri["metabolismo"]
        frame_metab = tk.Frame(scrollable_frame, bg="#1a3a4a", bd=2, relief="ridge")
        frame_metab.pack(fill="x", padx=15, pady=10)
        
        tk.Label(frame_metab, text="🔥 Metabolismo", bg="#1a3a4a", fg="#ffdd57",
                 font=("Segoe UI", 14, "bold")).pack(anchor="w", padx=10, pady=8)
        tk.Label(frame_metab, text=f"• Objetivo: {metab['objetivo_calorico']} kcal/día ({metab['tipo_objetivo']})",
                 bg="#1a3a4a", fg="#4ade80", font=("Segoe UI", 11, "bold")).pack(anchor="w", padx=20, pady=2)
        
        # Macros
        macros = plan_nutri["macronutrientes"]
        frame_macros = tk.Frame(scrollable_frame, bg="#2d1b4e", bd=2, relief="ridge")
        frame_macros.pack(fill="x", padx=15, pady=10)
        
        tk.Label(frame_macros, text="🍗 Macronutrientes", bg="#2d1b4e", fg="#a78bfa",
                 font=("Segoe UI", 14, "bold")).pack(anchor="w", padx=10, pady=8)
        tk.Label(frame_macros, text=f"Proteínas: {macros['proteinas']}g | Carbos: {macros['carbohidratos']}g | Grasas: {macros['grasas']}g",
                 bg="#2d1b4e", fg="white", font=("Segoe UI", 11)).pack(anchor="w", padx=20, pady=2)
        
        # Comidas
        tk.Label(scrollable_frame, text="🍽️ Plan de Comidas", bg="#0a0a0a", fg="#4ade80",
                 font=("Segoe UI", 14, "bold")).pack(anchor="w", padx=15, pady=10)
        
        colores = {"Desayuno": "#0f766e", "Snack Pre-Entreno": "#b45309", "Almuerzo": "#0369a1",
                   "Merienda": "#be185d", "Cena": "#4338ca"}
        
        for tiempo, detalle in plan_nutri["plan_comidas"].items():
            frame_comida = tk.Frame(scrollable_frame, bg=colores.get(tiempo, "#1e3a5f"), bd=1, relief="solid")
            frame_comida.pack(fill="x", padx=20, pady=6)
            
            tk.Label(frame_comida, text=f"⏰ {tiempo}", bg=colores.get(tiempo, "#1e3a5f"), fg="#ffd700",
                     font=("Segoe UI", 11, "bold")).pack(anchor="w", padx=10, pady=4)
            
            for alimento in detalle.get("alimentos", []):
                tk.Label(frame_comida, text=f"  • {alimento[0]} ({alimento[1]} kcal)",
                         bg=colores.get(tiempo, "#1e3a5f"), fg="#e0e0e0", 
                         font=("Segoe UI", 9)).pack(anchor="w", padx=15)
        
        # Botones
        btn_frame = tk.Frame(self.root, bg="#0a0a0a")
        btn_frame.pack(pady=10)
        
        tk.Button(btn_frame, text="💬 Dar Feedback", bg="#f368e0", fg="white", width=18,
                  font=("Segoe UI", 10, "bold"),
                  command=lambda: self.mostrar_feedback_dieta(plan_nutri)).pack(side="left", padx=5)
        tk.Button(btn_frame, text="Ver Rutina", bg="#00d9ff", fg="black", width=15,
                  font=("Segoe UI", 10, "bold"), command=self.mostrar_rutina_final).pack(side="left", padx=5)
        tk.Button(btn_frame, text="← Inicio", bg="#374151", fg="white", width=12,
                  font=("Segoe UI", 10, "bold"), command=self.mostrar_menu_principal).pack(side="left", padx=5)
    
    # ========== SISTEMA DE FEEDBACK ==========
    def mostrar_seleccion_feedback(self):
        self.limpiar_pantalla()
        
        tk.Label(self.root, text="¿Qué deseas evaluar?", fg="white", bg="#0a0a0a",
                 font=("Segoe UI", 20, "bold")).pack(pady=30)
        
        tk.Button(self.root, text="💪 Feedback de Rutina", width=30, height=3,
                  bg="#00d9ff", fg="black", font=("Segoe UI", 13, "bold"),
                  command=lambda: self.mostrar_feedback_rutina(None)).pack(pady=15)
        
        tk.Button(self.root, text="🥗 Feedback de Dieta", width=30, height=3,
                  bg="#43a047", fg="white", font=("Segoe UI", 13, "bold"),
                  command=lambda: self.mostrar_feedback_dieta(None)).pack(pady=15)
        
        tk.Button(self.root, text="← Volver", bg="#374151", fg="white", width=20,
                  font=("Segoe UI", 11, "bold"), command=self.mostrar_menu_principal).pack(pady=20)
    
    def mostrar_feedback_rutina(self, plan_rutina):
        ventana_fb = tk.Toplevel(self.root)
        ventana_fb.title("Feedback de Rutina")
        ventana_fb.geometry("600x550")
        ventana_fb.configure(bg="#1a1a2e")
        
        tk.Label(ventana_fb, text="💬 Evalúa tu rutina", fg="#00d9ff", bg="#1a1a2e",
                 font=("Segoe UI", 18, "bold")).pack(pady=15)
        
        # Calificación
        tk.Label(ventana_fb, text="⭐ Calificación (1-5):", fg="white", bg="#1a1a2e",
                 font=("Segoe UI", 12)).pack(pady=8)
        
        cal_var = tk.IntVar(value=5)
        cal_frame = tk.Frame(ventana_fb, bg="#1a1a2e")
        cal_frame.pack()
        
        for i in range(1, 6):
            tk.Radiobutton(cal_frame, text=f"{i}★", variable=cal_var, value=i,
                           bg="#1a1a2e", fg="white", selectcolor="#0f4c75",
                           font=("Segoe UI", 11)).pack(side="left", padx=8)
        
        # Días completados
        tk.Label(ventana_fb, text="📅 Días completados:", fg="white", bg="#1a1a2e",
                 font=("Segoe UI", 12)).pack(pady=(15,5))
        
        dias_var = tk.IntVar(value=4)
        dias_scale = ttk.Scale(ventana_fb, from_=0, to=7, orient="horizontal",
                               variable=dias_var, length=300)
        dias_scale.pack()
        
        dias_label = tk.Label(ventana_fb, text="4 días", fg="#ffd700", bg="#1a1a2e",
                              font=("Segoe UI", 11))
        dias_label.pack()
        
        dias_scale.config(command=lambda v: dias_label.config(text=f"{int(float(v))} días"))
        
        # Comentarios
        tk.Label(ventana_fb, text="💭 Comentarios (opcional):", fg="white", bg="#1a1a2e",
                 font=("Segoe UI", 12)).pack(pady=(15,5))
        
        comentario_text = scrolledtext.ScrolledText(ventana_fb, height=5, width=50,
                                                     bg="#2e2e2e", fg="white", 
                                                     font=("Segoe UI", 10))
        comentario_text.pack(padx=20)
        
        def guardar_feedback_rutina():
            if not self.genero or not self.edad:
                messagebox.showwarning("Datos incompletos", 
                                       "Primero crea una rutina desde el menú principal")
                ventana_fb.destroy()
                return
            
            usuario = {
                "genero": self.genero,
                "edad": self.edad,
                "estatura_cm": self.estatura,
                "peso_kg": self.peso,
                "motivo": self.motivo,
                "imc": imc_bin_from_values(self.peso, self.estatura)[0],
                "imc_bin": imc_bin_from_values(self.peso, self.estatura)[1]
            }
            
            rutina = plan_rutina if plan_rutina else self.rutina_actual
            if not rutina:
                rutina = {"Lunes": {"rutina_tipo": "Fuerza", "primary": ("Ejercicio", 30)}}
            
            registrar_feedback_rutina(
                usuario, rutina,
                cal_var.get(),
                dias_var.get(),
                comentario_text.get("1.0", "end-1c")
            )
            
            messagebox.showinfo("¡Gracias!", 
                                "Tu feedback ayudará a mejorar las recomendaciones para todos")
            ventana_fb.destroy()
        
        tk.Button(ventana_fb, text="✅ Enviar Feedback", bg="#00d9ff", fg="black", width=20,
                  font=("Segoe UI", 12, "bold"), command=guardar_feedback_rutina).pack(pady=20)
    
    def mostrar_feedback_dieta(self, plan_nutri):
        ventana_fb = tk.Toplevel(self.root)
        ventana_fb.title("Feedback de Dieta")
        ventana_fb.geometry("600x600")
        ventana_fb.configure(bg="#1a1a2e")
        
        tk.Label(ventana_fb, text="💬 Evalúa tu plan nutricional", fg="#43a047", bg="#1a1a2e",
                 font=("Segoe UI", 18, "bold")).pack(pady=15)
        
        # Calificación
        tk.Label(ventana_fb, text="⭐ Calificación (1-5):", fg="white", bg="#1a1a2e",
                 font=("Segoe UI", 12)).pack(pady=8)
        
        cal_var = tk.IntVar(value=5)
        cal_frame = tk.Frame(ventana_fb, bg="#1a1a2e")
        cal_frame.pack()
        
        for i in range(1, 6):
            tk.Radiobutton(cal_frame, text=f"{i}★", variable=cal_var, value=i,
                           bg="#1a1a2e", fg="white", selectcolor="#2d5016",
                           font=("Segoe UI", 11)).pack(side="left", padx=8)
        
        # Días seguidos
        tk.Label(ventana_fb, text="📅 Días que seguiste la dieta:", fg="white", bg="#1a1a2e",
                 font=("Segoe UI", 12)).pack(pady=(15,5))
        
        dias_var = tk.IntVar(value=5)
        dias_scale = ttk.Scale(ventana_fb, from_=0, to=14, orient="horizontal",
                               variable=dias_var, length=300)
        dias_scale.pack()
        
        dias_label = tk.Label(ventana_fb, text="5 días", fg="#ffd700", bg="#1a1a2e",
                              font=("Segoe UI", 11))
        dias_label.pack()
        
        dias_scale.config(command=lambda v: dias_label.config(text=f"{int(float(v))} días"))
        
        # Peso actual
        tk.Label(ventana_fb, text="⚖️ Peso actual (kg):", fg="white", bg="#1a1a2e",
                 font=("Segoe UI", 12)).pack(pady=(15,5))
        
        peso_var = tk.DoubleVar(value=self.peso if self.peso else 70.0)
        peso_frame = tk.Frame(ventana_fb, bg="#1a1a2e")
        peso_frame.pack()
        
        tk.Entry(peso_frame, textvariable=peso_var, width=10, font=("Segoe UI", 12),
                 bg="#2e2e2e", fg="white").pack(side="left", padx=5)
        tk.Label(peso_frame, text="kg", fg="white", bg="#1a1a2e",
                 font=("Segoe UI", 11)).pack(side="left")
        
        # Comentarios
        tk.Label(ventana_fb, text="💭 Comentarios (opcional):", fg="white", bg="#1a1a2e",
                 font=("Segoe UI", 12)).pack(pady=(15,5))
        
        comentario_text = scrolledtext.ScrolledText(ventana_fb, height=5, width=50,
                                                     bg="#2e2e2e", fg="white",
                                                     font=("Segoe UI", 10))
        comentario_text.pack(padx=20)
        
        def guardar_feedback_dieta():
            if not self.genero or not self.edad:
                messagebox.showwarning("Datos incompletos",
                                       "Primero crea una dieta desde el menú principal")
                ventana_fb.destroy()
                return
            
            usuario = {
                "genero": self.genero,
                "edad": self.edad,
                "estatura_cm": self.estatura,
                "peso_kg": self.peso,
                "motivo": self.motivo,
                "imc": imc_bin_from_values(self.peso, self.estatura)[0],
                "imc_bin": imc_bin_from_values(self.peso, self.estatura)[1]
            }
            
            plan = plan_nutri if plan_nutri else self.dieta_actual
            if not plan:
                # Plan dummy
                plan = {
                    "metabolismo": {"objetivo_calorico": 2000, "tipo_objetivo": "Mantenimiento"},
                    "macronutrientes": {"proteinas": 150, "carbohidratos": 200, "grasas": 60}
                }
            
            registrar_feedback_dieta(
                usuario, plan,
                cal_var.get(),
                dias_var.get(),
                peso_var.get(),
                comentario_text.get("1.0", "end-1c")
            )
            
            messagebox.showinfo("¡Gracias!",
                                "Tu feedback ayudará a mejorar las recomendaciones nutricionales")
            ventana_fb.destroy()
        
        tk.Button(ventana_fb, text="✅ Enviar Feedback", bg="#43a047", fg="white", width=20,
                  font=("Segoe UI", 12, "bold"), command=guardar_feedback_dieta).pack(pady=20)
    
    # ========== PROGRESO PERSONAL ==========
    def mostrar_progreso_personal(self):
        self.limpiar_pantalla()
        
        tk.Label(self.root, text="📈 Mi Progreso Personal", fg="#00d9ff", bg="#0a0a0a",
                 font=("Segoe UI", 20, "bold")).pack(pady=15)
        
        # Verificar si hay user_id
        if not self.user_id:
            self.user_id = "demo_user"
        
        stats = obtener_estadisticas_personales(self.user_id)
        
        if not stats:
            # Primera vez - solicitar datos iniciales
            frame_init = tk.Frame(self.root, bg="#1a1a2e", bd=2, relief="solid")
            frame_init.pack(fill="x", padx=40, pady=30)
            
            tk.Label(frame_init, text="🎯 Registra tu primera medición", bg="#1a1a2e", fg="#ffd700",
                     font=("Segoe UI", 16, "bold")).pack(pady=15)
            
            tk.Label(frame_init, text="Peso actual (kg):", bg="#1a1a2e", fg="white",
                     font=("Segoe UI", 12)).pack(pady=5)
            
            peso_entry = tk.Entry(frame_init, font=("Segoe UI", 12), width=15,
                                  bg="#2e2e2e", fg="white")
            peso_entry.pack(pady=5)
            peso_entry.insert(0, str(self.peso) if self.peso else "70")
            
            tk.Label(frame_init, text="Estatura (cm):", bg="#1a1a2e", fg="white",
                     font=("Segoe UI", 12)).pack(pady=5)
            
            est_entry = tk.Entry(frame_init, font=("Segoe UI", 12), width=15,
                                 bg="#2e2e2e", fg="white")
            est_entry.pack(pady=5)
            est_entry.insert(0, str(self.estatura) if self.estatura else "170")
            
            def guardar_primera_medicion():
                try:
                    peso = float(peso_entry.get())
                    estatura = float(est_entry.get())
                    imc, _ = imc_bin_from_values(peso, estatura)
                    
                    registrar_medicion(self.user_id, peso, imc)
                    messagebox.showinfo("¡Listo!", "Primera medición registrada")
                    self.mostrar_progreso_personal()
                except:
                    messagebox.showerror("Error", "Ingresa valores numéricos válidos")
            
            tk.Button(frame_init, text="💾 Guardar Medición", bg="#00d9ff", fg="black",
                      width=20, height=2, font=("Segoe UI", 11, "bold"),
                      command=guardar_primera_medicion).pack(pady=15)
        else:
            # Mostrar estadísticas
            stats_frame = tk.Frame(self.root, bg="#1a1a2e", bd=2, relief="solid")
            stats_frame.pack(fill="x", padx=40, pady=20)
            
            tk.Label(stats_frame, text="📊 Resumen de tu Progreso", bg="#1a1a2e", fg="#ffd700",
                     font=("Segoe UI", 16, "bold")).pack(pady=12)
            
            info_grid = tk.Frame(stats_frame, bg="#1a1a2e")
            info_grid.pack(pady=10)
            
            # Peso
            cambio_color = "#4ade80" if stats["cambio_total_kg"] < 0 else "#ef4444" if stats["cambio_total_kg"] > 0 else "#fbbf24"
            signo = "-" if stats["cambio_total_kg"] < 0 else "+" if stats["cambio_total_kg"] > 0 else ""
            
            tk.Label(info_grid, text=f"⚖️ Peso inicial: {stats['peso_inicial']}kg",
                     bg="#1a1a2e", fg="white", font=("Segoe UI", 12)).grid(row=0, column=0, padx=20, pady=5, sticky="w")
            tk.Label(info_grid, text=f"⚖️ Peso actual: {stats['peso_actual']}kg",
                     bg="#1a1a2e", fg="white", font=("Segoe UI", 12)).grid(row=1, column=0, padx=20, pady=5, sticky="w")
            tk.Label(info_grid, text=f"📉 Cambio: {signo}{abs(stats['cambio_total_kg'])}kg",
                     bg="#1a1a2e", fg=cambio_color, font=("Segoe UI", 13, "bold")).grid(row=2, column=0, padx=20, pady=5, sticky="w")
            
            # IMC
            tk.Label(info_grid, text=f"📊 IMC inicial: {stats['imc_inicial']:.1f}",
                     bg="#1a1a2e", fg="white", font=("Segoe UI", 12)).grid(row=0, column=1, padx=20, pady=5, sticky="w")
            tk.Label(info_grid, text=f"📊 IMC actual: {stats['imc_actual']:.1f}",
                     bg="#1a1a2e", fg="white", font=("Segoe UI", 12)).grid(row=1, column=1, padx=20, pady=5, sticky="w")
            
            # Actividad
            tk.Label(info_grid, text=f"💪 Rutinas completadas: {stats['rutinas_completadas']}",
                     bg="#1a1a2e", fg="#00d9ff", font=("Segoe UI", 12)).grid(row=3, column=0, padx=20, pady=5, sticky="w")
            tk.Label(info_grid, text=f"🥗 Dietas completadas: {stats['dietas_completadas']}",
                     bg="#1a1a2e", fg="#43a047", font=("Segoe UI", 12)).grid(row=3, column=1, padx=20, pady=5, sticky="w")
            
            tk.Label(info_grid, text=f"📅 Total mediciones: {stats['total_mediciones']}",
                     bg="#1a1a2e", fg="#fbbf24", font=("Segoe UI", 12)).grid(row=4, column=0, padx=20, pady=5, sticky="w")
            
            # Botón nueva medición
            tk.Button(stats_frame, text="➕ Registrar Nueva Medición", bg="#6c63ff", fg="white",
                      width=25, height=2, font=("Segoe UI", 11, "bold"),
                      command=lambda: self.registrar_nueva_medicion()).pack(pady=15)
        
        tk.Button(self.root, text="← Volver al Inicio", bg="#374151", fg="white", width=20,
                  font=("Segoe UI", 11, "bold"), command=self.mostrar_menu_principal).pack(pady=20)
    
    def registrar_nueva_medicion(self):
        ventana = tk.Toplevel(self.root)
        ventana.title("Nueva Medición")
        ventana.geometry("400x350")
        ventana.configure(bg="#1a1a2e")
        
        tk.Label(ventana, text="📝 Nueva Medición", fg="#00d9ff", bg="#1a1a2e",
                 font=("Segoe UI", 18, "bold")).pack(pady=20)
        
        tk.Label(ventana, text="Peso actual (kg):", fg="white", bg="#1a1a2e",
                 font=("Segoe UI", 12)).pack(pady=5)
        peso_entry = tk.Entry(ventana, font=("Segoe UI", 12), width=15,
                              bg="#2e2e2e", fg="white")
        peso_entry.pack(pady=5)
        
        tk.Label(ventana, text="Notas (opcional):", fg="white", bg="#1a1a2e",
                 font=("Segoe UI", 12)).pack(pady=5)
        notas_text = scrolledtext.ScrolledText(ventana, height=4, width=30,
                                                bg="#2e2e2e", fg="white",
                                                font=("Segoe UI", 10))
        notas_text.pack(pady=5, padx=20)
        
        def guardar():
            try:
                peso = float(peso_entry.get())
                imc, _ = imc_bin_from_values(peso, self.estatura if self.estatura else 170)
                notas = notas_text.get("1.0", "end-1c")
                
                registrar_medicion(self.user_id, peso, imc, notas=notas)
                messagebox.showinfo("¡Listo!", "Medición registrada correctamente")
                ventana.destroy()
                self.mostrar_progreso_personal()
            except:
                messagebox.showerror("Error", "Ingresa un peso válido")
        
        tk.Button(ventana, text="💾 Guardar", bg="#00d9ff", fg="black", width=15,
                  font=("Segoe UI", 11, "bold"), command=guardar).pack(pady=20)
    
    # ========== ESTADÍSTICAS GLOBALES ==========
    def mostrar_estadisticas_globales(self):
        self.limpiar_pantalla()
        
        tk.Label(self.root, text="📊 Estadísticas del Sistema", fg="#00d9ff", bg="#0a0a0a",
                 font=("Segoe UI", 20, "bold")).pack(pady=15)
        
        data = cargar_feedback()
        stats = data.get("estadisticas", {})
        
        # Panel de estadísticas
        stats_container = tk.Frame(self.root, bg="#0a0a0a")
        stats_container.pack(expand=True, pady=20)
        
        # Rutinas
        rutinas_frame = tk.Frame(stats_container, bg="#0f4c75", bd=2, relief="solid", padx=20, pady=15)
        rutinas_frame.grid(row=0, column=0, padx=15, pady=15, sticky="nsew")
        
        tk.Label(rutinas_frame, text="💪 Rutinas", bg="#0f4c75", fg="#00d9ff",
                 font=("Segoe UI", 16, "bold")).pack(pady=10)
        tk.Label(rutinas_frame, text=f"Total evaluaciones: {stats.get('total_feedbacks_rutinas', 0)}",
                 bg="#0f4c75", fg="white", font=("Segoe UI", 12)).pack(pady=5)
        tk.Label(rutinas_frame, text=f"⭐ Promedio: {stats.get('promedio_calificacion_rutinas', 0)}/5.0",
                 bg="#0f4c75", fg="#ffd700", font=("Segoe UI", 13, "bold")).pack(pady=5)
        tk.Label(rutinas_frame, text=f"Adherencia: {stats.get('tasa_adherencia_rutinas', 0)}%",
                 bg="#0f4c75", fg="#4ade80", font=("Segoe UI", 12)).pack(pady=5)
        
        # Dietas
        dietas_frame = tk.Frame(stats_container, bg="#2d5016", bd=2, relief="solid", padx=20, pady=15)
        dietas_frame.grid(row=0, column=1, padx=15, pady=15, sticky="nsew")
        
        tk.Label(dietas_frame, text="🥗 Dietas", bg="#2d5016", fg="#43a047",
                 font=("Segoe UI", 16, "bold")).pack(pady=10)
        tk.Label(dietas_frame, text=f"Total evaluaciones: {stats.get('total_feedbacks_dietas', 0)}",
                 bg="#2d5016", fg="white", font=("Segoe UI", 12)).pack(pady=5)
        tk.Label(dietas_frame, text=f"⭐ Promedio: {stats.get('promedio_calificacion_dietas', 0)}/5.0",
                 bg="#2d5016", fg="#ffd700", font=("Segoe UI", 13, "bold")).pack(pady=5)
        tk.Label(dietas_frame, text=f"Adherencia: {stats.get('tasa_adherencia_dietas', 0)}%",
                 bg="#2d5016", fg="#4ade80", font=("Segoe UI", 12)).pack(pady=5)
        
        # Insights
        insights_frame = tk.Frame(self.root, bg="#1a1a2e", bd=2, relief="solid")
        insights_frame.pack(fill="x", padx=40, pady=20)
        
        tk.Label(insights_frame, text="💡 Insights del Sistema", bg="#1a1a2e", fg="#ffd700",
                 font=("Segoe UI", 14, "bold")).pack(pady=10)
        
        # Análisis simple
        if stats.get('total_feedbacks_rutinas', 0) > 0:
            tk.Label(insights_frame, 
                     text=f"✓ El sistema ha procesado {stats['total_feedbacks_rutinas']} rutinas exitosamente",
                     bg="#1a1a2e", fg="white", font=("Segoe UI", 11)).pack(anchor="w", padx=20, pady=3)
        
        if stats.get('promedio_calificacion_rutinas', 0) >= 4:
            tk.Label(insights_frame,
                     text="✓ Alta satisfacción en rutinas - El algoritmo está funcionando bien",
                     bg="#1a1a2e", fg="#4ade80", font=("Segoe UI", 11)).pack(anchor="w", padx=20, pady=3)
        
        if stats.get('tasa_adherencia_rutinas', 0) >= 70:
            tk.Label(insights_frame,
                     text="✓ Excelente adherencia - Los usuarios completan sus rutinas",
                     bg="#1a1a2e", fg="#4ade80", font=("Segoe UI", 11)).pack(anchor="w", padx=20, pady=3)
        
        tk.Label(insights_frame,
                 text="🤖 El sistema mejora continuamente con cada feedback recibido",
                 bg="#1a1a2e", fg="#00d9ff", font=("Segoe UI", 11, "italic")).pack(anchor="w", padx=20, pady=8)
        
        tk.Button(self.root, text="← Volver al Inicio", bg="#374151", fg="white", width=20,
                  font=("Segoe UI", 11, "bold"), command=self.mostrar_menu_principal).pack(pady=15)
    
    # ========== UTILIDADES ==========
    def limpiar_pantalla(self):
        for w in self.root.winfo_children():
            w.destroy()

def determine_label_from_plan(plan):
    cnt = {}
    for dia, info in plan.items():
        t = info.get("rutina_tipo", "Descanso")
        if t != "Descanso":
            cnt[t] = cnt.get(t,0) + 1
    if not cnt:
        return "Descanso"
    return max(cnt.items(), key=lambda x: x[1])[0]

if __name__ == "__main__":
    root = tk.Tk()
    app = GymApp(root)
    root.mainloop()
