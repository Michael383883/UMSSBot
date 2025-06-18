import json
import pickle
import os
from typing import Tuple, Dict
from .nlp_processor import NLPProcessor


class IntentClassifier:
    def __init__(self, intents_file: str, model_path: str = None):
        self.nlp_processor = NLPProcessor()

        with open(intents_file, 'r', encoding='utf-8') as f:
            self.intents_data = json.load(f)

        self.trained_model = None
        self.use_ml_model = False

        if model_path and os.path.exists(model_path):
            try:
                self._load_trained_model(model_path)
                self.use_ml_model = True
                print("Modelo ML cargado exitosamente")
            except Exception as e:
                print(f"Error cargando modelo ML: {e}")
                print("Usando clasificador basado en reglas")
        else:
            print("Usando clasificador basado en reglas")

    def _load_trained_model(self, model_path: str):
        with open(model_path, 'rb') as f:
            self.trained_model = pickle.load(f)

    def classify_intent(self, user_input: str) -> Tuple[str, float]:
        user_input = self.nlp_processor.preprocess_text(user_input)

        if self.use_ml_model and self.trained_model:
            return self._classify_with_ml(user_input)
        else:
            return self._classify_with_rules(user_input)

    def _classify_with_ml(self, user_input: str) -> Tuple[str, float]:
        try:
            tokenized_text = ' '.join(self.nlp_processor.tokenize(user_input))

            pipeline = self.trained_model['pipeline']
            prediction = pipeline.predict([tokenized_text])[0]
            confidence = max(pipeline.predict_proba([tokenized_text])[0])

            if confidence < 0.3:
                fallback_intent, fallback_confidence = self._classify_with_rules(
                    user_input)
                if fallback_confidence > confidence:
                    return fallback_intent, fallback_confidence

            return prediction, confidence

        except Exception as e:
            print(f"Error en clasificación ML: {e}")
            return self._classify_with_rules(user_input)

    def _classify_with_rules(self, user_input: str) -> Tuple[str, float]:
        best_intent = "unknown"
        best_score = 0.0

        for intent in self.intents_data['intents']:
            for pattern in intent['patterns']:
                similarity = self.nlp_processor.calculate_similarity(
                    user_input, pattern)
                if similarity > best_score:
                    best_score = similarity
                    best_intent = intent['tag']

        if best_score < 0.3:
            best_intent, best_score = self._keyword_classification(user_input)

        return best_intent, best_score

    def _keyword_classification(self, text: str) -> Tuple[str, float]:
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

        for intent, keywords in keywords_map.items():
            for keyword in keywords:
                if keyword in text:
                    return intent, 0.7

        return "unknown", 0.0

    def get_model_info(self) -> Dict:
        if self.use_ml_model and self.trained_model:
            return {
                'type': 'Machine Learning',
                'version': self.trained_model.get('version', 'Unknown'),
                'accuracy': self.trained_model.get('accuracy', 0.0),
                'labels': self.trained_model.get('intent_labels', [])
            }
        else:
            return {
                'type': 'Rule-based',
                'version': '1.0',
                'accuracy': 0.0,
                'labels': [intent['tag'] for intent in self.intents_data['intents']]
            }
