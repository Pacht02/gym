
import json
import numpy as np
from collections import defaultdict
from datetime import datetime
import math


class MotorInferencia:
    def __init__(self, base_conocimientos=None):
   
        self.base_conocimientos = base_conocimientos or {}
        self.modelos_entrenados = {}
        self.reglas_inferencia = self._inicializar_reglas()
        self.umbrales = self._inicializar_umbrales()
        
    def _inicializar_reglas(self):
        return {
            # Reglas para predecir satisfacción
            'satisfaccion': {
                'similitud_alta': {'umbral': 0.85, 'peso': 0.4},
                'experiencias_previas': {'minimo': 3, 'peso': 0.3},
                'patron_consolidado': {'minimo': 5, 'peso': 0.3}
            },
            
            # Reglas para clasificación de usuarios
            'clasificacion': {
                'novato': {'experiencias': 0, 'generacion': 0},
                'regular': {'experiencias': (1, 5), 'generacion': (0, 2)},
                'experimentado': {'experiencias': (6, 15), 'generacion': (3, 5)},
                'veterano': {'experiencias': (16, 50), 'generacion': (6, 10)},
                'experto': {'experiencias': 50, 'generacion': 10}
            },
            
            # Reglas para recomendaciones
            'recomendacion': {
                'confianza_minima': 0.6,
                'muestras_minimas': 3,
                'similitud_minima': 0.7
            }
        }
    
    def _inicializar_umbrales(self):
        """Inicializa umbrales para decisiones del motor"""
        return {
            'similitud_alta': 0.85,
            'similitud_media': 0.70,
            'similitud_baja': 0.50,
            'satisfaccion_excelente': 4.5,
            'satisfaccion_buena': 4.0,
            'satisfaccion_aceptable': 3.5,
            'confianza_alta': 0.80,
            'confianza_media': 0.60,
            'confianza_baja': 0.40
        }
    
    # ========================================================================
    # PREDICCIÓN DE SATISFACCIÓN
    # ========================================================================
    
    def predecir_satisfaccion(self, perfil, rutina_propuesta):
        """
        Predice la satisfacción esperada de una rutina antes de asignarla
        
        Args:
            perfil: Perfil numérico del usuario
            rutina_propuesta: Rutina que se va a generar
            
        Returns:
            dict: {
                'satisfaccion_predicha': float (1-5),
                'confianza': float (0-1),
                'factores': dict con factores que influyen,
                'recomendacion': bool (si se recomienda usar esta rutina)
            }
        """
        print("\n🔮 Iniciando predicción de satisfacción...")
        
        # Obtener usuarios similares del histórico
        usuarios_similares = self._buscar_usuarios_similares(perfil)
        
        if not usuarios_similares:
            # Sin datos históricos, predicción conservadora
            return {
                'satisfaccion_predicha': 3.5,
                'confianza': 0.3,
                'factores': {'sin_datos': True},
                'recomendacion': True,
                'metodo': 'baseline'
            }
        
        # Análisis de factores
        factores = self._analizar_factores_satisfaccion(
            perfil, 
            rutina_propuesta, 
            usuarios_similares
        )
        
        # Calcular satisfacción predicha usando modelo bayesiano simple
        satisfaccion_predicha = self._calcular_prediccion_bayesiana(
            usuarios_similares,
            factores
        )
        
        # Calcular confianza de la predicción
        confianza = self._calcular_confianza_prediccion(
            usuarios_similares,
            factores
        )
        
        # Decidir si recomendar
        recomendacion = (
            satisfaccion_predicha >= 3.5 and 
            confianza >= self.umbrales['confianza_baja']
        )
        
        resultado = {
            'satisfaccion_predicha': round(satisfaccion_predicha, 2),
            'confianza': round(confianza, 2),
            'factores': factores,
            'recomendacion': recomendacion,
            'usuarios_similares': len(usuarios_similares),
            'metodo': 'bayesiano'
        }
        
        print(f"   ✓ Satisfacción predicha: {resultado['satisfaccion_predicha']}/5")
        print(f"   ✓ Confianza: {resultado['confianza']*100:.0f}%")
        print(f"   ✓ Recomendación: {'SÍ' if recomendacion else 'NO'}")
        
        return resultado
    
    def _buscar_usuarios_similares(self, perfil, umbral=0.7):
        """Busca usuarios similares en el histórico"""
        if not self.base_conocimientos.get('historico_usuarios'):
            return []
        
        similares = []
        for usuario in self.base_conocimientos['historico_usuarios']:
            similitud = self._calcular_similitud(perfil, usuario['perfil'])
            if similitud >= umbral:
                similares.append({
                    'usuario': usuario,
                    'similitud': similitud
                })
        
        # Ordenar por similitud
        similares.sort(key=lambda x: x['similitud'], reverse=True)
        return similares[:10]  # Top 10
    
    def _calcular_similitud(self, perfil1, perfil2):
        """Calcula similitud entre dos perfiles"""
        try:
            # Extraer valores numéricos
            edad1 = perfil1.get('edad', 30)
            edad2 = perfil2.get('edad', 30)
            imc1 = perfil1.get('imc', 22)
            imc2 = perfil2.get('imc', 22)
            nivel1 = perfil1.get('nivel_num', 2)
            nivel2 = perfil2.get('nivel_num', 2)
            dias1 = perfil1.get('dias', 4)
            dias2 = perfil2.get('dias', 4)
            
            # Comparación de objetivo (binaria)
            obj1 = perfil1.get('objetivo_str', '')
            obj2 = perfil2.get('objetivo_str', '')
            diff_obj = 0 if obj1 == obj2 else 1
            
            # Normalizar diferencias
            diff_edad = abs(edad1 - edad2) / 100
            diff_imc = abs(imc1 - imc2) / 20
            diff_nivel = abs(nivel1 - nivel2) / 3
            diff_dias = abs(dias1 - dias2) / 7
            
            # Distancia euclidiana
            distancia = math.sqrt(
                diff_edad**2 + 
                diff_imc**2 + 
                diff_nivel**2 + 
                diff_obj**2 + 
                diff_dias**2
            )
            
            # Convertir a similitud
            similitud = 1 / (1 + distancia)
            
            return similitud
            
        except Exception as e:
            return 0.5  # Similitud media por defecto
    
    def _analizar_factores_satisfaccion(self, perfil, rutina, usuarios_similares):
        """Analiza factores que influyen en la satisfacción"""
        factores = {}
        
        # Factor 1: Similitud con usuarios exitosos
        if usuarios_similares:
            satisfacciones = [
                u['usuario'].get('satisfaccion', 3) 
                for u in usuarios_similares
            ]
            factores['promedio_similares'] = sum(satisfacciones) / len(satisfacciones)
            factores['cantidad_similares'] = len(usuarios_similares)
            factores['similitud_promedio'] = sum(u['similitud'] for u in usuarios_similares) / len(usuarios_similares)
        else:
            factores['promedio_similares'] = 3.5
            factores['cantidad_similares'] = 0
            factores['similitud_promedio'] = 0
        
        # Factor 2: Complejidad de la rutina vs nivel del usuario
        nivel = perfil.get('nivel_num', 2)
        if rutina and 'rutina_semanal' in rutina:
            num_ejercicios = sum(len(ejercicios) for ejercicios in rutina['rutina_semanal'].values())
            complejidad = num_ejercicios / perfil.get('dias', 4)
            
            # Complejidad ideal: 4-6 ejercicios por día para intermedio
            if nivel == 1:  # Principiante
                ideal = 4
            elif nivel == 2:  # Intermedio
                ideal = 5
            else:  # Avanzado
                ideal = 6
            
            factores['ajuste_complejidad'] = 1 - abs(complejidad - ideal) / ideal
        else:
            factores['ajuste_complejidad'] = 1.0
        
        # Factor 3: Consistencia con patrones exitosos
        clave_patron = f"{perfil.get('nivel_str', 'intermedio')}_{perfil.get('objetivo_str', 'ganar_masa')}"
        patrones = self.base_conocimientos.get('patrones_exitosos', {})
        
        if clave_patron in patrones and patrones[clave_patron]:
            factores['patron_existe'] = True
            factores['cantidad_patrones'] = len(patrones[clave_patron])
        else:
            factores['patron_existe'] = False
            factores['cantidad_patrones'] = 0
        
        return factores
    
    def _calcular_prediccion_bayesiana(self, usuarios_similares, factores):
        """
        Calcula predicción usando enfoque bayesiano simple
        
        P(Satisfacción | Factores) ∝ P(Factores | Satisfacción) * P(Satisfacción)
        """
        if not usuarios_similares:
            return 3.5  # Prior neutral
        
        # Prior: promedio de satisfacción de usuarios similares
        satisfacciones = [u['usuario'].get('satisfaccion', 3) for u in usuarios_similares]
        prior = sum(satisfacciones) / len(satisfacciones)
        
        # Likelihood: ajustar según factores
        ajustes = []
        
        # Ajuste por similitud promedio
        if factores['similitud_promedio'] > self.umbrales['similitud_alta']:
            ajustes.append(0.3)
        elif factores['similitud_promedio'] > self.umbrales['similitud_media']:
            ajustes.append(0.1)
        else:
            ajustes.append(-0.1)
        
        # Ajuste por cantidad de datos
        if factores['cantidad_similares'] >= 5:
            ajustes.append(0.2)
        elif factores['cantidad_similares'] >= 3:
            ajustes.append(0.1)
        
        # Ajuste por complejidad
        if factores['ajuste_complejidad'] > 0.8:
            ajustes.append(0.2)
        elif factores['ajuste_complejidad'] > 0.6:
            ajustes.append(0.0)
        else:
            ajustes.append(-0.2)
        
        # Ajuste por patrones consolidados
        if factores['patron_existe'] and factores['cantidad_patrones'] >= 5:
            ajustes.append(0.3)
        
        # Calcular posterior
        ajuste_total = sum(ajustes)
        posterior = prior + ajuste_total
        
        # Limitar a rango [1, 5]
        return max(1.0, min(5.0, posterior))
    
    def _calcular_confianza_prediccion(self, usuarios_similares, factores):
        """Calcula la confianza de la predicción (0-1)"""
        confianza = 0.5  # Base
        
        # Factor 1: Cantidad de datos (max +0.3)
        if factores['cantidad_similares'] >= 10:
            confianza += 0.3
        elif factores['cantidad_similares'] >= 5:
            confianza += 0.2
        elif factores['cantidad_similares'] >= 3:
            confianza += 0.1
        
        # Factor 2: Similitud promedio (max +0.3)
        if factores['similitud_promedio'] > self.umbrales['similitud_alta']:
            confianza += 0.3
        elif factores['similitud_promedio'] > self.umbrales['similitud_media']:
            confianza += 0.2
        elif factores['similitud_promedio'] > self.umbrales['similitud_baja']:
            confianza += 0.1
        
        # Factor 3: Consistencia de resultados (max +0.2)
        if usuarios_similares:
            satisfacciones = [u['usuario'].get('satisfaccion', 3) for u in usuarios_similares]
            desviacion = np.std(satisfacciones) if len(satisfacciones) > 1 else 1.0
            
            if desviacion < 0.5:  # Muy consistente
                confianza += 0.2
            elif desviacion < 1.0:  # Medianamente consistente
                confianza += 0.1
        
        return min(1.0, confianza)
    
    # ========================================================================
    # INFERENCIA DE PARÁMETROS ÓPTIMOS
    # ========================================================================
    
    def inferir_parametros_optimos(self, perfil):
        """
        Infiere los parámetros óptimos (series, reps, descanso) para un perfil
        
        Args:
            perfil: Perfil del usuario
            
        Returns:
            dict: Parámetros óptimos inferidos con nivel de confianza
        """
        print("\n🎯 Infiriendo parámetros óptimos...")
        
        # Buscar usuarios similares exitosos
        usuarios_similares = self._buscar_usuarios_similares(perfil, umbral=0.75)
        usuarios_exitosos = [
            u for u in usuarios_similares 
            if u['usuario'].get('satisfaccion', 0) >= 4
        ]
        
        if not usuarios_exitosos:
            # Sin datos, usar heurísticas por objetivo
            return self._parametros_por_heuristica(perfil)
        
        # Extraer parámetros de rutinas exitosas
        series_list = []
        reps_list = []
        descansos_list = []
        
        for usuario_data in usuarios_exitosos:
            rutina = usuario_data['usuario'].get('rutina_exitosa', {})
            if 'rutina_semanal' in rutina:
                for dia, ejercicios in rutina['rutina_semanal'].items():
                    for ej in ejercicios:
                        if 'series' in ej:
                            series_list.append(ej['series'])
                        if 'repeticiones' in ej:
                            # Extraer el promedio del rango (ej: "8-12" -> 10)
                            reps_str = str(ej['repeticiones'])
                            if '-' in reps_str:
                                reps_range = reps_str.split('-')
                                try:
                                    reps_avg = (int(reps_range[0]) + int(reps_range[1])) / 2
                                    reps_list.append(reps_avg)
                                except:
                                    pass
        
        # Calcular valores óptimos
        if series_list:
            series_optimo = int(round(np.median(series_list)))
        else:
            series_optimo = 4
        
        if reps_list:
            reps_optimo = int(round(np.median(reps_list)))
        else:
            reps_optimo = 10
        
        # Calcular confianza
        confianza = min(1.0, len(usuarios_exitosos) / 10)
        
        resultado = {
            'series': series_optimo,
            'repeticiones_min': max(4, reps_optimo - 2),
            'repeticiones_max': reps_optimo + 2,
            'descanso': self._inferir_descanso(perfil, series_optimo, reps_optimo),
            'confianza': round(confianza, 2),
            'basado_en': len(usuarios_exitosos),
            'metodo': 'inferencia_datos'
        }
        
        print(f"   ✓ Series: {resultado['series']}")
        print(f"   ✓ Reps: {resultado['repeticiones_min']}-{resultado['repeticiones_max']}")
        print(f"   ✓ Descanso: {resultado['descanso']}")
        print(f"   ✓ Confianza: {resultado['confianza']*100:.0f}%")
        
        return resultado
    
    def _parametros_por_heuristica(self, perfil):
        """Parámetros basados en reglas heurísticas (sin datos históricos)"""
        objetivo = perfil.get('objetivo_str', 'ganar_masa')
        nivel = perfil.get('nivel_num', 2)
        
        # Mapeo de parámetros por objetivo
        params_objetivo = {
            'perder_peso': {'series': 3, 'reps': (12, 18), 'descanso': '45-60s'},
            'ganar_masa': {'series': 4, 'reps': (8, 12), 'descanso': '60-90s'},
            'resistencia': {'series': 3, 'reps': (15, 25), 'descanso': '30-45s'},
            'fuerza': {'series': 5, 'reps': (4, 8), 'descanso': '120-180s'}
        }
        
        params = params_objetivo.get(objetivo, params_objetivo['ganar_masa'])
        
        # Ajustar por nivel
        if nivel == 1:  # Principiante
            params['series'] = max(3, params['series'] - 1)
        elif nivel == 3:  # Avanzado
            params['series'] = params['series'] + 1
        
        return {
            'series': params['series'],
            'repeticiones_min': params['reps'][0],
            'repeticiones_max': params['reps'][1],
            'descanso': params['descanso'],
            'confianza': 0.5,
            'basado_en': 0,
            'metodo': 'heuristica'
        }
    
    def _inferir_descanso(self, perfil, series, reps):
        """Infiere tiempo de descanso óptimo"""
        objetivo = perfil.get('objetivo_str', 'ganar_masa')
        
        if objetivo == 'fuerza' or series >= 5:
            return "120-180s"
        elif objetivo == 'ganar_masa':
            return "60-90s"
        elif objetivo == 'resistencia' or reps >= 15:
            return "30-45s"
        else:
            return "45-60s"
    
    # ========================================================================
    # CLASIFICACIÓN DE USUARIOS
    # ========================================================================
    
    def clasificar_usuario(self, perfil, historico_personal=None):
        """
        Clasifica al usuario en una categoría según su experiencia y rendimiento
        
        Args:
            perfil: Perfil del usuario
            historico_personal: Lista de experiencias previas del usuario
            
        Returns:
            dict: Clasificación y características
        """
        print("\n👤 Clasificando usuario...")
        
        # Contar experiencias del usuario
        num_experiencias = len(historico_personal) if historico_personal else 0
        
        # Obtener generación actual del sistema
        generacion_sistema = self.base_conocimientos.get('learning_system', {}).get('generacion', 0)
        
        # Calcular satisfacción promedio del usuario
        if historico_personal:
            satisfacciones = [exp.get('satisfaccion', 3) for exp in historico_personal]
            satisfaccion_promedio = sum(satisfacciones) / len(satisfacciones)
        else:
            satisfaccion_promedio = 0
        
        # Clasificar según reglas
        reglas = self.reglas_inferencia['clasificacion']
        
        if num_experiencias == 0:
            categoria = 'novato'
            descripcion = "Primera vez usando el sistema"
        elif num_experiencias <= 5:
            categoria = 'regular'
            descripcion = "Usuario regular con algunas experiencias"
        elif num_experiencias <= 15:
            categoria = 'experimentado'
            descripcion = "Usuario experimentado con buen historial"
        elif num_experiencias <= 50:
            categoria = 'veterano'
            descripcion = "Usuario veterano con amplia experiencia"
        else:
            categoria = 'experto'
            descripcion = "Usuario experto del sistema"
        
        # Subcategoría por rendimiento
        if satisfaccion_promedio >= 4.5:
            rendimiento = "excelente"
        elif satisfaccion_promedio >= 4.0:
            rendimiento = "bueno"
        elif satisfaccion_promedio >= 3.5:
            rendimiento = "aceptable"
        else:
            rendimiento = "necesita_ajuste"
        
        resultado = {
            'categoria': categoria,
            'descripcion': descripcion,
            'experiencias': num_experiencias,
            'satisfaccion_promedio': round(satisfaccion_promedio, 2),
            'rendimiento': rendimiento,
            'recomendaciones': self._generar_recomendaciones_categoria(
                categoria, 
                rendimiento,
                perfil
            )
        }
        
        print(f"   ✓ Categoría: {categoria.upper()}")
        print(f"   ✓ Experiencias: {num_experiencias}")
        print(f"   ✓ Satisfacción promedio: {satisfaccion_promedio:.2f}/5")
        print(f"   ✓ Rendimiento: {rendimiento}")
        
        return resultado
    
    def _generar_recomendaciones_categoria(self, categoria, rendimiento, perfil):
        """Genera recomendaciones específicas según la categoría"""
        recomendaciones = []
        
        if categoria == 'novato':
            recomendaciones.append("Comienza con rutinas Full Body 3 días/semana")
            recomendaciones.append("Enfócate en aprender técnica correcta")
            recomendaciones.append("Da feedback detallado para ayudar al sistema")
        
        elif categoria == 'regular':
            if rendimiento == "necesita_ajuste":
                recomendaciones.append("Considera ajustar días de entrenamiento")
                recomendaciones.append("Revisa si la intensidad es adecuada")
            else:
                recomendaciones.append("Continúa con la consistencia")
                recomendaciones.append("Considera aumentar días de entrenamiento")
        
        elif categoria in ['experimentado', 'veterano']:
            if rendimiento == "excelente":
                recomendaciones.append("Excelente progreso, mantén el ritmo")
                recomendaciones.append("Considera técnicas avanzadas")
            recomendaciones.append("Revisa objetivos cada 4-6 semanas")
        
        elif categoria == 'experto':
            recomendaciones.append("Usuario experimentado del sistema")
            recomendaciones.append("Considera compartir feedback detallado")
            recomendaciones.append("Experimenta con variaciones avanzadas")
        
        return recomendaciones
    
    # ========================================================================
    # SISTEMA DE RECOMENDACIONES
    # ========================================================================
    
    def recomendar_rutina(self, perfil, opciones_rutinas):
        """
        Recomienda la mejor rutina entre varias opciones
        
        Args:
            perfil: Perfil del usuario
            opciones_rutinas: Lista de rutinas posibles
            
        Returns:
            dict: Mejor rutina recomendada con scoring
        """
        print("\n⭐ Recomendando rutina óptima...")
        
        if not opciones_rutinas:
            return None
        
        # Evaluar cada opción
        evaluaciones = []
        for idx, rutina in enumerate(opciones_rutinas):
            score = self._evaluar_rutina(perfil, rutina)
            evaluaciones.append({
                'indice': idx,
                'rutina': rutina,
                'score': score['score_total'],
                'detalles': score
            })
        
        # Ordenar por score
        evaluaciones.sort(key=lambda x: x['score'], reverse=True)
        
        mejor = evaluaciones[0]
        
        print(f"   ✓ Mejor opción: Rutina #{mejor['indice']+1}")
        print(f"   ✓ Score: {mejor['score']:.2f}/100")
        
        return {
            'rutina_recomendada': mejor['rutina'],
            'score': mejor['score'],
            'ranking': evaluaciones,
            'justificacion': self._generar_justificacion(mejor['detalles'])
        }
    
    def _evaluar_rutina(self, perfil, rutina):
        """Evalúa una rutina y le asigna un score (0-100)"""
        scores = {}
        
        # Criterio 1: Predicción de satisfacción (40 puntos)
        prediccion = self.predecir_satisfaccion(perfil, rutina)
        scores['satisfaccion'] = (prediccion['satisfaccion_predicha'] / 5) * 40
        
        # Criterio 2: Adecuación al nivel (20 puntos)
        nivel = perfil.get('nivel_num', 2)
        if rutina and 'rutina_semanal' in rutina:
            num_ejercicios = sum(len(ejs) for ejs in rutina['rutina_semanal'].values())
            complejidad = num_ejercicios / perfil.get('dias', 4)
            
            if nivel == 1:  # Principiante: 3-4 ejercicios/día
                scores['nivel'] = 20 if 3 <= complejidad <= 4 else 10
            elif nivel == 2:  # Intermedio: 4-5 ejercicios/día
                scores['nivel'] = 20 if 4 <= complejidad <= 5 else 15
            else:  # Avanzado: 5-7 ejercicios/día
                scores['nivel'] = 20 if 5 <= complejidad <= 7 else 15
        else:
            scores['nivel'] = 10
        
        # Criterio 3: Consistencia con objetivo (20 puntos)
        objetivo = perfil.get('objetivo_str', 'ganar_masa')
        # (Aquí se podría analizar si los ejercicios son apropiados)
        scores['objetivo'] = 20  # Simplificado
        
        # Criterio 4: Variedad y balance (20 puntos)
        if rutina and 'rutina_semanal' in rutina:
            grupos_trabajados = set()
            for ejercicios in rutina['rutina_semanal'].values():
                for ej in ejercicios:
                    if 'grupo' in ej:
                        grupos_trabajados.add(ej['grupo'])
            
            variedad = len(grupos_trabajados)
            scores['variedad'] = min(20, variedad * 4)
        else:
            scores['variedad'] = 10
        
        # Score total
        score_total = sum(scores.values())
        
        return {
            'score_total': round(score_total, 2),
            'scores_detallados': scores
        }
    
    def _generar_justificacion(self, detalles):
        """Genera justificación textual de la recomendación"""
        justificacion = []
        
        scores = detalles['scores_detallados']
        
        if scores['satisfaccion'] >= 30:
            justificacion.append("Alta probabilidad de satisfacción")
        if scores['nivel'] >= 18:
            justificacion.append("Muy adecuada para tu nivel")
        if scores['variedad'] >= 16:
            justificacion.append("Excelente variedad de ejercicios")
        
        return justificacion if justificacion else ["Rutina balanceada general"]
    
    # ========================================================================
    # DETECCIÓN DE ANOMALÍAS Y PATRONES
    # ========================================================================
    
    def detectar_anomalias(self, perfil, feedback_historico):
        """
        Detecta patrones anómalos en el rendimiento del usuario
        
        Args:
            perfil: Perfil del usuario
            feedback_historico: Lista de feedbacks previos
            
        Returns:
            dict: Anomalías detectadas y recomendaciones
        """
        if not feedback_historico or len(feedback_historico) < 3:
            return {'anomalias': [], 'estado': 'normal'}
        
        satisfacciones = [f.get('satisfaccion', 3) for f in feedback_historico]
        
        anomalias = []
        
        # Detectar tendencia negativa
        if len(satisfacciones) >= 3:
            ultimas_3 = satisfacciones[-3:]
            if all(ultimas_3[i] > ultimas_3[i+1] for i in range(len(ultimas_3)-1)):
                anomalias.append({
                    'tipo': 'tendencia_negativa',
                    'descripcion': 'Satisfacción en descenso constante',
                    'recomendacion': 'Revisar intensidad o variedad de ejercicios'
                })
        
        # Detectar caída abrupta
        if len(satisfacciones) >= 2:
            if satisfacciones[-2] >= 4 and satisfacciones[-1] <= 2:
                anomalias.append({
                    'tipo': 'caida_abrupta',
                    'descripcion': 'Caída súbita en satisfacción',
                    'recomendacion': 'Verificar posibles lesiones o sobreentrenamiento'
                })
        
        # Detectar estancamiento
        promedio = sum(satisfacciones) / len(satisfacciones)
        if 3.0 <= promedio <= 3.5 and len(satisfacciones) >= 5:
            anomalias.append({
                'tipo': 'estancamiento',
                'descripcion': 'Satisfacción estancada en nivel medio',
                'recomendacion': 'Considerar cambio de enfoque o metodología'
            })
        
        return {
            'anomalias': anomalias,
            'estado': 'anomalo' if anomalias else 'normal',
            'satisfaccion_promedio': promedio
        }
    
    # ========================================================================
    # UTILIDADES
    # ========================================================================
    
    def generar_reporte_inferencias(self, perfil):
        """
        Genera un reporte completo de todas las inferencias para un perfil
        
        Returns:
            dict: Reporte completo
        """
        print("\n📋 Generando reporte de inferencias...")
        
        reporte = {
            'perfil': perfil,
            'timestamp': datetime.now().isoformat(),
            'prediccion_satisfaccion': self.predecir_satisfaccion(perfil, None),
            'parametros_optimos': self.inferir_parametros_optimos(perfil),
            'clasificacion': self.clasificar_usuario(perfil),
            'estadisticas_sistema': {
                'usuarios_en_base': len(self.base_conocimientos.get('historico_usuarios', [])),
                'patrones_identificados': len(self.base_conocimientos.get('patrones_exitosos', {})),
                'generacion_actual': self.base_conocimientos.get('learning_system', {}).get('generacion', 0)
            }
        }
        
        print("   ✓ Reporte generado exitosamente")
        
        return reporte


