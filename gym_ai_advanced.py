import json
import os
import random
import math
from datetime import datetime, timedelta
from collections import defaultdict
import pickle

# Importar motor de inferencia
try:
    from motor_inferencia import MotorInferencia
    MOTOR_INFERENCIA_DISPONIBLE = True
except ImportError:
    MOTOR_INFERENCIA_DISPONIBLE = False
    print("⚠ Motor de inferencia no disponible")

class AdvancedGymAI:
    """
    Sistema de IA avanzado que APRENDE y GENERA rutinas por su cuenta.
    
    CARACTERÍSTICAS DE APRENDIZAJE:
    1. Red neuronal simple para predecir satisfacción
    2. Algoritmo genético para generar nuevas combinaciones de ejercicios
    3. Sistema de recompensas que premia rutinas exitosas
    4. Memoria de patrones que identifica qué funciona mejor
    5. Generación automática de nuevas rutinas basadas en datos históricos
    """
    
    def __init__(self, data_file='gym_ai_advanced_data.json'):
        self.data_file = data_file
        self.user_data = {}
        
        # Base de conocimiento inicial (seed data)
        self.ejercicios_base = {
            'pecho': {
                'compuestos': ['Press banca', 'Press inclinado', 'Fondos en paralelas', 'Press declinado'],
                'aislamiento': ['Aperturas con mancuernas', 'Cruces en polea', 'Pullover', 'Press con mancuernas']
            },
            'espalda': {
                'compuestos': ['Dominadas', 'Peso muerto', 'Remo con barra', 'Remo en polea'],
                'aislamiento': ['Jalón al pecho', 'Remo con mancuerna', 'Face pulls', 'Pullover espalda']
            },
            'piernas': {
                'compuestos': ['Sentadilla', 'Prensa', 'Peso muerto rumano', 'Sentadilla búlgara'],
                'aislamiento': ['Extensiones de cuádriceps', 'Curl femoral', 'Elevación de pantorrillas', 'Hip thrust']
            },
            'hombros': {
                'compuestos': ['Press militar', 'Press Arnold', 'Remo al mentón'],
                'aislamiento': ['Elevaciones laterales', 'Elevaciones frontales', 'Pájaros', 'Face pulls']
            },
            'brazos': {
                'compuestos': ['Press cerrado', 'Dominadas cerradas'],
                'aislamiento': ['Curl con barra', 'Extensiones de tríceps', 'Curl martillo', 'Curl concentrado', 'Fondos tríceps']
            },
            'core': {
                'compuestos': ['Plancha', 'Crunches', 'Elevación de piernas', 'Russian twists']
            },
            'cardio': ['Caminata', 'Trote', 'HIIT', 'Bicicleta', 'Remo', 'Elíptica', 'Escaladora', 'Sprints']
        }
        
        # Sistema de aprendizaje
        self.learning_system = {
            'rutinas_generadas': [],  # Todas las rutinas que ha creado el sistema
            'historico_usuarios': [],  # Histórico de todos los usuarios
            'patrones_exitosos': {},   # Patrones que han funcionado bien
            'combinaciones_ejercicios': {},  # Qué ejercicios funcionan bien juntos
            'parametros_optimos': {},  # Series, reps, descansos óptimos por perfil
            'generacion': 0,  # Generación actual del sistema (mejora con el tiempo)
            'tasa_aprendizaje': 0.1,  # Qué tanto aprende de cada feedback
            'factor_exploracion': 0.2  # Probabilidad de probar cosas nuevas
        }
        
        # Métricas de rendimiento del sistema
        self.metricas = {
            'precision_predicciones': [],
            'satisfaccion_promedio_por_generacion': [],
            'mejores_rutinas': []
        }
        
        # Inicializar motor de inferencia
        self.motor_inferencia = None
        
        self.load_data()
        
        # Cargar motor de inferencia con los datos
        if MOTOR_INFERENCIA_DISPONIBLE:
            self.motor_inferencia = MotorInferencia({
                'learning_system': self.learning_system,
                'historico_usuarios': self.learning_system.get('historico_usuarios', []),
                'patrones_exitosos': self.learning_system.get('patrones_exitosos', {})
            })
            print("✓ Motor de inferencia integrado")
    
    def load_data(self):
        """Carga el conocimiento previo del sistema"""
        if os.path.exists(self.data_file):
            try:
                with open(self.data_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.learning_system = data.get('learning_system', self.learning_system)
                    self.metricas = data.get('metricas', self.metricas)
                    print(f"✓ Conocimiento cargado - Generación {self.learning_system['generacion']}")
            except Exception as e:
                print(f"Iniciando con conocimiento base")
    
    def save_data(self):
        """Guarda el conocimiento aprendido"""
        data = {
            'learning_system': self.learning_system,
            'metricas': self.metricas,
            'last_update': datetime.now().isoformat()
        }
        with open(self.data_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    
    def calcular_imc(self, peso, altura):
        """Calcula el Índice de Masa Corporal"""
        return peso / (altura ** 2)
    
    def crear_perfil_usuario(self, datos):
        """Crea un perfil numérico del usuario para el sistema de ML"""
        imc = self.calcular_imc(datos['peso'], datos['altura'])
        
        # Codificación numérica del perfil
        nivel_map = {'principiante': 1, 'intermedio': 2, 'avanzado': 3}
        objetivo_map = {'perder_peso': 1, 'ganar_masa': 2, 'resistencia': 3, 'fuerza': 4}
        
        perfil = {
            'edad': datos['edad'],
            'peso': datos['peso'],
            'altura': datos['altura'],
            'imc': imc,
            'nivel_num': nivel_map[datos['nivel_experiencia']],
            'objetivo_num': objetivo_map[datos['objetivo']],
            'dias': datos['dias_entrenamiento'],
            'nivel_str': datos['nivel_experiencia'],
            'objetivo_str': datos['objetivo']
        }
        
        return perfil
    
    def buscar_patrones_similares(self, perfil_actual):
        """
        FUNCIÓN CLAVE DE APRENDIZAJE:
        Busca en el histórico usuarios con perfiles similares y sus rutinas exitosas.
        Esto permite que el sistema aprenda de experiencias pasadas.
        """
        usuarios_similares = []
        
        for usuario in self.learning_system['historico_usuarios']:
            # Calcular similitud entre perfiles (distancia euclidiana)
            similitud = self._calcular_similitud_perfil(perfil_actual, usuario['perfil'])
            
            if similitud > 0.7:  # Umbral de similitud
                usuarios_similares.append({
                    'usuario': usuario,
                    'similitud': similitud
                })
        
        # Ordenar por similitud y satisfacción
        usuarios_similares.sort(key=lambda x: (x['similitud'], x['usuario'].get('satisfaccion', 0)), reverse=True)
        
        return usuarios_similares[:5]  # Top 5 más similares
    
    def _calcular_similitud_perfil(self, perfil1, perfil2):
        """
        Calcula qué tan similar es un perfil a otro usando distancia normalizada.
        Retorna un valor entre 0 y 1 (1 = idénticos, 0 = muy diferentes)
        """
        # Normalizar y calcular diferencias
        diff_edad = abs(perfil1['edad'] - perfil2['edad']) / 100
        diff_imc = abs(perfil1['imc'] - perfil2['imc']) / 20
        diff_nivel = abs(perfil1['nivel_num'] - perfil2['nivel_num']) / 3
        diff_objetivo = 0 if perfil1['objetivo_str'] == perfil2['objetivo_str'] else 1
        diff_dias = abs(perfil1['dias'] - perfil2['dias']) / 7
        
        # Calcular distancia total
        distancia = math.sqrt(
            diff_edad**2 + 
            diff_imc**2 + 
            diff_nivel**2 + 
            diff_objetivo**2 + 
            diff_dias**2
        )
        
        # Convertir distancia a similitud (inversamente proporcional)
        similitud = 1 / (1 + distancia)
        
        return similitud
    
    def generar_rutina_inteligente(self, perfil):
        """
        CORAZÓN DEL SISTEMA DE IA:
        Genera una rutina completamente nueva basándose en:
        1. Patrones aprendidos de usuarios similares
        2. Combinaciones exitosas de ejercicios
        3. Parámetros óptimos encontrados
        4. Exploración de nuevas combinaciones (factor de innovación)
        5. Predicciones del motor de inferencia (NUEVO)
        """
        print("\n🧠 Generando rutina con IA...")
        
        # NUEVO: Usar motor de inferencia para predicciones
        if self.motor_inferencia:
            print("\n🔮 Consultando motor de inferencia...")
            
            # Predecir parámetros óptimos
            parametros_inferidos = self.motor_inferencia.inferir_parametros_optimos(perfil)
            print(f"   → Parámetros inferidos: {parametros_inferidos['series']} series, "
                  f"{parametros_inferidos['repeticiones_min']}-{parametros_inferidos['repeticiones_max']} reps")
            
            # Clasificar usuario
            clasificacion = self.motor_inferencia.clasificar_usuario(perfil)
            print(f"   → Usuario clasificado como: {clasificacion['categoria'].upper()}")
            
            # Guardar para uso posterior
            self.parametros_inferidos = parametros_inferidos
            self.clasificacion_usuario = clasificacion
        else:
            self.parametros_inferidos = None
            self.clasificacion_usuario = None
        
        # Buscar patrones de éxito en perfiles similares
        usuarios_similares = self.buscar_patrones_similares(perfil)
        
        # Decidir si explorar (probar algo nuevo) o explotar (usar conocimiento)
        explorar = random.random() < self.learning_system['factor_exploracion']
        
        if explorar or len(usuarios_similares) == 0:
            print("   → Modo EXPLORACIÓN: Generando rutina innovadora")
            rutina = self._generar_rutina_exploracion(perfil)
        else:
            print(f"   → Modo EXPLOTACIÓN: Basándose en {len(usuarios_similares)} perfiles similares exitosos")
            rutina = self._generar_rutina_aprendida(perfil, usuarios_similares)
        
        # NUEVO: Aplicar parámetros inferidos si están disponibles
        if self.parametros_inferidos and self.parametros_inferidos['confianza'] >= 0.6:
            print("\n   ✓ Aplicando parámetros optimizados por motor de inferencia")
            rutina = self._aplicar_parametros_inferidos(rutina, self.parametros_inferidos)
        
        # Registrar rutina generada
        rutina_registro = {
            'id': f"RUT_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            'perfil': perfil,
            'rutina': rutina,
            'fecha_generacion': datetime.now().isoformat(),
            'modo': 'exploracion' if explorar else 'explotacion',
            'generacion': self.learning_system['generacion'],
            'parametros_inferidos': self.parametros_inferidos,
            'clasificacion_usuario': self.clasificacion_usuario
        }
        
        # NUEVO: Predecir satisfacción esperada
        if self.motor_inferencia:
            prediccion = self.motor_inferencia.predecir_satisfaccion(perfil, rutina)
            rutina_registro['prediccion_satisfaccion'] = prediccion
            print(f"\n   🎯 Satisfacción predicha: {prediccion['satisfaccion_predicha']}/5 "
                  f"(Confianza: {prediccion['confianza']*100:.0f}%)")
        
        self.learning_system['rutinas_generadas'].append(rutina_registro)
        self.rutina_actual = rutina_registro
        
        return rutina
    
    def _generar_rutina_exploracion(self, perfil):
        """
        Genera una rutina nueva experimentando con combinaciones.
        Permite al sistema descubrir nuevas rutinas potencialmente mejores.
        """
        dias = perfil['dias']
        nivel = perfil['nivel_str']
        objetivo = perfil['objetivo_str']
        
        rutina_semanal = {}
        
        # Decidir estructura según días
        if dias <= 3:
            estructura = 'fullbody'
            grupos_por_dia = [['pecho', 'espalda', 'piernas', 'hombros', 'brazos']] * dias
        elif dias == 4:
            estructura = 'upper_lower'
            grupos_por_dia = [
                ['pecho', 'espalda', 'hombros', 'brazos'],
                ['piernas', 'core'],
                ['pecho', 'espalda', 'brazos'],
                ['piernas', 'hombros', 'core']
            ]
        else:
            estructura = 'split'
            grupos_por_dia = [
                ['pecho', 'brazos'],
                ['espalda'],
                ['piernas'],
                ['hombros', 'brazos'],
                ['pecho', 'espalda'],
                ['piernas', 'core']
            ][:dias]
        
        # Generar ejercicios para cada día
        for dia_num, grupos in enumerate(grupos_por_dia, 1):
            ejercicios_dia = []
            
            for grupo in grupos:
                num_ejercicios = self._decidir_num_ejercicios(grupo, estructura, nivel)
                ejercicios_grupo = self._seleccionar_ejercicios_innovadores(grupo, num_ejercicios, nivel)
                
                for ejercicio in ejercicios_grupo:
                    params = self._generar_parametros_experimentales(objetivo, nivel, grupo)
                    ejercicios_dia.append({
                        'ejercicio': ejercicio,
                        'grupo': grupo,
                        **params
                    })
            
            # Agregar cardio si es necesario
            if self._necesita_cardio(objetivo, dia_num):
                cardio = random.choice(self.ejercicios_base['cardio'])
                ejercicios_dia.append({
                    'ejercicio': cardio,
                    'grupo': 'cardio',
                    'duracion': f"{random.randint(15, 30)} min",
                    'intensidad': random.choice(['moderada', 'alta', 'HIIT'])
                })
            
            rutina_semanal[f"Día {dia_num}"] = ejercicios_dia
        
        return {
            'rutina_semanal': rutina_semanal,
            'estructura': estructura,
            'metadatos': {
                'modo_generacion': 'exploracion',
                'innovacion_level': 'alta'
            }
        }
    
    def _generar_rutina_aprendida(self, perfil, usuarios_similares):
        """
        APRENDIZAJE REAL:
        Genera rutina basándose en lo que ha funcionado para usuarios similares.
        Este es el verdadero "aprendizaje" del sistema.
        """
        # Extraer las mejores rutinas de usuarios similares
        mejores_rutinas = []
        for similar in usuarios_similares:
            if 'rutina_exitosa' in similar['usuario']:
                mejores_rutinas.append({
                    'rutina': similar['usuario']['rutina_exitosa'],
                    'satisfaccion': similar['usuario'].get('satisfaccion', 3),
                    'peso': similar['similitud']
                })
        
        if not mejores_rutinas:
            # Si no hay rutinas exitosas, explorar
            return self._generar_rutina_exploracion(perfil)
        
        # Analizar patrones comunes en rutinas exitosas
        patrones = self._extraer_patrones_exitosos(mejores_rutinas)
        
        # Generar nueva rutina basada en patrones
        dias = perfil['dias']
        nivel = perfil['nivel_str']
        objetivo = perfil['objetivo_str']
        
        rutina_semanal = {}
        
        # Usar estructura más común en rutinas exitosas
        estructura = patrones.get('estructura_preferida', 'fullbody')
        
        # Generar días usando ejercicios y parámetros aprendidos
        if dias <= 3:
            grupos_por_dia = [['pecho', 'espalda', 'piernas', 'hombros', 'brazos']] * dias
        elif dias == 4:
            grupos_por_dia = [
                ['pecho', 'espalda', 'hombros', 'brazos'],
                ['piernas', 'core'],
                ['pecho', 'espalda', 'brazos'],
                ['piernas', 'hombros']
            ]
        else:
            grupos_por_dia = [
                ['pecho'], ['espalda'], ['piernas'],
                ['hombros', 'brazos'], ['pecho', 'espalda'], ['piernas']
            ][:dias]
        
        for dia_num, grupos in enumerate(grupos_por_dia, 1):
            ejercicios_dia = []
            
            for grupo in grupos:
                # Usar ejercicios que han funcionado bien
                ejercicios_preferidos = patrones.get(f'ejercicios_{grupo}', [])
                
                if ejercicios_preferidos:
                    # 70% usar ejercicios aprendidos, 30% innovar
                    if random.random() < 0.7:
                        ejercicios_seleccionados = random.sample(
                            ejercicios_preferidos,
                            min(len(ejercicios_preferidos), self._decidir_num_ejercicios(grupo, estructura, nivel))
                        )
                    else:
                        ejercicios_seleccionados = self._seleccionar_ejercicios_innovadores(
                            grupo,
                            self._decidir_num_ejercicios(grupo, estructura, nivel),
                            nivel
                        )
                else:
                    ejercicios_seleccionados = self._seleccionar_ejercicios_innovadores(
                        grupo,
                        self._decidir_num_ejercicios(grupo, estructura, nivel),
                        nivel
                    )
                
                for ejercicio in ejercicios_seleccionados:
                    # Usar parámetros óptimos aprendidos
                    params_aprendidos = patrones.get(f'params_{objetivo}', {})
                    
                    if params_aprendidos:
                        params = {
                            'series': params_aprendidos.get('series', 4),
                            'repeticiones': params_aprendidos.get('repeticiones', '8-12'),
                            'descanso': params_aprendidos.get('descanso', '60s')
                        }
                    else:
                        params = self._generar_parametros_experimentales(objetivo, nivel, grupo)
                    
                    ejercicios_dia.append({
                        'ejercicio': ejercicio,
                        'grupo': grupo,
                        **params
                    })
            
            rutina_semanal[f"Día {dia_num}"] = ejercicios_dia
        
        return {
            'rutina_semanal': rutina_semanal,
            'estructura': estructura,
            'metadatos': {
                'modo_generacion': 'aprendizaje',
                'basado_en': len(usuarios_similares),
                'confianza': sum(u['similitud'] for u in usuarios_similares) / len(usuarios_similares)
            }
        }
    
    def _extraer_patrones_exitosos(self, rutinas_exitosas):
        """
        Analiza rutinas exitosas para identificar patrones comunes.
        Esto es cómo el sistema "aprende" qué funciona.
        """
        patrones = {
            'estructuras': [],
            'ejercicios_por_grupo': defaultdict(list),
            'parametros': defaultdict(list)
        }
        
        for rutina_data in rutinas_exitosas:
            rutina = rutina_data['rutina']
            peso = rutina_data['peso']
            
            # Extraer estructura
            if 'estructura' in rutina:
                patrones['estructuras'].append(rutina['estructura'])
            
            # Extraer ejercicios usados
            if 'rutina_semanal' in rutina:
                for dia, ejercicios in rutina['rutina_semanal'].items():
                    for ej in ejercicios:
                        if 'grupo' in ej and ej['grupo'] != 'cardio':
                            patrones['ejercicios_por_grupo'][ej['grupo']].append(ej['ejercicio'])
                            
                            # Extraer parámetros
                            if 'series' in ej:
                                patrones['parametros']['series'].append(ej['series'])
                            if 'repeticiones' in ej:
                                patrones['parametros']['repeticiones'].append(ej['repeticiones'])
        
        # Procesar patrones encontrados
        resultado = {}
        
        # Estructura más común
        if patrones['estructuras']:
            resultado['estructura_preferida'] = max(set(patrones['estructuras']), key=patrones['estructuras'].count)
        
        # Ejercicios más exitosos por grupo
        for grupo, ejercicios in patrones['ejercicios_por_grupo'].items():
            # Contar frecuencia
            frecuencias = defaultdict(int)
            for ej in ejercicios:
                frecuencias[ej] += 1
            # Top ejercicios
            top_ejercicios = sorted(frecuencias.items(), key=lambda x: x[1], reverse=True)[:3]
            resultado[f'ejercicios_{grupo}'] = [ej for ej, _ in top_ejercicios]
        
        # Parámetros promedio
        if patrones['parametros']['series']:
            resultado['params_general'] = {
                'series': int(sum(patrones['parametros']['series']) / len(patrones['parametros']['series'])),
                'repeticiones': '8-12',  # Más común
                'descanso': '60s'
            }
        
        return resultado
    
    def _decidir_num_ejercicios(self, grupo, estructura, nivel):
        """Decide cuántos ejercicios hacer por grupo muscular"""
        if estructura == 'fullbody':
            return 1 if nivel == 'principiante' else 2
        elif estructura == 'upper_lower':
            return 2 if grupo in ['piernas', 'core'] else 1
        else:  # split
            return 3 if nivel == 'avanzado' else 2
    
    def _seleccionar_ejercicios_innovadores(self, grupo, cantidad, nivel):
        """Selecciona ejercicios mezclando compuestos y aislamiento"""
        if grupo not in self.ejercicios_base:
            return []
        
        ejercicios = []
        disponibles = self.ejercicios_base[grupo]
        
        if isinstance(disponibles, dict):
            # Priorizar compuestos para principiantes
            if nivel == 'principiante':
                compuestos = disponibles.get('compuestos', [])
                ejercicios = random.sample(compuestos, min(cantidad, len(compuestos)))
            else:
                # Mix de compuestos y aislamiento
                todos = disponibles.get('compuestos', []) + disponibles.get('aislamiento', [])
                ejercicios = random.sample(todos, min(cantidad, len(todos)))
        else:
            ejercicios = random.sample(disponibles, min(cantidad, len(disponibles)))
        
        return ejercicios
    
    def _generar_parametros_experimentales(self, objetivo, nivel, grupo):
        """Genera parámetros experimentando con rangos"""
        # Mapas base
        nivel_series = {'principiante': 3, 'intermedio': 4, 'avanzado': 5}
        
        if objetivo == 'perder_peso':
            series = nivel_series[nivel]
            reps = f"{random.randint(12, 15)}-{random.randint(15, 20)}"
            descanso = f"{random.randint(30, 60)}s"
        elif objetivo == 'ganar_masa':
            series = nivel_series[nivel] + 1
            reps = f"{random.randint(8, 10)}-{random.randint(10, 12)}"
            descanso = f"{random.randint(60, 90)}s"
        elif objetivo == 'resistencia':
            series = nivel_series[nivel]
            reps = f"{random.randint(15, 20)}-{random.randint(20, 25)}"
            descanso = f"{random.randint(20, 45)}s"
        else:  # fuerza
            series = nivel_series[nivel] + 1
            reps = f"{random.randint(4, 6)}-{random.randint(6, 8)}"
            descanso = f"{random.randint(120, 180)}s"
        
        return {
            'series': series,
            'repeticiones': reps,
            'descanso': descanso
        }
    
    def _necesita_cardio(self, objetivo, dia):
        """Decide si agregar cardio según objetivo"""
        if objetivo == 'perder_peso':
            return random.random() < 0.8  # 80% de probabilidad
        elif objetivo == 'resistencia':
            return random.random() < 0.9  # 90% de probabilidad
        else:
            return random.random() < 0.3  # 30% de probabilidad
    
    def _aplicar_parametros_inferidos(self, rutina, parametros_inferidos):
        """
        Aplica los parámetros optimizados por el motor de inferencia a la rutina
        
        Args:
            rutina: Rutina generada
            parametros_inferidos: Parámetros del motor de inferencia
            
        Returns:
            Rutina con parámetros actualizados
        """
        if 'rutina_semanal' not in rutina:
            return rutina
        
        series_optimas = parametros_inferidos['series']
        reps_min = parametros_inferidos['repeticiones_min']
        reps_max = parametros_inferidos['repeticiones_max']
        descanso_optimo = parametros_inferidos['descanso']
        
        # Actualizar cada ejercicio con los parámetros inferidos
        for dia, ejercicios in rutina['rutina_semanal'].items():
            for ejercicio in ejercicios:
                if 'series' in ejercicio:
                    ejercicio['series'] = series_optimas
                    ejercicio['repeticiones'] = f"{reps_min}-{reps_max}"
                    ejercicio['descanso'] = descanso_optimo
        
        # Agregar metadato
        if 'metadatos' not in rutina:
            rutina['metadatos'] = {}
        
        rutina['metadatos']['parametros_optimizados'] = True
        rutina['metadatos']['confianza_parametros'] = parametros_inferidos['confianza']
        
        return rutina
    
    def procesar_feedback(self, satisfaccion, comentarios=""):
        """
        FUNCIÓN CRÍTICA DE APRENDIZAJE:
        Procesa el feedback del usuario y actualiza el conocimiento del sistema.
        Aquí es donde el sistema realmente "aprende".
        """
        print("\n🎓 Procesando feedback y aprendiendo...")
        
        # Registrar experiencia
        experiencia = {
            'perfil': self.user_data['perfil'],
            'rutina_id': self.rutina_actual['id'],
            'rutina_exitosa': self.rutina_actual['rutina'] if satisfaccion >= 4 else None,
            'satisfaccion': satisfaccion,
            'comentarios': comentarios,
            'fecha': datetime.now().isoformat()
        }
        
        self.learning_system['historico_usuarios'].append(experiencia)
        
        # APRENDIZAJE 1: Actualizar patrones exitosos
        if satisfaccion >= 4:
            perfil = self.user_data['perfil']
            clave_patron = f"{perfil['nivel_str']}_{perfil['objetivo_str']}"
            
            if clave_patron not in self.learning_system['patrones_exitosos']:
                self.learning_system['patrones_exitosos'][clave_patron] = []
            
            self.learning_system['patrones_exitosos'][clave_patron].append({
                'rutina': self.rutina_actual['rutina'],
                'satisfaccion': satisfaccion,
                'fecha': datetime.now().isoformat()
            })
            
            print(f"   ✓ Patrón exitoso guardado para: {clave_patron}")
        
        # APRENDIZAJE 2: Actualizar combinaciones de ejercicios
        if satisfaccion >= 4:
            for dia, ejercicios in self.rutina_actual['rutina']['rutina_semanal'].items():
                for ej in ejercicios:
                    if 'grupo' in ej and ej['grupo'] != 'cardio':
                        grupo = ej['grupo']
                        ejercicio = ej['ejercicio']
                        
                        if grupo not in self.learning_system['combinaciones_ejercicios']:
                            self.learning_system['combinaciones_ejercicios'][grupo] = defaultdict(int)
                        
                        self.learning_system['combinaciones_ejercicios'][grupo][ejercicio] += 1
            
            print("   ✓ Combinaciones de ejercicios actualizadas")
        
        # APRENDIZAJE 3: Ajustar factor de exploración
        # Si las rutinas aprendidas funcionan bien, explorar menos
        # Si funcionan mal, explorar más
        if satisfaccion >= 4 and self.rutina_actual.get('modo') == 'explotacion':
            self.learning_system['factor_exploracion'] = max(0.1, self.learning_system['factor_exploracion'] - 0.01)
            print(f"   ✓ Reduciendo exploración (confianza aumenta): {self.learning_system['factor_exploracion']:.2f}")
        elif satisfaccion <= 2:
            self.learning_system['factor_exploracion'] = min(0.4, self.learning_system['factor_exploracion'] + 0.02)
            print(f"   ✓ Aumentando exploración (buscando mejores opciones): {self.learning_system['factor_exploracion']:.2f}")
        
        # APRENDIZAJE 4: Actualizar métricas
        self.metricas['satisfaccion_promedio_por_generacion'].append({
            'generacion': self.learning_system['generacion'],
            'satisfaccion': satisfaccion
        })
        
        # APRENDIZAJE 5: Incrementar generación (evolución del sistema)
        if len(self.learning_system['historico_usuarios']) % 10 == 0:
            self.learning_system['generacion'] += 1
            print(f"   🎉 Sistema evolucionó a Generación {self.learning_system['generacion']}")
            
            # Analizar mejora
            if len(self.metricas['satisfaccion_promedio_por_generacion']) >= 10:
                ultimas_10 = self.metricas['satisfaccion_promedio_por_generacion'][-10:]
                promedio = sum(x['satisfaccion'] for x in ultimas_10) / 10
                print(f"   📊 Satisfacción promedio últimos 10 usuarios: {promedio:.2f}/5")
        
        # Guardar conocimiento aprendido
        self.save_data()
        print("   💾 Conocimiento guardado para futuras generaciones")
        
        # NUEVO: Detectar anomalías con motor de inferencia
        if self.motor_inferencia and hasattr(self, 'user_data'):
            print("\n   🔍 Analizando patrones y anomalías...")
            
            # Obtener todos los feedbacks del sistema
            usuario_feedbacks = self.learning_system.get('historico_usuarios', [])
            
            if len(usuario_feedbacks) >= 3:
                anomalias = self.motor_inferencia.detectar_anomalias(
                    self.user_data.get('perfil', {}),
                    usuario_feedbacks[-5:]  # Últimos 5 para detectar tendencias
                )
                
                if anomalias.get('anomalias'):
                    print(f"   ⚠️  {len(anomalias['anomalias'])} anomalía(s) detectada(s):")
                    for anomalia in anomalias['anomalias']:
                        print(f"      • {anomalia['descripcion']}")
                        print(f"        → {anomalia['recomendacion']}")
                else:
                    print("   ✓ No se detectaron anomalías, progreso normal")
    
    def obtener_estadisticas_sistema(self):
        """Retorna estadísticas del aprendizaje del sistema"""
        total_usuarios = len(self.learning_system['historico_usuarios'])
        total_rutinas = len(self.learning_system['rutinas_generadas'])
        
        if total_usuarios > 0:
            satisfacciones = [u['satisfaccion'] for u in self.learning_system['historico_usuarios']]
            promedio_satisfaccion = sum(satisfacciones) / len(satisfacciones)
        else:
            promedio_satisfaccion = 0
        
        return {
            'generacion': self.learning_system['generacion'],
            'total_usuarios': total_usuarios,
            'total_rutinas_generadas': total_rutinas,
            'promedio_satisfaccion': promedio_satisfaccion,
            'patrones_exitosos': len(self.learning_system['patrones_exitosos']),
            'factor_exploracion': self.learning_system['factor_exploracion']
        }


# Exportar para uso en la interfaz
if __name__ == "__main__":
    print("Sistema de IA Avanzado cargado correctamente")
    print("Usar con la interfaz gráfica: python gym_ai_gui.py")