"""
Sistema de Nutrición Personalizada
Calcula necesidades calóricas y genera planes de comidas
"""
import random

# -------------------------
# Cálculos Nutricionales
# -------------------------

def calcular_tmb(peso, estatura, edad, genero):
    """
    Calcula Tasa Metabólica Basal usando fórmula Mifflin-St Jeor
    Devuelve calorías diarias en reposo
    """
    if genero == "Hombre":
        tmb = (10 * peso) + (6.25 * estatura) - (5 * edad) + 5
    else:  # Mujer
        tmb = (10 * peso) + (6.25 * estatura) - (5 * edad) - 161
    return round(tmb)

def calcular_tdee(tmb, dias_entrenamiento):
    """
    Calcula Total Daily Energy Expenditure (gasto calórico total)
    Según nivel de actividad física
    """
    # Factor de actividad basado en días de entrenamiento
    if dias_entrenamiento <= 2:
        factor = 1.375  # Ligera actividad
    elif dias_entrenamiento <= 4:
        factor = 1.55   # Actividad moderada
    elif dias_entrenamiento <= 6:
        factor = 1.725  # Actividad intensa
    else:
        factor = 1.9    # Actividad muy intensa
    
    return round(tmb * factor)

def calcular_objetivo_calorico(tdee, motivo, imc_bin):
    """
    Ajusta calorías según objetivo del usuario
    """
    if motivo == "Nuevo" or imc_bin in ["sobrepeso", "obesidad"]:
        # Déficit calórico para pérdida de peso
        if imc_bin == "obesidad":
            deficit = 500  # Déficit agresivo pero seguro
        else:
            deficit = 300  # Déficit moderado
        objetivo = tdee - deficit
        tipo_objetivo = "Déficit (Pérdida de peso)"
    
    elif imc_bin == "bajo":
        # Superávit para ganancia muscular
        surplus = 300
        objetivo = tdee + surplus
        tipo_objetivo = "Superávit (Ganancia muscular)"
    
    else:  # normal + motivos salud/rutina
        if motivo == "Rutina":
            # Mantenimiento
            objetivo = tdee
            tipo_objetivo = "Mantenimiento"
        else:  # Salud
            # Leve superávit para composición corporal
            objetivo = tdee + 100
            tipo_objetivo = "Recomposición"
    
    return round(objetivo), tipo_objetivo

def calcular_macronutrientes(calorias_objetivo, objetivo_tipo, imc_bin):
    """
    Distribuye macronutrientes (proteína, carbohidratos, grasas)
    según objetivo y condición física
    """
    # Proteína: 1.6-2.2g por kg de peso (usamos % de calorías)
    if objetivo_tipo in ["Superávit (Ganancia muscular)", "Recomposición"]:
        prot_pct = 0.30  # 30% proteína para hipertrofia
    elif imc_bin == "obesidad":
        prot_pct = 0.35  # Alta proteína preserva músculo en déficit
    else:
        prot_pct = 0.25  # Balance normal
    
    # Grasas saludables
    if imc_bin in ["sobrepeso", "obesidad"]:
        grasa_pct = 0.25  # Moderada para déficit
    else:
        grasa_pct = 0.30  # Suficiente para hormonas
    
    # Carbohidratos: el resto
    carbs_pct = 1.0 - prot_pct - grasa_pct
    
    # Convertir a gramos (1g prot = 4cal, 1g carbs = 4cal, 1g grasa = 9cal)
    proteina_g = round((calorias_objetivo * prot_pct) / 4)
    carbos_g = round((calorias_objetivo * carbs_pct) / 4)
    grasas_g = round((calorias_objetivo * grasa_pct) / 9)
    
    return {
        "proteinas": proteina_g,
        "carbohidratos": carbos_g,
        "grasas": grasas_g,
        "calorias": calorias_objetivo
    }

# -------------------------
# Base de Datos de Alimentos
# -------------------------

