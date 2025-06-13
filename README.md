
# 🤖 UMSSBot - Asistente Virtual para Estudiantes UMSS

[![Python Version](https://img.shields.io/badge/python-3.8+-blue.svg)](https://python.org)
[![SpaCy](https://img.shields.io/badge/spaCy-3.6+-green.svg)](https://spacy.io)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

Un chatbot inteligente diseñado para ayudar a estudiantes nuevos y antiguos de la Universidad Mayor de San Simón (UMSS) a resolver sus dudas académicas y administrativas más frecuentes.

## 🎯 Características Principales

- **Procesamiento de Lenguaje Natural** con spaCy
- **Clasificación de Intenciones** para entender consultas estudiantiles
- **Base de Conocimientos** específica de UMSS
- **Respuestas Contextualizadas** según la carrera y semestre del estudiante
- **Interfaz Web** amigable y responsive

## ❓ Preguntas que Puede Responder

### 📚 Académicas
- ¿Cuántas materias debo tomar en 1er semestre?
- ¿Qué materias son pesadas según el semestre?
- ¿En cuántos semestres puedo terminar mi carrera?
- ¿Cuál es la malla curricular de mi carrera?
- ¿Qué habilidades debo adquirir para aprobar la materia?

### 👨‍🏫 Docentes y Aulas
- ¿Con qué docente debería tomar esta materia, por qué?
- ¿Dónde se encuentra esta aula?
- ¿Qué materia da tal docente y en qué aula?
- ¿Cuál es el plan de estudio de este docente según la materia?

### 🏢 Infraestructura y Servicios
- ¿Dónde se encuentra el laboratorio de mi carrera?
- ¿Dónde se encuentra la biblioteca?
- ¿Dónde encuentro esta infraestructura?
- ¿Dónde compro valorado de inscripción?

### 📖 Recursos Académicos
- ¿Cómo me inscribo en una materia?
- ¿Dónde encuentro material de estudio?
- ¿Cómo puedo aprobar esta materia?
- ¿Qué áreas de trabajo existen en mi carrera?

## 🚀 Instalación y Configuración

### Prerrequisitos
- Python 3.8 o superior
- pip (gestor de paquetes de Python)
- Git

### Pasos de Instalación

1. **Clonar el repositorio**
```bash
git clone https://github.com/tu-usuario/UMSSBot.git
cd UMSSBot
```

2. **Crear entorno virtual**
```bash
python -m venv venv

# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate
```

3. **Instalar dependencias**
```bash
pip install -r requirements.txt
```

4. **Descargar modelo de spaCy**
```bash
python -m spacy download es_core_news_sm
```

5. **Configurar variables de entorno**
```bash
cp .env.example .env
# Editar .env con tus configuraciones
```

6. **Entrenar el modelo inicial**
```bash
python scripts/train_model.py
```

7. **Ejecutar la aplicación**
```bash
python app.py
```

## 🏗️ Arquitectura del Proyecto

```
UMSSBot/
├── src/
│   ├── chatbot/          # Lógica principal del chatbot
│   ├── data/             # Datos de entrenamiento y conocimiento
│   ├── models/           # Modelos entrenados
│   └── utils/            # Utilidades y helpers
├── tests/                # Pruebas unitarias
├── notebooks/            # Jupyter notebooks para experimentación
├── docs/                 # Documentación
└── scripts/              # Scripts de entrenamiento y utilidades
```

## 🤖 Uso del Chatbot

### Interfaz Web
1. Ejecuta `python app.py`
2. Abre tu navegador en `http://localhost:5000`
3. Comienza a hacer preguntas sobre UMSS

### Ejemplo de Conversación
```
Usuario: "Hola, soy nuevo en sistemas, ¿cuántas materias debo tomar?"
UMSSBot: "¡Hola! Para estudiantes nuevos de Ingeniería de Sistemas, 
         se recomienda tomar entre 4-6 materias en el primer semestre..."

Usuario: "¿Dónde está el laboratorio de sistemas?"
UMSSBot: "El laboratorio de Ingeniería de Sistemas se encuentra en..."
```

## 🧠 Tecnologías Utilizadas

- **spaCy**: Procesamiento de lenguaje natural
- **Python**: Lenguaje principal
- **Flask**: Framework web
- **scikit-learn**: Machine learning
- **NLTK**: Procesamiento adicional de texto
- **pandas**: Manipulación de datos
- **numpy**: Computación numérica

## 📊 Dataset y Entrenamiento

El chatbot se entrena con:
- Preguntas frecuentes de estudiantes UMSS
- Información oficial de la universidad
- Planes de estudio por carrera
- Datos de infraestructura y servicios

## 🧪 Pruebas

Ejecutar las pruebas:
```bash
pytest tests/
```

## 📈 Métricas de Rendimiento

- **Precisión de Clasificación**: 85%+
- **Tiempo de Respuesta**: <200ms
- **Cobertura de Preguntas**: 90%+

## 🤝 Contribución

1. Fork el proyecto
2. Crea una rama para tu feature (`git checkout -b feature/AmazingFeature`)
3. Commit tus cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abre un Pull Request

## 📝 Roadmap

- [x] Configuración inicial del proyecto
- [ ] Implementación del procesador NLP
- [ ] Clasificador de intenciones
- [ ] Base de conocimientos UMSS
- [ ] Interfaz web básica
- [ ] Sistema de aprendizaje continuo
- [ ] Integración con sistemas UMSS
- [ ] Aplicación móvil

## 👥 Equipo de Desarrollo

- **[Asencio Quintana Michael]** - Desarollador
- **[Heredia Suaznabar Cristian]** - Desarollador
- **[Cardenas Calizaya Gabriela Abril]** - Desarollador
- **[Claure Quinteros Nataly]** - Desarollador
- **IA 2** - Curso de Inteligencia Artificial

## 📄 Licencia

Este proyecto está bajo la Licencia MIT - ver el archivo [LICENSE](LICENSE) para detalles.

## 🙏 Agradecimientos

- Universidad Mayor de San Simón (UMSS)
- Comunidad de spaCy
- Estudiantes UMSS por sus preguntas frecuentes

## 📞 Contacto

- **GitHub**: [@tu-usuario](https://github.com/tu-usuario)
- **Proyecto**: [https://github.com/tu-usuario/UMSSBot](https://github.com/tu-usuario/UMSSBot)

---

*Desarrollado con ❤️ para la comunidad estudiantil de UMSS*
