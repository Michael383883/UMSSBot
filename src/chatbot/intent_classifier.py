# Importación de librerías necesarias
import json
import pickle
import os
from typing import Tuple, Dict

from .nlp_processor import NLPProcessor

# Clase que clasifica la intención del texto ingresado por el usuario


class IntentClassifier:
    def __init__(self, intents_file: str, model_path: str = None):
        # Inicializa el procesador de lenguaje natural
        self.nlp_processor = NLPProcessor()

        # Carga las intenciones definidas en el archivo JSON
        with open(intents_file, 'r', encoding='utf-8') as f:
            self.intents_data = json.load(f)

        # Inicializa el modelo entrenado y una bandera para saber si se usa ML
        self.trained_model = None
        self.use_ml_model = False

        # Si se proporciona un modelo y existe, se intenta cargar
        if model_path and os.path.exists(model_path):
            try:
                # Carga modelo con pickle
                self._load_trained_model(model_path)
                self.use_ml_model = True               # Activa el uso de ML
                print("Modelo ML cargado exitosamente")
            except Exception as e:
                # Si falla al cargar el modelo, se usa el sistema basado en reglas
                print(f"Error cargando modelo ML: {e}")
                print("Usando clasificador basado en reglas")
        else:
            # Si no hay modelo, también se usa el sistema de reglas
            print("Usando clasificador basado en reglas")

    # Método privado para cargar el modelo entrenado desde archivo .pkl
    def _load_trained_model(self, model_path: str):
        with open(model_path, 'rb') as f:
            self.trained_model = pickle.load(f)

    # Método principal para clasificar la intención
    def classify_intent(self, user_input: str) -> Tuple[str, float]:
        user_input = self.nlp_processor.preprocess_text(
            user_input)  # Limpieza y normalización del texto

        # Si se está usando ML y hay modelo cargado
        if self.use_ml_model and self.trained_model:
            return self._classify_with_ml(user_input)
        else:
            return self._classify_with_rules(user_input)

    # Clasificación usando un modelo de Machine Learning
    def _classify_with_ml(self, user_input: str) -> Tuple[str, float]:
        try:
            # Tokeniza el texto para pasarlo al modelo
            tokenized_text = ' '.join(self.nlp_processor.tokenize(user_input))

            # Accede al pipeline entrenado
            pipeline = self.trained_model['pipeline']
            prediction = pipeline.predict([tokenized_text])[
                0]  # Predice la intención
            confidence = max(pipeline.predict_proba([tokenized_text])[
                             0])  # Obtiene la mayor probabilidad

            # Si la confianza es baja, se prueba con el clasificador basado en reglas
            if confidence < 0.3:
                fallback_intent, fallback_confidence = self._classify_with_rules(
                    user_input)
                # Se elige la mejor entre ambas
                if fallback_confidence > confidence:
                    return fallback_intent, fallback_confidence

            return prediction, confidence

        except Exception as e:
            # En caso de error, se vuelve a las reglas
            print(f"Error en clasificación ML: {e}")
            return self._classify_with_rules(user_input)

    # Clasificación basada en reglas (comparación de similitud)
    def _classify_with_rules(self, user_input: str) -> Tuple[str, float]:
        best_intent = "unknown"  # Intención por defecto si no se encuentra otra
        best_score = 0.0         # Mayor similitud encontrada

        # Recorre cada intención y sus patrones
        for intent in self.intents_data['intents']:
            for pattern in intent['patterns']:
                similarity = self.nlp_processor.calculate_similarity(
                    user_input, pattern)  # Calcula similitud entre lo que dijo el usuario y el patrón
                if similarity > best_score:
                    best_score = similarity
                    best_intent = intent['tag']

        # Si la similitud fue baja, usa clasificación por palabras clave
        if best_score < 0.3:
            best_intent, best_score = self._keyword_classification(user_input)

        return best_intent, best_score

    # Método alternativo por palabras clave específicas por intención
    def _keyword_classification(self, text: str) -> Tuple[str, float]:
        # Diccionario de intenciones y sus palabras clave asociadas
        keywords_map = {
            'valorados': ['valorados', 'segunda', 'instancia', '2da', 'fotocopias'],
            'aulas': ['aula', 'salon', 'donde', 'ubicacion'],
            'recomendacion_docente': ['profesor', 'docente', 'recomienda', 'mejor'],
            'algebra': ['algebra', 'matematicas'],
            'calculo': ['calculo', 'derivadas', 'integrales'],
            'ingles': ['ingles', 'english'],
            'fisica': ['fisica'],
            'programacion': ['programacion', 'coding', 'programar'],
            'horario': ['horario', 'armar', 'crear', 'ver', 'mostrar']
        }

        # Recorre cada intención y busca si alguna palabra clave está presente
        for intent, keywords in keywords_map.items():
            for keyword in keywords:
                if keyword in text:
                    return intent, 0.7  # Retorna la intención con una confianza fija

        return "unknown", 0.0  # Si no se encuentra coincidencia

    # Devuelve información del modelo actual (tipo, precisión, etiquetas, etc.)
    def get_model_info(self) -> Dict:
        if self.use_ml_model and self.trained_model:
            return {
                'type': 'Machine Learning',
                'version': self.trained_model.get('version', 'Unknown'),
                'accuracy': self.trained_model.get('accuracy', 0.0),
                'labels': self.trained_model.get('intent_labels', [])
            }
        else:
            # Información si se usa clasificación por reglas
            return {
                'type': 'Rule-based',
                'version': '1.0',
                'accuracy': 0.0,
                'labels': [intent['tag'] for intent in self.intents_data['intents']]
            }