ALIMENTOS = {
    "proteinas": {
        "alto": [
            ("Pechuga de pollo (150g)", 240, 45, 0, 3),
            ("Huevos (3 unidades)", 210, 18, 2, 15),
            ("Atún enlatado (1 lata)", 120, 25, 0, 1),
            ("Carne molida magra (150g)", 280, 35, 0, 12),
            ("Salmón (150g)", 300, 35, 0, 17),
            ("Yogur griego (200g)", 140, 20, 8, 2),
        ],
        "medio": [
            ("Lentejas cocidas (200g)", 230, 18, 40, 1),
            ("Frijoles negros (200g)", 220, 15, 40, 1),
            ("Quinoa cocida (150g)", 180, 7, 30, 3),
            ("Requesón bajo en grasa (150g)", 120, 18, 5, 2),
        ]
    },
    "carbohidratos": {
        "complejos": [
            ("Arroz integral (150g)", 180, 4, 38, 2),
            ("Papa al horno (200g)", 160, 4, 37, 0),
            ("Avena (80g)", 300, 10, 54, 6),
            ("Camote (200g)", 180, 4, 41, 0),
            ("Pan integral (2 rebanadas)", 140, 6, 24, 2),
            ("Pasta integral (100g)", 310, 13, 63, 2),
        ],
        "simples": [
            ("Plátano", 105, 1, 27, 0),
            ("Manzana", 95, 0, 25, 0),
            ("Naranja", 60, 1, 15, 0),
            ("Uvas (150g)", 100, 1, 26, 0),
        ]
    },
    "grasas_saludables": [
        ("Aguacate (1/2 unidad)", 120, 2, 6, 11),
        ("Almendras (30g)", 170, 6, 6, 15),
        ("Aceite de oliva (1 cdta)", 120, 0, 0, 14),
        ("Nueces (30g)", 185, 4, 4, 18),
        ("Mantequilla de maní (2 cdas)", 190, 8, 7, 16),
    ],
    "vegetales": [
        ("Brócoli al vapor (150g)", 50, 4, 10, 0),
        ("Espinacas (100g)", 23, 3, 4, 0),
        ("Zanahoria (100g)", 41, 1, 10, 0),
        ("Tomate (1 unidad)", 22, 1, 5, 0),
        ("Pimientos (100g)", 31, 1, 6, 0),
        ("Ensalada verde mixta", 25, 2, 5, 0),
    ]
}

# -------------------------
# Generador de Plan de Comidas
# -------------------------

def generar_plan_comidas(macros, objetivo_tipo, dias_entrenamiento):
    """
    Genera plan de comidas diario con 4-5 tiempos de comida
    Retorna diccionario con desayuno, almuerzo, cena, snacks
    """
    # Distribuir calorías por tiempo de comida
    cal_total = macros["calorias"]
    
    if dias_entrenamiento >= 4:
        # Más comidas para deportistas activos
        comidas = {
            "Desayuno": cal_total * 0.25,
            "Snack Pre-Entreno": cal_total * 0.15,
            "Almuerzo": cal_total * 0.30,
            "Merienda": cal_total * 0.10,
            "Cena": cal_total * 0.20
        }
    else:
        comidas = {
            "Desayuno": cal_total * 0.30,
            "Almuerzo": cal_total * 0.35,
            "Merienda": cal_total * 0.10,
            "Cena": cal_total * 0.25
        }
    
    plan_diario = {}
    
    for tiempo, calorias_tiempo in comidas.items():
        if "Desayuno" in tiempo:
            plan_diario[tiempo] = generar_desayuno(calorias_tiempo)
        elif "Almuerzo" in tiempo or "Cena" in tiempo:
            plan_diario[tiempo] = generar_comida_principal(calorias_tiempo, objetivo_tipo)
        else:  # Snacks/Meriendas
            plan_diario[tiempo] = generar_snack(calorias_tiempo)
    
    return plan_diario

def generar_desayuno(calorias_objetivo):
    """Genera opciones de desayuno balanceado"""
    opciones = [
        {
            "nombre": "Desayuno Proteico",
            "alimentos": [
                ALIMENTOS["proteinas"]["alto"][1],  # Huevos
                ALIMENTOS["carbohidratos"]["complejos"][4],  # Pan integral
                ALIMENTOS["grasas_saludables"][0],  # Aguacate
                ("Café o té", 0, 0, 0, 0)
            ]
        },
        {
            "nombre": "Bowl de Avena",
            "alimentos": [
                ALIMENTOS["carbohidratos"]["complejos"][2],  # Avena
                ALIMENTOS["proteinas"]["alto"][5],  # Yogur griego
                ALIMENTOS["carbohidratos"]["simples"][0],  # Plátano
                ALIMENTOS["grasas_saludables"][1],  # Almendras
            ]
        },
        {
            "nombre": "Desayuno Rápido",
            "alimentos": [
                ALIMENTOS["proteinas"]["medio"][3],  # Requesón
                ALIMENTOS["carbohidratos"]["simples"][2],  # Naranja
                ALIMENTOS["grasas_saludables"][3],  # Nueces
                ("Té verde", 0, 0, 0, 0)
            ]
        }
    ]
    return random.choice(opciones)

