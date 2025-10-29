"""
Sistema de Progresión y Periodización
Maneja cargas progresivas, deload weeks y adaptación automática
"""
import json
import os
from datetime import datetime, timedelta
from collections import defaultdict

PROGRESSION_FILE = "progression_data.json"

# -------------------------
# Configuración de Periodización
# -------------------------

PERIODIZATION_CONFIG = {
    "ciclo_duracion_semanas": 6,  # Ciclos de 6 semanas
    "deload_cada_semanas": 4,     # Semana de descarga cada 4
    "incremento_peso_porcentaje": {
        "Fuerza": 2.5,            # 2.5% por semana
        "Hipertrofia": 2.0,
        "Cardio": 5.0,            # 5% intensidad
        "HIIT": 3.0,
        "Fullbody": 2.0,
        "Yoga": 0.0               # Sin incremento en yoga
    },
    "incremento_volumen_porcentaje": 5.0  # 5% más series/reps
}

# -------------------------
# Gestión de Datos
# -------------------------

def cargar_progresion():
    """Carga datos de progresión"""
    if not os.path.exists(PROGRESSION_FILE):
        return {"usuarios": {}}
    try:
        with open(PROGRESSION_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return {"usuarios": {}}

def guardar_progresion(data):
    """Guarda datos de progresión"""
    with open(PROGRESSION_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

# -------------------------
# Cálculo de Cargas Progresivas
# -------------------------

def calcular_carga_inicial(tipo_rutina, nivel_usuario="principiante"):
    """
    Calcula cargas iniciales recomendadas según tipo de rutina y nivel
    
    Returns: dict con ejercicios y pesos/intensidad sugeridos
    """
    cargas_base = {
        "Fuerza": {
            "principiante": {
                "Press banca": {"kg": 20, "reps": 12, "series": 3},
                "Sentadillas": {"kg": 30, "reps": 12, "series": 3},
                "Peso muerto": {"kg": 40, "reps": 10, "series": 3},
                "Press militar": {"kg": 15, "reps": 12, "series": 3}
            },
            "intermedio": {
                "Press banca": {"kg": 40, "reps": 10, "series": 4},
                "Sentadillas": {"kg": 60, "reps": 10, "series": 4},
                "Peso muerto": {"kg": 80, "reps": 8, "series": 4},
                "Press militar": {"kg": 30, "reps": 10, "series": 4}
            },
            "avanzado": {
                "Press banca": {"kg": 70, "reps": 8, "series": 5},
                "Sentadillas": {"kg": 100, "reps": 8, "series": 5},
                "Peso muerto": {"kg": 120, "reps": 6, "series": 5},
                "Press militar": {"kg": 50, "reps": 8, "series": 5}
            }
        },
        "Hipertrofia": {
            "principiante": {
                "Curl bíceps": {"kg": 8, "reps": 15, "series": 3},
                "Extensiones tríceps": {"kg": 10, "reps": 15, "series": 3},
                "Press inclinado": {"kg": 25, "reps": 12, "series": 3}
            },
            "intermedio": {
                "Curl bíceps": {"kg": 15, "reps": 12, "series": 4},
                "Extensiones tríceps": {"kg": 20, "reps": 12, "series": 4},
                "Press inclinado": {"kg": 40, "reps": 10, "series": 4}
            },
            "avanzado": {
                "Curl bíceps": {"kg": 22, "reps": 10, "series": 5},
                "Extensiones tríceps": {"kg": 30, "reps": 10, "series": 5},
                "Press inclinado": {"kg": 60, "reps": 8, "series": 5}
            }
        },
        "Cardio": {
            "principiante": {
                "Cinta/Trote": {"intensidad": "60%", "duracion_min": 20},
                "Bicicleta": {"intensidad": "65%", "duracion_min": 25},
                "Elíptica": {"intensidad": "60%", "duracion_min": 20}
            },
            "intermedio": {
                "Cinta/Trote": {"intensidad": "70%", "duracion_min": 30},
                "Bicicleta": {"intensidad": "75%", "duracion_min": 35},
                "Elíptica": {"intensidad": "70%", "duracion_min": 30}
            },
            "avanzado": {
                "Cinta/Trote": {"intensidad": "80%", "duracion_min": 40},
                "Bicicleta": {"intensidad": "85%", "duracion_min": 45},
                "Elíptica": {"intensidad": "80%", "duracion_min": 40}
            }
        }
    }
    
    return cargas_base.get(tipo_rutina, {}).get(nivel_usuario, {})

def calcular_nivel_usuario(user_id):
    """
    Determina nivel del usuario según historial
    principiante: 0-8 semanas
    intermedio: 8-24 semanas
    avanzado: 24+ semanas
    """
    data = cargar_progresion()
    usuario_data = data.get("usuarios", {}).get(user_id, {})
    
    semanas_entrenando = usuario_data.get("semanas_totales", 0)
    
    if semanas_entrenando < 8:
        return "principiante"
    elif semanas_entrenando < 24:
        return "intermedio"
    else:
        return "avanzado"

def aplicar_progresion(ejercicio_actual, tipo_rutina, semana_en_ciclo):
    """
    Aplica progresión lineal a un ejercicio
    
    Args:
        ejercicio_actual: dict con kg, reps, series actuales
        tipo_rutina: str tipo de rutina
        semana_en_ciclo: int (1-6)
    
    Returns: dict con nueva carga
    """
    incremento = PERIODIZATION_CONFIG["incremento_peso_porcentaje"].get(tipo_rutina, 2.0)
    
    # Semana 4 = deload (reducir 30%)
    if semana_en_ciclo == 4:
        factor = 0.7  # Deload: 70% de la carga
    else:
        # Progresión lineal
        factor = 1 + (incremento / 100) * (semana_en_ciclo - 1)
    
    nuevo_ejercicio = ejercicio_actual.copy()
    
    if "kg" in ejercicio_actual:
        nuevo_ejercicio["kg"] = round(ejercicio_actual["kg"] * factor, 1)
    
    if "intensidad" in ejercicio_actual:
        # Para cardio, ajustar intensidad
        intensidad_actual = float(ejercicio_actual["intensidad"].rstrip("%"))
        nueva_intensidad = min(intensidad_actual * factor, 95.0)  # Max 95%
        nuevo_ejercicio["intensidad"] = f"{int(nueva_intensidad)}%"
    
    # Aumentar volumen en semanas 2, 3, 5, 6
    if semana_en_ciclo in [2, 3, 5, 6] and "series" in ejercicio_actual:
        vol_incremento = PERIODIZATION_CONFIG["incremento_volumen_porcentaje"]
        nuevo_ejercicio["series"] = max(ejercicio_actual["series"], 
                                        int(ejercicio_actual["series"] * (1 + vol_incremento/100)))
    
    return nuevo_ejercicio

# -------------------------
# Sistema de Semanas
# -------------------------

def registrar_semana_completada(user_id, semana_data):
    """
    Registra una semana de entrenamiento completada
    
    Args:
        semana_data: dict {
            "fecha_inicio": str,
            "fecha_fin": str,
            "dias_completados": int,
            "tipo_rutina": str,
            "ejercicios_realizados": list,
            "notas": str
        }
    """
    data = cargar_progresion()
    
    if "usuarios" not in data:
        data["usuarios"] = {}
    
    if user_id not in data["usuarios"]:
        data["usuarios"][user_id] = {
            "fecha_inicio_programa": datetime.now().isoformat(),
            "semanas_totales": 0,
            "semanas_historial": [],
            "ciclo_actual": 1,
            "semana_en_ciclo": 1,
            "cargas_actuales": {}
        }
    
    usuario = data["usuarios"][user_id]
    
    # Agregar semana al historial
    semana_data["timestamp"] = datetime.now().isoformat()
    semana_data["semana_numero"] = usuario["semanas_totales"] + 1
    usuario["semanas_historial"].append(semana_data)
    
    # Actualizar contadores
    usuario["semanas_totales"] += 1
    usuario["semana_en_ciclo"] += 1
    
    # Verificar si termina ciclo
    if usuario["semana_en_ciclo"] > PERIODIZATION_CONFIG["ciclo_duracion_semanas"]:
        usuario["ciclo_actual"] += 1
        usuario["semana_en_ciclo"] = 1
    
    guardar_progresion(data)
    return usuario

def obtener_plan_semana_actual(user_id, tipo_rutina):
    """
    Genera plan de la semana actual con cargas apropiadas
    """
    data = cargar_progresion()
    usuario = data.get("usuarios", {}).get(user_id, {})
    
    semana_en_ciclo = usuario.get("semana_en_ciclo", 1)
    nivel = calcular_nivel_usuario(user_id)
    
    # Obtener cargas base
    cargas_base = calcular_carga_inicial(tipo_rutina, nivel)
    
    # Si tiene historial, usar sus cargas actuales
    if usuario.get("cargas_actuales", {}).get(tipo_rutina):
        cargas_base = usuario["cargas_actuales"][tipo_rutina]
    
    # Aplicar progresión según semana en ciclo
    cargas_ajustadas = {}
    for ejercicio, datos in cargas_base.items():
        cargas_ajustadas[ejercicio] = aplicar_progresion(datos, tipo_rutina, semana_en_ciclo)
    
    # Actualizar cargas actuales del usuario
    if "cargas_actuales" not in usuario:
        usuario["cargas_actuales"] = {}
    usuario["cargas_actuales"][tipo_rutina] = cargas_ajustadas
    
    data["usuarios"][user_id] = usuario
    guardar_progresion(data)
    
    return {
        "semana_numero": usuario.get("semanas_totales", 0) + 1,
        "ciclo": usuario.get("ciclo_actual", 1),
        "semana_en_ciclo": semana_en_ciclo,
        "es_deload": semana_en_ciclo == 4,
        "nivel_usuario": nivel,
        "cargas": cargas_ajustadas
    }

def obtener_estadisticas_progresion(user_id):
    """
    Calcula estadísticas de progresión del usuario
    """
    data = cargar_progresion()
    usuario = data.get("usuarios", {}).get(user_id, {})
    
    if not usuario:
        return None
    
    historial = usuario.get("semanas_historial", [])
    
    if not historial:
        return {
            "semanas_totales": 0,
            "dias_totales_entrenados": 0,
            "tasa_adherencia_promedio": 0.0,
            "ciclos_completados": 0
        }
    
    # Calcular estadísticas
    dias_totales = sum(s.get("dias_completados", 0) for s in historial)
    dias_programados = len(historial) * 4  # Asumiendo 4 días por semana
    
    tasa_adherencia = (dias_totales / dias_programados * 100) if dias_programados > 0 else 0
    
    # Progresión de cargas (ejemplo con primer ejercicio)
    progresion_cargas = []
    for semana in historial:
        ejercicios = semana.get("ejercicios_realizados", [])
        if ejercicios:
            primer_ejer = ejercicios[0]
            if "kg" in primer_ejer:
                progresion_cargas.append({
                    "semana": semana.get("semana_numero", 0),
                    "kg": primer_ejer.get("kg", 0)
                })
    
    return {
        "semanas_totales": usuario.get("semanas_totales", 0),
        "dias_totales_entrenados": dias_totales,
        "tasa_adherencia_promedio": round(tasa_adherencia, 1),
        "ciclos_completados": usuario.get("ciclo_actual", 1) - 1,
        "nivel_actual": calcular_nivel_usuario(user_id),
        "progresion_cargas": progresion_cargas,
        "proxima_deload": 4 - usuario.get("semana_en_ciclo", 1) + 1 if usuario.get("semana_en_ciclo", 1) < 4 else "Esta semana"
    }

# -------------------------
# Análisis y Recomendaciones
# -------------------------

def analizar_sobreentrenamiento(user_id):
    """
    Detecta señales de sobreentrenamiento
    """
    data = cargar_progresion()
    usuario = data.get("usuarios", {}).get(user_id, {})
    historial = usuario.get("semanas_historial", [])
    
    if len(historial) < 3:
        return {"riesgo": "bajo", "mensaje": "Continúa con tu plan"}
    
    # Analizar últimas 3 semanas
    ultimas_3 = historial[-3:]
    
    # Señales de sobreentrenamiento:
    # 1. Adherencia decreciente
    adherencias = [s.get("dias_completados", 0) for s in ultimas_3]
    if adherencias[0] > adherencias[1] > adherencias[2]:
        return {
            "riesgo": "alto",
            "mensaje": "⚠️ Tu adherencia está disminuyendo. Considera una semana de descanso activo."
        }
    
    # 2. Muchas semanas consecutivas sin deload
    semanas_sin_deload = usuario.get("semana_en_ciclo", 1)
    if semanas_sin_deload >= 5:
        return {
            "riesgo": "medio",
            "mensaje": "💡 Próxima semana realiza un deload (reducir intensidad 30%)"
        }
    
    return {
        "riesgo": "bajo",
        "mensaje": "✅ Tu progresión es saludable. ¡Sigue así!"
    }

def generar_recomendacion_proxima_semana(user_id):
    """
    Genera recomendación inteligente para próxima semana
    """
    data = cargar_progresion()
    usuario = data.get("usuarios", {}).get(user_id, {})
    
    semana_en_ciclo = usuario.get("semana_en_ciclo", 1)
    semanas_totales = usuario.get("semanas_totales", 0)
    
    recomendaciones = []
    
    # Deload próxima semana
    if semana_en_ciclo == 3:
        recomendaciones.append("🔵 Próxima semana es DELOAD: Reduce peso 30% y enfócate en técnica")
    
    # Nueva en programa
    if semanas_totales < 4:
        recomendaciones.append("🟢 Semanas iniciales: Enfócate en aprender la técnica correcta")
    
    # Progresión consistente
    if semanas_totales >= 8:
        recomendaciones.append("🟡 Ya tienes experiencia: Incrementa gradualmente la intensidad")
    
    # Analizar adherencia
    historial = usuario.get("semanas_historial", [])
    if historial:
        ultima_adherencia = historial[-1].get("dias_completados", 0)
        if ultima_adherencia < 3:
            recomendaciones.append("🔴 Baja adherencia la semana pasada: Ajusta tu horario para cumplir al menos 4 días")
    
    if not recomendaciones:
        recomendaciones.append("✅ Continúa con tu progresión actual")
    
    return recomendaciones

# -------------------------
# Generación de Planes Detallados con Progresión
# -------------------------

def generar_plan_semanal_con_progresion(user_id, tipo_rutina_principal, dias_entrenamiento=4):
    """
    Genera plan semanal completo con cargas específicas y progresión
    """
    plan_semana = obtener_plan_semana_actual(user_id, tipo_rutina_principal)
    
    dias_semana = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"]
    
    # Seleccionar días de entrenamiento (ej: lunes, miércoles, viernes, sábado)
    import random
    dias_indices = sorted(random.sample(range(7), dias_entrenamiento))
    
    plan_detallado = {}
    
    cargas = plan_semana["cargas"]
    ejercicios_disponibles = list(cargas.keys())
    
    for i, dia in enumerate(dias_semana):
        if i in dias_indices:
            # Día de entrenamiento
            # Asignar 2-3 ejercicios
            num_ejercicios = 3 if not plan_semana["es_deload"] else 2
            ejercicios_dia = random.sample(ejercicios_disponibles, 
                                          min(num_ejercicios, len(ejercicios_disponibles)))
            
            plan_detallado[dia] = {
                "tipo": "Entrenamiento",
                "ejercicios": []
            }
            
            for ejercicio_nombre in ejercicios_dia:
                datos = cargas[ejercicio_nombre]
                plan_detallado[dia]["ejercicios"].append({
                    "nombre": ejercicio_nombre,
                    **datos
                })
        else:
            plan_detallado[dia] = {
                "tipo": "Descanso",
                "mensaje": "Recuperación activa: Caminar 20-30 min o estiramientos"
            }
    
    return {
        "plan_semanal": plan_detallado,
        "info_semana": {
            "semana_numero": plan_semana["semana_numero"],
            "ciclo": plan_semana["ciclo"],
            "es_deload": plan_semana["es_deload"],
            "nivel": plan_semana["nivel_usuario"]
        },
        "recomendaciones": generar_recomendacion_proxima_semana(user_id)
    }