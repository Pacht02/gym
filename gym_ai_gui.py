import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import json
from gym_ai_advanced import AdvancedGymAI
from datetime import datetime

class GymAIGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("🏋️ Sistema de IA Adaptativo - Gimnasio")
        self.root.geometry("1000x700")
        self.root.configure(bg='#1a1a2e')
        
        # Inicializar el sistema de IA
        self.ai_system = AdvancedGymAI()
        
        # Variables
        self.current_step = 0
        self.user_data = {}
        self.rutina_generada = None
        
        # Estilo
        self.setup_styles()
        
        # Crear interfaz
        self.create_header()
        self.create_main_container()
        self.show_welcome_screen()
    
    def setup_styles(self):
        """Configura estilos personalizados"""
        style = ttk.Style()
        style.theme_use('clam')
        
        # Colores
        self.colors = {
            'bg_dark': '#1a1a2e',
            'bg_medium': '#16213e',
            'bg_light': '#0f3460',
            'accent': '#00adb5',
            'text': '#eeeeee',
            'success': '#06d6a0',
            'warning': '#ffd93d',
            'error': '#ef476f'
        }
        
        # Botón principal
        style.configure('Accent.TButton',
                       background=self.colors['accent'],
                       foreground='white',
                       borderwidth=0,
                       focuscolor='none',
                       font=('Helvetica', 11, 'bold'),
                       padding=10)
        
        # Frame
        style.configure('Custom.TFrame',
                       background=self.colors['bg_medium'])
        
        # Label
        style.configure('Custom.TLabel',
                       background=self.colors['bg_medium'],
                       foreground=self.colors['text'],
                       font=('Helvetica', 10))
        
        style.configure('Title.TLabel',
                       background=self.colors['bg_medium'],
                       foreground=self.colors['accent'],
                       font=('Helvetica', 14, 'bold'))
    
    def create_header(self):
        """Crea el header de la aplicación"""
        header = tk.Frame(self.root, bg=self.colors['bg_light'], height=80)
        header.pack(fill='x', side='top')
        header.pack_propagate(False)
        
        # Título
        title = tk.Label(header,
                        text="🏋️ SISTEMA DE IA ADAPTATIVO PARA GIMNASIO",
                        font=('Helvetica', 18, 'bold'),
                        bg=self.colors['bg_light'],
                        fg=self.colors['accent'])
        title.pack(pady=20)
        
        # Estadísticas del sistema
        stats = self.ai_system.obtener_estadisticas_sistema()
        stats_text = f"Generación: {stats['generacion']} | Usuarios: {stats['total_usuarios']} | Satisfacción: {stats['promedio_satisfaccion']:.1f}/5"
        
        stats_label = tk.Label(header,
                              text=stats_text,
                              font=('Helvetica', 9),
                              bg=self.colors['bg_light'],
                              fg=self.colors['text'])
        stats_label.pack()
    
    def create_main_container(self):
        """Crea el contenedor principal"""
        self.main_container = tk.Frame(self.root, bg=self.colors['bg_dark'])
        self.main_container.pack(fill='both', expand=True, padx=20, pady=20)
    
    def clear_main_container(self):
        """Limpia el contenedor principal"""
        for widget in self.main_container.winfo_children():
            widget.destroy()
    
    def show_welcome_screen(self):
        """Pantalla de bienvenida"""
        self.clear_main_container()
        
        frame = tk.Frame(self.main_container, bg=self.colors['bg_medium'], padx=40, pady=40)
        frame.place(relx=0.5, rely=0.5, anchor='center')
        
        # Logo/Icono
        welcome_label = tk.Label(frame,
                                text="💪 ¡BIENVENIDO!",
                                font=('Helvetica', 24, 'bold'),
                                bg=self.colors['bg_medium'],
                                fg=self.colors['accent'])
        welcome_label.pack(pady=20)
        
        # Descripción
        desc = """Sistema de Inteligencia Artificial que aprende de cada usuario
para generar rutinas de gimnasio cada vez más precisas y personalizadas.

El sistema analiza tu perfil, busca patrones en usuarios similares
y genera una rutina completamente personalizada para ti.

¡Mientras más personas lo usen, más inteligente se vuelve!"""
        
        desc_label = tk.Label(frame,
                             text=desc,
                             font=('Helvetica', 11),
                             bg=self.colors['bg_medium'],
                             fg=self.colors['text'],
                             justify='center')
        desc_label.pack(pady=20)
        
        # Información del sistema
        stats = self.ai_system.obtener_estadisticas_sistema()
        info = f"""
🧠 Generación actual del sistema: {stats['generacion']}
👥 Usuarios que han ayudado a entrenar la IA: {stats['total_usuarios']}
📊 Patrones exitosos identificados: {stats['patrones_exitosos']}
🎯 Tasa de satisfacción promedio: {stats['promedio_satisfaccion']:.2f}/5
"""
        
        info_label = tk.Label(frame,
                             text=info,
                             font=('Helvetica', 10),
                             bg=self.colors['bg_medium'],
                             fg=self.colors['success'],
                             justify='left')
        info_label.pack(pady=15)
        
        # Botón comenzar
        start_btn = tk.Button(frame,
                             text="COMENZAR →",
                             font=('Helvetica', 14, 'bold'),
                             bg=self.colors['accent'],
                             fg='white',
                             activebackground=self.colors['success'],
                             activeforeground='white',
                             padx=40,
                             pady=15,
                             border=0,
                             cursor='hand2',
                             command=self.show_form_screen)
        start_btn.pack(pady=20)
    
    def show_form_screen(self):
        """Formulario de datos del usuario"""
        self.clear_main_container()
        
        # Frame principal con scroll
        canvas = tk.Canvas(self.main_container, bg=self.colors['bg_dark'], highlightthickness=0)
        scrollbar = ttk.Scrollbar(self.main_container, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg=self.colors['bg_medium'])
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True, padx=(0, 10))
        scrollbar.pack(side="right", fill="y")
        
        # Contenido del formulario
        form_frame = tk.Frame(scrollable_frame, bg=self.colors['bg_medium'], padx=50, pady=30)
        form_frame.pack(fill='both', expand=True)
        
        # Título
        title = tk.Label(form_frame,
                        text="📝 Cuéntame sobre ti",
                        font=('Helvetica', 20, 'bold'),
                        bg=self.colors['bg_medium'],
                        fg=self.colors['accent'])
        title.grid(row=0, column=0, columnspan=2, pady=(0, 30))
        
        # Campos del formulario
        fields = [
            ("Nombre:", "nombre", "entry"),
            ("Edad:", "edad", "entry"),
            ("Peso (kg):", "peso", "entry"),
            ("Altura (m):", "altura", "entry"),
        ]
        
        self.form_vars = {}
        row = 1
        
        for label_text, var_name, field_type in fields:
            label = tk.Label(form_frame,
                           text=label_text,
                           font=('Helvetica', 12),
                           bg=self.colors['bg_medium'],
                           fg=self.colors['text'])
            label.grid(row=row, column=0, sticky='w', pady=10, padx=(0, 20))
            
            if field_type == "entry":
                entry = tk.Entry(form_frame,
                               font=('Helvetica', 12),
                               bg=self.colors['bg_light'],
                               fg=self.colors['text'],
                               insertbackground=self.colors['text'],
                               relief='flat',
                               width=30)
                entry.grid(row=row, column=1, pady=10)
                self.form_vars[var_name] = entry
            
            row += 1
        
        # Nivel de experiencia
        label = tk.Label(form_frame,
                        text="Nivel de experiencia:",
                        font=('Helvetica', 12),
                        bg=self.colors['bg_medium'],
                        fg=self.colors['text'])
        label.grid(row=row, column=0, sticky='w', pady=10, padx=(0, 20))
        
        nivel_var = tk.StringVar(value="principiante")
        nivel_frame = tk.Frame(form_frame, bg=self.colors['bg_medium'])
        nivel_frame.grid(row=row, column=1, pady=10, sticky='w')
        
        for nivel in ['principiante', 'intermedio', 'avanzado']:
            rb = tk.Radiobutton(nivel_frame,
                               text=nivel.title(),
                               variable=nivel_var,
                               value=nivel,
                               font=('Helvetica', 10),
                               bg=self.colors['bg_medium'],
                               fg=self.colors['text'],
                               selectcolor=self.colors['bg_light'],
                               activebackground=self.colors['bg_medium'],
                               activeforeground=self.colors['accent'])
            rb.pack(side='left', padx=10)
        
        self.form_vars['nivel'] = nivel_var
        row += 1
        
        # Objetivo
        label = tk.Label(form_frame,
                        text="Objetivo principal:",
                        font=('Helvetica', 12),
                        bg=self.colors['bg_medium'],
                        fg=self.colors['text'])
        label.grid(row=row, column=0, sticky='w', pady=10, padx=(0, 20))
        
        objetivo_var = tk.StringVar(value="ganar_masa")
        objetivo_frame = tk.Frame(form_frame, bg=self.colors['bg_medium'])
        objetivo_frame.grid(row=row, column=1, pady=10, sticky='w')
        
        objetivos = [
            ('Perder peso', 'perder_peso'),
            ('Ganar masa', 'ganar_masa'),
            ('Resistencia', 'resistencia'),
            ('Fuerza', 'fuerza')
        ]
        
        for text, value in objetivos:
            rb = tk.Radiobutton(objetivo_frame,
                               text=text,
                               variable=objetivo_var,
                               value=value,
                               font=('Helvetica', 10),
                               bg=self.colors['bg_medium'],
                               fg=self.colors['text'],
                               selectcolor=self.colors['bg_light'],
                               activebackground=self.colors['bg_medium'],
                               activeforeground=self.colors['accent'])
            rb.pack(anchor='w', pady=2)
        
        self.form_vars['objetivo'] = objetivo_var
        row += 1
        
        # Días de entrenamiento
        label = tk.Label(form_frame,
                        text="Días disponibles:",
                        font=('Helvetica', 12),
                        bg=self.colors['bg_medium'],
                        fg=self.colors['text'])
        label.grid(row=row, column=0, sticky='w', pady=10, padx=(0, 20))
        
        dias_var = tk.IntVar(value=4)
        dias_spinbox = tk.Spinbox(form_frame,
                                 from_=2,
                                 to=7,
                                 textvariable=dias_var,
                                 font=('Helvetica', 12),
                                 bg=self.colors['bg_light'],
                                 fg=self.colors['text'],
                                 width=28)
        dias_spinbox.grid(row=row, column=1, pady=10)
        self.form_vars['dias'] = dias_var
        row += 1
        
        # Limitaciones
        label = tk.Label(form_frame,
                        text="Limitaciones (opcional):",
                        font=('Helvetica', 12),
                        bg=self.colors['bg_medium'],
                        fg=self.colors['text'])
        label.grid(row=row, column=0, sticky='w', pady=10, padx=(0, 20))
        
        limitaciones_text = tk.Text(form_frame,
                                   height=3,
                                   font=('Helvetica', 10),
                                   bg=self.colors['bg_light'],
                                   fg=self.colors['text'],
                                   insertbackground=self.colors['text'],
                                   relief='flat',
                                   width=30)
        limitaciones_text.grid(row=row, column=1, pady=10)
        self.form_vars['limitaciones'] = limitaciones_text
        row += 1
        
        # Botón generar rutina
        btn_frame = tk.Frame(form_frame, bg=self.colors['bg_medium'])
        btn_frame.grid(row=row, column=0, columnspan=2, pady=30)
        
        generate_btn = tk.Button(btn_frame,
                                text="🧠 GENERAR RUTINA CON IA",
                                font=('Helvetica', 14, 'bold'),
                                bg=self.colors['accent'],
                                fg='white',
                                activebackground=self.colors['success'],
                                activeforeground='white',
                                padx=40,
                                pady=15,
                                border=0,
                                cursor='hand2',
                                command=self.generate_routine)
        generate_btn.pack()
    
    def generate_routine(self):
        """Genera la rutina usando IA"""
        try:
            # Validar datos
            nombre = self.form_vars['nombre'].get().strip()
            edad = int(self.form_vars['edad'].get())
            peso = float(self.form_vars['peso'].get())
            altura = float(self.form_vars['altura'].get())
            
            if not nombre or edad < 10 or peso < 30 or altura < 1.0:
                messagebox.showerror("Error", "Por favor, completa todos los campos correctamente")
                return
            
            # Recopilar datos
            self.user_data = {
                'nombre': nombre,
                'edad': edad,
                'peso': peso,
                'altura': altura,
                'nivel_experiencia': self.form_vars['nivel'].get(),
                'objetivo': self.form_vars['objetivo'].get(),
                'dias_entrenamiento': self.form_vars['dias'].get(),
                'limitaciones': self.form_vars['limitaciones'].get('1.0', 'end').strip() or 'ninguna',
                'fecha_inicio': datetime.now().isoformat()
            }
            
            # Mostrar pantalla de carga
            self.show_loading_screen()
            
            # Generar rutina con IA (simulamos un pequeño delay para efecto)
            self.root.after(1500, self.finish_generation)
            
        except ValueError:
            messagebox.showerror("Error", "Por favor, ingresa valores numéricos válidos")
    
    def show_loading_screen(self):
        """Muestra pantalla de carga mientras la IA genera"""
        self.clear_main_container()
        
        frame = tk.Frame(self.main_container, bg=self.colors['bg_medium'], padx=60, pady=60)
        frame.place(relx=0.5, rely=0.5, anchor='center')
        
        # Animación de carga
        loading_label = tk.Label(frame,
                                text="🧠 IA TRABAJANDO...",
                                font=('Helvetica', 20, 'bold'),
                                bg=self.colors['bg_medium'],
                                fg=self.colors['accent'])
        loading_label.pack(pady=20)
        
        status_texts = [
            "🔍 Analizando tu perfil...",
            "📊 Calculando IMC y métricas...",
            "🎯 Buscando patrones en usuarios similares...",
            "💡 Generando combinaciones de ejercicios...",
            "⚡ Optimizando parámetros de entrenamiento...",
            "✨ Creando tu rutina personalizada..."
        ]
        
        for text in status_texts:
            label = tk.Label(frame,
                           text=text,
                           font=('Helvetica', 11),
                           bg=self.colors['bg_medium'],
                           fg=self.colors['text'])
            label.pack(pady=5, anchor='w')
    
    def finish_generation(self):
        """Finaliza la generación de rutina"""
        # Crear perfil y generar rutina
        self.ai_system.user_data = self.user_data
        perfil = self.ai_system.crear_perfil_usuario(self.user_data)
        self.user_data['perfil'] = perfil
        
        self.rutina_generada = self.ai_system.generar_rutina_inteligente(perfil)
        
        # Mostrar rutina
        self.show_routine_screen()
    
    def show_routine_screen(self):
        """Muestra la rutina generada"""
        self.clear_main_container()
        
        # Frame principal con scroll
        canvas = tk.Canvas(self.main_container, bg=self.colors['bg_dark'], highlightthickness=0)
        scrollbar = ttk.Scrollbar(self.main_container, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg=self.colors['bg_dark'])
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True, padx=(0, 10))
        scrollbar.pack(side="right", fill="y")
        
        # Contenido
        content_frame = tk.Frame(scrollable_frame, bg=self.colors['bg_dark'], padx=20, pady=20)
        content_frame.pack(fill='both', expand=True)
        
        # Título
        title = tk.Label(content_frame,
                        text=f"🎯 RUTINA PERSONALIZADA PARA {self.user_data['nombre'].upper()}",
                        font=('Helvetica', 18, 'bold'),
                        bg=self.colors['bg_dark'],
                        fg=self.colors['accent'])
        title.pack(pady=(0, 20))
        
        # Análisis del perfil
        perfil = self.user_data['perfil']
        imc = perfil['imc']
        
        info_frame = tk.Frame(content_frame, bg=self.colors['bg_medium'], padx=20, pady=15)
        info_frame.pack(fill='x', pady=(0, 20))
        
        info_text = f"""📊 ANÁLISIS DE TU PERFIL
        
IMC: {imc:.1f} - {self.get_imc_category(imc)}
Edad: {perfil['edad']} años | Nivel: {perfil['nivel_str'].title()} | Objetivo: {perfil['objetivo_str'].replace('_', ' ').title()}

🧠 Modo de generación: {self.rutina_generada['metadatos'].get('modo_generacion', 'IA').upper()}
"""
        
        if 'basado_en' in self.rutina_generada['metadatos']:
            info_text += f"📚 Basado en {self.rutina_generada['metadatos']['basado_en']} perfiles similares exitosos\n"
            info_text += f"✅ Nivel de confianza: {self.rutina_generada['metadatos']['confianza']*100:.0f}%"
        
        info_label = tk.Label(info_frame,
                             text=info_text,
                             font=('Helvetica', 10),
                             bg=self.colors['bg_medium'],
                             fg=self.colors['text'],
                             justify='left')
        info_label.pack(anchor='w')
        
        # Rutina semanal
        for dia, ejercicios in self.rutina_generada['rutina_semanal'].items():
            dia_frame = tk.Frame(content_frame, bg=self.colors['bg_medium'], padx=20, pady=15)
            dia_frame.pack(fill='x', pady=10)
            
            dia_label = tk.Label(dia_frame,
                                text=f"📅 {dia.upper()}",
                                font=('Helvetica', 13, 'bold'),
                                bg=self.colors['bg_medium'],
                                fg=self.colors['accent'])
            dia_label.pack(anchor='w', pady=(0, 10))
            
            for idx, ej in enumerate(ejercicios, 1):
                ej_text = f"{idx}. {ej['ejercicio']} ({ej['grupo'].title()})"
                
                if 'series' in ej:
                    ej_text += f"\n   Series: {ej['series']} | Reps: {ej['repeticiones']} | Descanso: {ej['descanso']}"
                else:
                    ej_text += f"\n   Duración: {ej['duracion']} | Intensidad: {ej['intensidad'].title()}"
                
                ej_label = tk.Label(dia_frame,
                                   text=ej_text,
                                   font=('Helvetica', 10),
                                   bg=self.colors['bg_medium'],
                                   fg=self.colors['text'],
                                   justify='left')
                ej_label.pack(anchor='w', pady=5)
        
        # Botones
        btn_frame = tk.Frame(content_frame, bg=self.colors['bg_dark'])
        btn_frame.pack(pady=30)
        
        feedback_btn = tk.Button(btn_frame,
                                text="💬 DAR FEEDBACK",
                                font=('Helvetica', 12, 'bold'),
                                bg=self.colors['success'],
                                fg='white',
                                activebackground=self.colors['accent'],
                                activeforeground='white',
                                padx=30,
                                pady=12,
                                border=0,
                                cursor='hand2',
                                command=self.show_feedback_screen)
        feedback_btn.pack(side='left', padx=10)
        
        new_btn = tk.Button(btn_frame,
                           text="🔄 NUEVA RUTINA",
                           font=('Helvetica', 12, 'bold'),
                           bg=self.colors['bg_light'],
                           fg='white',
                           activebackground=self.colors['accent'],
                           activeforeground='white',
                           padx=30,
                           pady=12,
                           border=0,
                           cursor='hand2',
                           command=self.show_form_screen)
        new_btn.pack(side='left', padx=10)
    
    def get_imc_category(self, imc):
        """Retorna categoría del IMC"""
        if imc < 18.5:
            return "Bajo peso"
        elif imc < 25:
            return "Peso normal"
        elif imc < 30:
            return "Sobrepeso"
        else:
            return "Obesidad"
    
    def show_feedback_screen(self):
        """Pantalla para dar feedback"""
        self.clear_main_container()
        
        frame = tk.Frame(self.main_container, bg=self.colors['bg_medium'], padx=50, pady=40)
        frame.place(relx=0.5, rely=0.5, anchor='center')
        
        # Título
        title = tk.Label(frame,
                        text="💬 TU OPINIÓN AYUDA A LA IA A MEJORAR",
                        font=('Helvetica', 16, 'bold'),
                        bg=self.colors['bg_medium'],
                        fg=self.colors['accent'])
        title.pack(pady=(0, 30))
        
        # Explicación
        exp = """El sistema aprende de tu feedback para generar
rutinas cada vez más precisas y personalizadas."""
        
        exp_label = tk.Label(frame,
                            text=exp,
                            font=('Helvetica', 11),
                            bg=self.colors['bg_medium'],
                            fg=self.colors['text'],
                            justify='center')
        exp_label.pack(pady=(0, 20))
        
        # Pregunta satisfacción
        question = tk.Label(frame,
                           text="¿Cómo te sientes con esta rutina?",
                           font=('Helvetica', 12, 'bold'),
                           bg=self.colors['bg_medium'],
                           fg=self.colors['text'])
        question.pack(pady=10)
        
        # Escala de satisfacción
        satisfaccion_var = tk.IntVar(value=3)
        
        scale_frame = tk.Frame(frame, bg=self.colors['bg_medium'])
        scale_frame.pack(pady=20)
        
        ratings = [
            (1, "😫 Muy difícil"),
            (2, "😕 Difícil"),
            (3, "😊 Adecuada"),
            (4, "😄 Buena"),
            (5, "🤩 Perfecta")
        ]
        
        for value, text in ratings:
            rb = tk.Radiobutton(scale_frame,
                               text=text,
                               variable=satisfaccion_var,
                               value=value,
                               font=('Helvetica', 11),
                               bg=self.colors['bg_medium'],
                               fg=self.colors['text'],
                               selectcolor=self.colors['bg_light'],
                               activebackground=self.colors['bg_medium'],
                               activeforeground=self.colors['accent'])
            rb.pack(anchor='w', pady=5)
        
        # Comentarios
        comment_label = tk.Label(frame,
                                text="Comentarios adicionales (opcional):",
                                font=('Helvetica', 11),
                                bg=self.colors['bg_medium'],
                                fg=self.colors['text'])
        comment_label.pack(pady=(20, 5))
        
        comment_text = tk.Text(frame,
                              height=4,
                              width=50,
                              font=('Helvetica', 10),
                              bg=self.colors['bg_light'],
                              fg=self.colors['text'],
                              insertbackground=self.colors['text'],
                              relief='flat')
        comment_text.pack(pady=10)
        
        # Botón enviar
        def submit_feedback():
            satisfaccion = satisfaccion_var.get()
            comentarios = comment_text.get('1.0', 'end').strip()
            
            self.ai_system.procesar_feedback(satisfaccion, comentarios)
            
            self.show_thanks_screen(satisfaccion)
        
        submit_btn = tk.Button(frame,
                              text="✅ ENVIAR FEEDBACK",
                              font=('Helvetica', 13, 'bold'),
                              bg=self.colors['success'],
                              fg='white',
                              activebackground=self.colors['accent'],
                              activeforeground='white',
                              padx=40,
                              pady=15,
                              border=0,
                              cursor='hand2',
                              command=submit_feedback)
        submit_btn.pack(pady=20)
    
    def show_thanks_screen(self, satisfaccion):
        """Pantalla de agradecimiento"""
        self.clear_main_container()
        
        frame = tk.Frame(self.main_container, bg=self.colors['bg_medium'], padx=60, pady=50)
        frame.place(relx=0.5, rely=0.5, anchor='center')
        
        # Icono según satisfacción
        icon = "🎉" if satisfaccion >= 4 else "👍" if satisfaccion == 3 else "🔄"
        
        thanks_label = tk.Label(frame,
                               text=f"{icon} ¡GRACIAS POR TU FEEDBACK!",
                               font=('Helvetica', 20, 'bold'),
                               bg=self.colors['bg_medium'],
                               fg=self.colors['success'])
        thanks_label.pack(pady=20)
        
        # Mensaje de aprendizaje
        stats = self.ai_system.obtener_estadisticas_sistema()
        
        message = f"""Tu opinión ha sido procesada y guardada.
        
El sistema ha aprendido de tu experiencia y usará
este conocimiento para mejorar las futuras rutinas.

📊 Estado actual del sistema:
   • Generación: {stats['generacion']}
   • Total usuarios: {stats['total_usuarios']}
   • Satisfacción promedio: {stats['promedio_satisfaccion']:.2f}/5
   
¡Cada feedback hace que la IA sea más inteligente!"""
        
        message_label = tk.Label(frame,
                                text=message,
                                font=('Helvetica', 11),
                                bg=self.colors['bg_medium'],
                                fg=self.colors['text'],
                                justify='center')
        message_label.pack(pady=20)
        
        # Botones
        btn_frame = tk.Frame(frame, bg=self.colors['bg_medium'])
        btn_frame.pack(pady=20)
        
        home_btn = tk.Button(btn_frame,
                            text="🏠 INICIO",
                            font=('Helvetica', 12, 'bold'),
                            bg=self.colors['accent'],
                            fg='white',
                            activebackground=self.colors['success'],
                            activeforeground='white',
                            padx=30,
                            pady=12,
                            border=0,
                            cursor='hand2',
                            command=self.show_welcome_screen)
        home_btn.pack(side='left', padx=10)
        
        new_btn = tk.Button(btn_frame,
                           text="➕ NUEVA RUTINA",
                           font=('Helvetica', 12, 'bold'),
                           bg=self.colors['bg_light'],
                           fg='white',
                           activebackground=self.colors['accent'],
                           activeforeground='white',
                           padx=30,
                           pady=12,
                           border=0,
                           cursor='hand2',
                           command=self.show_form_screen)
        new_btn.pack(side='left', padx=10)


def main():
    root = tk.Tk()
    app = GymAIGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()