def generar_comida_principal(calorias_objetivo, objetivo_tipo):
    """Genera almuerzo o cena completo"""
    # Seleccionar proteína principal
    if objetivo_tipo in ["Superávit (Ganancia muscular)", "Recomposición"]:
        proteina = random.choice(ALIMENTOS["proteinas"]["alto"])
    else:
        # Mix de proteínas
        todas_prot = ALIMENTOS["proteinas"]["alto"] + ALIMENTOS["proteinas"]["medio"]
        proteina = random.choice(todas_prot)
    
    # Carbohidrato
    if objetivo_tipo == "Déficit (Pérdida de peso)":
        # Menos carbs, más vegetales
        carb = random.choice(ALIMENTOS["carbohidratos"]["complejos"][:3])
        porcion_carb = 0.7  # Porción reducida
    else:
        carb = random.choice(ALIMENTOS["carbohidratos"]["complejos"])
        porcion_carb = 1.0
    
    # Vegetales (siempre)
    veg = random.choice(ALIMENTOS["vegetales"])
    
    # Grasa saludable
    grasa = random.choice(ALIMENTOS["grasas_saludables"][:3])
    
    return {
        "nombre": f"{proteina[0].split('(')[0].strip()} con {carb[0].split('(')[0].strip()}",
        "alimentos": [proteina, carb, veg, grasa],
        "nota_porcion": f"Carbohidrato al {int(porcion_carb*100)}%" if porcion_carb < 1 else ""
    }

def generar_snack(calorias_objetivo):
    """Genera snack o merienda"""
    opciones = [
        {
            "nombre": "Snack Proteico",
            "alimentos": [
                ALIMENTOS["proteinas"]["alto"][5],  # Yogur
                ALIMENTOS["carbohidratos"]["simples"][0],  # Fruta
            ]
        },
        {
            "nombre": "Snack Energético",
            "alimentos": [
                ALIMENTOS["grasas_saludables"][1],  # Almendras
                ALIMENTOS["carbohidratos"]["simples"][1],  # Manzana
            ]
        },
        {
            "nombre": "Snack Pre/Post Entreno",
            "alimentos": [
                ALIMENTOS["proteinas"]["medio"][3],  # Requesón
                ALIMENTOS["carbohidratos"]["simples"][0],  # Plátano
            ]
        }
    ]
    return random.choice(opciones)

# -------------------------
# Función Principal de Integración
# -------------------------

def generar_plan_nutricional_completo(peso, estatura, edad, genero, motivo, imc_bin, dias_entrenamiento):
    """
    Función principal que genera el plan nutricional completo
    Retorna diccionario con toda la información nutricional
    """
    # 1. Calcular TMB
    tmb = calcular_tmb(peso, estatura, edad, genero)
    
    # 2. Calcular TDEE
    tdee = calcular_tdee(tmb, dias_entrenamiento)
    
    # 3. Calcular objetivo calórico
    calorias_objetivo, tipo_objetivo = calcular_objetivo_calorico(tdee, motivo, imc_bin)
    
    # 4. Calcular macronutrientes
    macros = calcular_macronutrientes(calorias_objetivo, tipo_objetivo, imc_bin)
    
    # 5. Generar plan de comidas
    plan_comidas = generar_plan_comidas(macros, tipo_objetivo, dias_entrenamiento)
    
    # 6. Generar recomendaciones adicionales
    recomendaciones = generar_recomendaciones(imc_bin, objetivo_tipo=tipo_objetivo)
    
    return {
        "metabolismo": {
            "tmb": tmb,
            "tdee": tdee,
            "objetivo_calorico": calorias_objetivo,
            "tipo_objetivo": tipo_objetivo
        },
        "macronutrientes": macros,
        "plan_comidas": plan_comidas,
        "recomendaciones": recomendaciones,
        "hidratacion_litros": calcular_hidratacion(peso, dias_entrenamiento)
    }

def generar_recomendaciones(imc_bin, objetivo_tipo):
    """Genera tips personalizados según perfil"""
    recomendaciones = []
    
    if "Déficit" in objetivo_tipo:
        recomendaciones.extend([
            "🥗 Prioriza alimentos altos en volumen pero bajos en calorías (verduras)",
            "⏰ Considera ayuno intermitente 16/8 si te adaptas bien",
            "💧 Bebe agua antes de las comidas para aumentar saciedad"
        ])
    
    if "Superávit" in objetivo_tipo:
        recomendaciones.extend([
            "💪 Consume proteína cada 3-4 horas para síntesis muscular",
            "🍚 No temas a los carbohidratos, son tu combustible",
            "😴 Duerme 7-9 horas para recuperación muscular"
        ])
    
    if imc_bin == "obesidad":
        recomendaciones.append("⚠️ Considera consultar con nutricionista profesional")
    
    # Recomendaciones generales
    recomendaciones.extend([
        "🥤 Evita bebidas azucaradas y alcohol",
        "🍽️ Come despacio y mastica bien (20 min por comida)",
        "📊 Pésate 1 vez por semana, misma hora y condiciones"
    ])
    
    return recomendaciones

def calcular_hidratacion(peso, dias_entrenamiento):
    """Calcula necesidad de agua diaria"""
    # Base: 35ml por kg de peso
    base = (peso * 35) / 1000  # en litros
    
    # Ajuste por actividad física
    if dias_entrenamiento >= 5:
        extra = 1.0
    elif dias_entrenamiento >= 3:
        extra = 0.5
    else:
        extra = 0.0
    
    return round(base + extra, 1)