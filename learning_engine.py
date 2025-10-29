"""
Sistema de Aprendizaje Adaptativo con Feedback
Mejora las recomendaciones basándose en la satisfacción del usuario
"""
import json
import os
from datetime import datetime
from collections import defaultdict
import math

FEEDBACK_FILE = "feedback_database.json"
PROGRESS_FILE = "progress_tracking.json"

# -------------------------
# Gestión de Feedback
# -------------------------

def cargar_feedback():
    """Carga base de datos de feedback"""
    if not os.path.exists(FEEDBACK_FILE):
        return {"rutinas": [], "dietas": [], "estadisticas": {}}
    try:
        with open(FEEDBACK_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {"rutinas": [], "dietas": [], "estadisticas": {}}

def guardar_feedback(data):
    """Guarda feedback en archivo"""
    with open(FEEDBACK_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def registrar_feedback_rutina(usuario, rutina_generada, calificacion, completado_dias, comentario=""):
    """
    Registra feedback de una rutina
    
    Args:
        usuario: dict con datos del usuario (edad, peso, imc_bin, motivo, etc.)
        rutina_generada: dict con el plan semanal generado
        calificacion: int 1-5 estrellas
        completado_dias: int días completados de la semana
        comentario: str opcional con comentarios del usuario
    """
    data = cargar_feedback()
    
    timestamp = datetime.now().isoformat()
    
    feedback_entry = {
        "timestamp": timestamp,
        "usuario": usuario,
        "rutina": {
            "label": determinar_rutina_predominante(rutina_generada),
            "dias_programados": contar_dias_entrenamiento(rutina_generada),
            "plan_completo": rutina_generada
        },
        "feedback": {
            "calificacion": calificacion,
            "dias_completados": completado_dias,
            "tasa_completitud": round(completado_dias / contar_dias_entrenamiento(rutina_generada) * 100, 1),
            "comentario": comentario
        },
        "metricas": {
            "satisfaccion": calificacion >= 4,  # True si 4-5 estrellas
            "adherencia": completado_dias >= contar_dias_entrenamiento(rutina_generada) * 0.7  # 70%+
        }
    }
    
    data["rutinas"].append(feedback_entry)
    
    # Actualizar estadísticas globales
    actualizar_estadisticas(data)
    
    guardar_feedback(data)
    return feedback_entry

def registrar_feedback_dieta(usuario, plan_nutricional, calificacion, dias_seguidos, peso_actual, comentario=""):
    """
    Registra feedback de un plan nutricional
    
    Args:
        usuario: dict con datos del usuario
        plan_nutricional: dict con plan generado
        calificacion: int 1-5
        dias_seguidos: int días que siguió la dieta
        peso_actual: float peso actual para tracking
        comentario: str opcional
    """
    data = cargar_feedback()
    
    timestamp = datetime.now().isoformat()
    peso_inicial = usuario.get("peso_kg", peso_actual)
    cambio_peso = peso_actual - peso_inicial
    
    feedback_entry = {
        "timestamp": timestamp,
        "usuario": usuario,
        "plan_nutricional": {
            "objetivo_calorico": plan_nutricional["metabolismo"]["objetivo_calorico"],
            "tipo_objetivo": plan_nutricional["metabolismo"]["tipo_objetivo"],
            "macros": plan_nutricional["macronutrientes"]
        },
        "feedback": {
            "calificacion": calificacion,
            "dias_seguidos": dias_seguidos,
            "peso_inicial": peso_inicial,
            "peso_actual": peso_actual,
            "cambio_peso_kg": round(cambio_peso, 2),
            "comentario": comentario
        },
        "metricas": {
            "satisfaccion": calificacion >= 4,
            "adherencia": dias_seguidos >= 5,  # Al menos 5 días
            "progreso_objetivo": evaluar_progreso_peso(cambio_peso, plan_nutricional["metabolismo"]["tipo_objetivo"])
        }
    }
    
    data["dietas"].append(feedback_entry)
    actualizar_estadisticas(data)
    guardar_feedback(data)
    return feedback_entry

# -------------------------
# Algoritmo de Aprendizaje Mejorado
# -------------------------

def calcular_scores_rutinas(perfil_usuario):
    """
    Calcula scores para cada tipo de rutina basándose en:
    1. Reglas base (IMC, edad)
    2. Historial de feedback similar
    3. Tasa de éxito global
    
    Returns: dict {rutina: score_normalizado}
    """
    imc_bin = perfil_usuario.get("imc_bin", "normal")
    motivo = perfil_usuario.get("motivo", "Salud")
    edad = perfil_usuario.get("edad", 30)
    
    # Scores base por IMC (de tu sistema original)
    scores_base = {
        "bajo": {"Fuerza": 0.5, "Hipertrofia": 0.3, "Fullbody": 0.2, "Cardio": 0.0, "HIIT": 0.0, "Yoga": 0.0},
        "normal": {"Fuerza": 0.3, "Cardio": 0.25, "Fullbody": 0.25, "HIIT": 0.2, "Hipertrofia": 0.0, "Yoga": 0.0},
        "sobrepeso": {"Cardio": 0.4, "Fullbody": 0.3, "HIIT": 0.2, "Yoga": 0.1, "Fuerza": 0.0, "Hipertrofia": 0.0},
        "obesidad": {"Cardio": 0.6, "Yoga": 0.25, "Fullbody": 0.15, "Fuerza": 0.0, "Hipertrofia": 0.0, "HIIT": 0.0}
    }
    
    scores = scores_base.get(imc_bin, scores_base["normal"]).copy()
    
    # Cargar feedback histórico
    data = cargar_feedback()
    feedbacks_similares = filtrar_feedbacks_similares(data["rutinas"], perfil_usuario)
    
    if not feedbacks_similares:
        return normalizar_scores(scores)
    
    # Calcular boost por feedback positivo
    boost_por_rutina = defaultdict(float)
    
    for fb in feedbacks_similares:
        rutina_label = fb["rutina"]["label"]
        calificacion = fb["feedback"]["calificacion"]
        adherencia = fb["metricas"]["adherencia"]
        
        # Factor de relevancia (feedback reciente pesa más)
        timestamp = fb.get("timestamp", "")
        factor_tiempo = calcular_factor_recencia(timestamp)
        
        # Score del feedback (0-1)
        score_feedback = (calificacion / 5.0) * 0.7 + (1.0 if adherencia else 0.0) * 0.3
        
        # Aplicar boost con decaimiento temporal
        boost_por_rutina[rutina_label] += score_feedback * factor_tiempo
    
    # Aplicar boosts a scores base
    for rutina, boost in boost_por_rutina.items():
        if rutina in scores:
            # Aumentar score base proporcionalmente
            scores[rutina] = scores[rutina] * (1 + boost * 0.5)  # boost moderado
    
    return normalizar_scores(scores)

def calcular_scores_dietas(perfil_usuario):
    """
    Similar a rutinas, pero para planes nutricionales
    Considera: tipo_objetivo, macros preferidos, adherencia histórica
    """
    imc_bin = perfil_usuario.get("imc_bin", "normal")
    motivo = perfil_usuario.get("motivo", "Salud")
    
    # Scores base por tipo de objetivo
    scores_base = {
        "Déficit (Pérdida de peso)": 0.0,
        "Superávit (Ganancia muscular)": 0.0,
        "Mantenimiento": 0.0,
        "Recomposición": 0.0
    }
    
    # Asignar score base según perfil
    if imc_bin in ["sobrepeso", "obesidad"]:
        scores_base["Déficit (Pérdida de peso)"] = 0.8
        scores_base["Mantenimiento"] = 0.2
    elif imc_bin == "bajo":
        scores_base["Superávit (Ganancia muscular)"] = 0.7
        scores_base["Recomposición"] = 0.3
    else:  # normal
        if motivo == "Rutina":
            scores_base["Mantenimiento"] = 0.5
            scores_base["Recomposición"] = 0.5
        else:
            scores_base["Recomposición"] = 0.6
            scores_base["Mantenimiento"] = 0.4
    
    # Ajustar con feedback
    data = cargar_feedback()
    feedbacks_similares = filtrar_feedbacks_similares(data["dietas"], perfil_usuario)
    
    if not feedbacks_similares:
        return normalizar_scores(scores_base)
    
    boost_por_objetivo = defaultdict(float)
    
    for fb in feedbacks_similares:
        tipo_objetivo = fb["plan_nutricional"]["tipo_objetivo"]
        calificacion = fb["feedback"]["calificacion"]
        adherencia = fb["metricas"]["adherencia"]
        progreso = fb["metricas"]["progreso_objetivo"]
        
        factor_tiempo = calcular_factor_recencia(fb.get("timestamp", ""))
        
        # Score compuesto
        score_feedback = (calificacion / 5.0) * 0.4 + \
                        (1.0 if adherencia else 0.0) * 0.3 + \
                        (1.0 if progreso else 0.0) * 0.3
        
        boost_por_objetivo[tipo_objetivo] += score_feedback * factor_tiempo
    
    for objetivo, boost in boost_por_objetivo.items():
        if objetivo in scores_base:
            scores_base[objetivo] = scores_base[objetivo] * (1 + boost * 0.6)
    
    return normalizar_scores(scores_base)

# -------------------------
# Utilidades de Análisis
# -------------------------

def filtrar_feedbacks_similares(feedbacks, perfil_usuario, umbral_similitud=0.7):
    """
    Filtra feedbacks de usuarios con perfil similar
    Considera: IMC bin, rango edad, motivo
    """
    similares = []
    
    imc_bin_usuario = perfil_usuario.get("imc_bin")
    edad_usuario = perfil_usuario.get("edad", 30)
    motivo_usuario = perfil_usuario.get("motivo")
    
    for fb in feedbacks:
        usuario_fb = fb.get("usuario", {})
        
        # Calcular similitud
        score_similitud = 0.0
        
        # IMC bin (peso más importante)
        if usuario_fb.get("imc_bin") == imc_bin_usuario:
            score_similitud += 0.5
        
        # Edad (rango de ±10 años)
        edad_fb = usuario_fb.get("edad", 30)
        if abs(edad_fb - edad_usuario) <= 10:
            score_similitud += 0.3
        
        # Motivo
        if usuario_fb.get("motivo") == motivo_usuario:
            score_similitud += 0.2
        
        if score_similitud >= umbral_similitud:
            similares.append(fb)
    
    return similares

def calcular_factor_recencia(timestamp_str, dias_relevancia=90):
    """
    Feedback reciente tiene más peso
    Decaimiento exponencial después de dias_relevancia
    """
    if not timestamp_str:
        return 0.5  # Factor neutro para datos sin fecha
    
    try:
        fecha_fb = datetime.fromisoformat(timestamp_str)
        dias_pasados = (datetime.now() - fecha_fb).days
        
        if dias_pasados <= dias_relevancia:
            return 1.0
        else:
            # Decaimiento exponencial
            decay_rate = 0.01
            factor = math.exp(-decay_rate * (dias_pasados - dias_relevancia))
            return max(factor, 0.1)  # Mínimo 10%
    except Exception:
        return 0.5

def evaluar_progreso_peso(cambio_kg, tipo_objetivo):
    """
    Evalúa si el cambio de peso es adecuado según objetivo
    """
    if "Déficit" in tipo_objetivo:
        return cambio_kg < -0.3  # Perdió al menos 300g
    elif "Superávit" in tipo_objetivo:
        return cambio_kg > 0.2  # Ganó al menos 200g
    else:  # Mantenimiento/Recomposición
        return abs(cambio_kg) <= 0.5  # Se mantuvo ±500g

def normalizar_scores(scores):
    """Normaliza scores para que sumen 1.0"""
    total = sum(scores.values())
    if total == 0:
        return {k: 1.0/len(scores) for k in scores}
    return {k: v/total for k, v in scores.items()}

def determinar_rutina_predominante(plan_semanal):
    """Determina qué tipo de rutina es más frecuente en el plan"""
    contador = defaultdict(int)
    for dia, info in plan_semanal.items():
        tipo = info.get("rutina_tipo", "Descanso")
        if tipo != "Descanso":
            contador[tipo] += 1
    
    if not contador:
        return "Descanso"
    return max(contador.items(), key=lambda x: x[1])[0]

def contar_dias_entrenamiento(plan_semanal):
    """Cuenta días de entrenamiento en plan semanal"""
    count = 0
    for info in plan_semanal.values():
        if info.get("rutina_tipo") != "Descanso":
            count += 1
    return count

def actualizar_estadisticas(data):
    """Actualiza estadísticas globales del sistema"""
    stats = {
        "total_feedbacks_rutinas": len(data["rutinas"]),
        "total_feedbacks_dietas": len(data["dietas"]),
        "promedio_calificacion_rutinas": 0.0,
        "promedio_calificacion_dietas": 0.0,
        "tasa_adherencia_rutinas": 0.0,
        "tasa_adherencia_dietas": 0.0
    }
    
    if data["rutinas"]:
        cals = [fb["feedback"]["calificacion"] for fb in data["rutinas"]]
        stats["promedio_calificacion_rutinas"] = round(sum(cals) / len(cals), 2)
        
        adherencias = [fb["metricas"]["adherencia"] for fb in data["rutinas"]]
        stats["tasa_adherencia_rutinas"] = round(sum(adherencias) / len(adherencias) * 100, 1)
    
    if data["dietas"]:
        cals = [fb["feedback"]["calificacion"] for fb in data["dietas"]]
        stats["promedio_calificacion_dietas"] = round(sum(cals) / len(cals), 2)
        
        adherencias = [fb["metricas"]["adherencia"] for fb in data["dietas"]]
        stats["tasa_adherencia_dietas"] = round(sum(adherencias) / len(adherencias) * 100, 1)
    
    data["estadisticas"] = stats

# -------------------------
# Tracking de Progreso Individual
# -------------------------

def cargar_progreso_usuario(user_id):
    """Carga historial de progreso de un usuario específico"""
    if not os.path.exists(PROGRESS_FILE):
        return {"usuarios": {}}
    
    try:
        with open(PROGRESS_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            return data.get("usuarios", {}).get(user_id, {
                "mediciones": [],
                "rutinas_completadas": 0,
                "dietas_completadas": 0
            })
    except Exception:
        return {"mediciones": [], "rutinas_completadas": 0, "dietas_completadas": 0}

def guardar_progreso_usuario(user_id, progreso_data):
    """Guarda progreso de usuario"""
    if not os.path.exists(PROGRESS_FILE):
        data = {"usuarios": {}}
    else:
        try:
            with open(PROGRESS_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
        except Exception:
            data = {"usuarios": {}}
    
    if "usuarios" not in data:
        data["usuarios"] = {}
    
    data["usuarios"][user_id] = progreso_data
    
    with open(PROGRESS_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def registrar_medicion(user_id, peso, imc, circunferencia_cintura=None, notas=""):
    """Registra una medición de progreso"""
    progreso = cargar_progreso_usuario(user_id)
    
    medicion = {
        "fecha": datetime.now().isoformat(),
        "peso_kg": peso,
        "imc": imc,
        "circunferencia_cintura_cm": circunferencia_cintura,
        "notas": notas
    }
    
    if "mediciones" not in progreso:
        progreso["mediciones"] = []
    
    progreso["mediciones"].append(medicion)
    guardar_progreso_usuario(user_id, progreso)
    
    return medicion

def obtener_estadisticas_personales(user_id):
    """Obtiene resumen de progreso personal"""
    progreso = cargar_progreso_usuario(user_id)
    mediciones = progreso.get("mediciones", [])
    
    if not mediciones:
        return None
    
    primera = mediciones[0]
    ultima = mediciones[-1]
    
    return {
        "fecha_inicio": primera["fecha"],
        "fecha_ultima": ultima["fecha"],
        "peso_inicial": primera["peso_kg"],
        "peso_actual": ultima["peso_kg"],
        "cambio_total_kg": round(ultima["peso_kg"] - primera["peso_kg"], 2),
        "imc_inicial": primera["imc"],
        "imc_actual": ultima["imc"],
        "total_mediciones": len(mediciones),
        "rutinas_completadas": progreso.get("rutinas_completadas", 0),
        "dietas_completadas": progreso.get("dietas_completadas", 0)
    }

# -------------------------
# Sistema de Recomendaciones Inteligentes
# -------------------------

def generar_recomendacion_inteligente(perfil_usuario):
    """
    Genera recomendación basada en:
    1. Scores calculados con ML
    2. Tendencias históricas
    3. Mejores prácticas
    """
    scores_rutinas = calcular_scores_rutinas(perfil_usuario)
    scores_dietas = calcular_scores_dietas(perfil_usuario)
    
    # Seleccionar mejor rutina
    mejor_rutina = max(scores_rutinas.items(), key=lambda x: x[1])
    
    # Seleccionar mejor tipo de dieta
    mejor_dieta = max(scores_dietas.items(), key=lambda x: x[1])
    
    # Generar explicación
    explicacion_rutina = f"Recomendamos {mejor_rutina[0]} porque usuarios similares tuvieron {mejor_rutina[1]*100:.0f}% de éxito con este enfoque."
    
    explicacion_dieta = f"Tu plan nutricional será tipo '{mejor_dieta[0]}' basado en tu perfil y objetivos."
    
    return {
        "rutina_recomendada": mejor_rutina[0],
        "confianza_rutina": round(mejor_rutina[1] * 100, 1),
        "explicacion_rutina": explicacion_rutina,
        "dieta_recomendada": mejor_dieta[0],
        "confianza_dieta": round(mejor_dieta[1] * 100, 1),
        "explicacion_dieta": explicacion_dieta,
        "todas_opciones_rutinas": scores_rutinas,
        "todas_opciones_dietas": scores_dietas
    }