# ============================================================================
# FUNCIONES DE UTILIDAD
# ============================================================================

def cargar_motor_inferencia(archivo_datos='gym_ai_advanced_data.json'):
    """Carga el motor de inferencia con datos existentes"""
    try:
        with open(archivo_datos, 'r', encoding='utf-8') as f:
            base_conocimientos = json.load(f)
        print(f"✓ Base de conocimientos cargada desde {archivo_datos}")
    except FileNotFoundError:
        base_conocimientos = {}
        print("⚠ No se encontró base de conocimientos, iniciando vacío")
    
    return MotorInferencia(base_conocimientos)


def ejemplo_uso():
    """Ejemplo de uso del motor de inferencia"""
    print("="*70)
    print("EJEMPLO DE USO DEL MOTOR DE INFERENCIA")
    print("="*70)
    
    # Crear motor
    motor = MotorInferencia()
    
    # Perfil de ejemplo
    perfil_ejemplo = {
        'edad': 25,
        'peso': 70,
        'altura': 1.75,
        'imc': 22.86,
        'nivel_num': 2,
        'nivel_str': 'intermedio',
        'objetivo_num': 2,
        'objetivo_str': 'ganar_masa',
        'dias': 4
    }
    
    print("\n1. PREDICCIÓN DE SATISFACCIÓN")
    print("-" * 70)
    prediccion = motor.predecir_satisfaccion(perfil_ejemplo, None)
    
    print("\n2. INFERENCIA DE PARÁMETROS")
    print("-" * 70)
    parametros = motor.inferir_parametros_optimos(perfil_ejemplo)
    
    print("\n3. CLASIFICACIÓN DE USUARIO")
    print("-" * 70)
    clasificacion = motor.clasificar_usuario(perfil_ejemplo)
    
    print("\n" + "="*70)
    print("EJEMPLO COMPLETADO")
    print("="*70)


if __name__ == "__main__":
    ejemplo_uso()