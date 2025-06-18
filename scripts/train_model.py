# === ENTRENAMIENTO Y USO DE UN MODELO DE CLASIFICACIÓN DE INTENCIONES PARA UN CHATBOT UMSS ===
# Este script carga datos de intenciones desde un archivo JSON, los procesa con NLP,
# entrena un modelo de clasificación (SVM con TF-IDF), lo evalúa, guarda y permite probarlo.

import json
import pickle
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.svm import SVC
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, accuracy_score
from sklearn.pipeline import Pipeline
import os
import sys
import re
from collections import Counter

# Agrega al path el directorio 'src' para importar módulos personalizados
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
src_path = os.path.join(project_root, 'src')
sys.path.insert(0, src_path)

# Intenta importar una clase de procesamiento NLP personalizada
try:
    from nlp_processor import NLPProcessor
except ImportError:
    # Si no existe, usa una clase básica para preprocesar y tokenizar texto
    class NLPProcessor:
        def preprocess_text(self, text):
            text = text.lower()
            text = re.sub(r'[^\w\s]', '', text)
            text = re.sub(r'\s+', ' ', text).strip()
            return text

        def tokenize(self, text):
            return text.split()


# Clase principal para entrenar el modelo de intención
class ModelTrainer:
    def __init__(self, intents_file: str, model_output_dir: str):
        self.intents_file = intents_file
        self.model_output_dir = model_output_dir
        self.nlp_processor = NLPProcessor()

        # Crea el directorio donde se guardará el modelo si no existe
        os.makedirs(model_output_dir, exist_ok=True)

        # Verifica que el archivo de intenciones existe
        if not os.path.exists(intents_file):
            raise FileNotFoundError(
                f"No se encontró el archivo: {intents_file}")

        # Carga los datos del archivo JSON
        with open(intents_file, 'r', encoding='utf-8') as f:
            self.intents_data = json.load(f)

    # Prepara los datos de entrenamiento extrayendo y procesando patrones y etiquetas
    def prepare_training_data(self):
        X = []
        y = []

        for intent in self.intents_data['intents']:
            intent_tag = intent['tag']
            for pattern in intent['patterns']:
                processed_text = self.nlp_processor.preprocess_text(pattern)
                tokenized_text = ' '.join(
                    self.nlp_processor.tokenize(processed_text))
                X.append(tokenized_text)
                y.append(intent_tag)

        print(f"Datos preparados: {len(X)} muestras, {len(set(y))} clases")
        print(f"Clases encontradas: {list(set(y))}")
        return X, y

    # Crea el pipeline de entrenamiento con TF-IDF y un clasificador SVM
    def create_pipeline(self):
        pipeline = Pipeline([
            ('tfidf', TfidfVectorizer(
                max_features=1000,
                ngram_range=(1, 2),
                stop_words=None,
                lowercase=True,
                min_df=1,
                max_df=0.8
            )),
            ('classifier', SVC(
                kernel='linear',
                C=1.0,
                probability=True,
                random_state=42
            ))
        ])
        return pipeline

    # Entrena el modelo con los datos preparados y evalúa su precisión
    def train_model(self):
        print("Preparando datos de entrenamiento...")
        X, y = self.prepare_training_data()

        if len(X) < 2:
            raise ValueError(
                "No hay suficientes datos para entrenar el modelo")

        # Muestra la distribución de clases
        class_counts = Counter(y)
        print(f"Distribución de clases: {dict(class_counts)}")

        print("Dividiendo datos en entrenamiento y prueba...")
        test_size = min(0.2, max(0.1, len(X) * 0.2))

        # División estratificada si es posible
        try:
            X_train, X_test, y_train, y_test = train_test_split(
                X, y, test_size=test_size, random_state=42, stratify=y
            )
        except ValueError:
            X_train, X_test, y_train, y_test = train_test_split(
                X, y, test_size=test_size, random_state=42
            )

        print(f"Datos de entrenamiento: {len(X_train)}")
        print(f"Datos de prueba: {len(X_test)}")

        print("Creando pipeline de ML...")
        pipeline = self.create_pipeline()

        print("Entrenando modelo...")
        pipeline.fit(X_train, y_train)

        print("Evaluando modelo...")
        y_pred = pipeline.predict(X_test)
        accuracy = accuracy_score(y_test, y_pred)

        print(f"\nPrecisión del modelo: {accuracy:.4f}")

        if len(X_test) > 0:
            print("\nReporte de clasificación:")
            print(classification_report(y_test, y_pred, zero_division=0))

        return pipeline, accuracy

    # Guarda el modelo entrenado y sus metadatos en un archivo pickle
    def save_model(self, pipeline, accuracy):
        model_path = os.path.join(
            self.model_output_dir, 'intent_classifier.pkl')

        model_data = {
            'pipeline': pipeline,
            'accuracy': accuracy,
            'intent_labels': list(set([intent['tag'] for intent in self.intents_data['intents']])),
            'version': '1.0',
            'training_samples': len([p for intent in self.intents_data['intents'] for p in intent['patterns']])
        }

        with open(model_path, 'wb') as f:
            pickle.dump(model_data, f)

        print(f"Modelo guardado en: {model_path}")
        return model_path

    # Prueba el modelo con frases de ejemplo
    def test_model(self, pipeline):
        test_phrases = [
            "quiero información sobre álgebra",
            "dónde está el aula 691A",
            "recomiéndame un profesor de física",
            "dónde puedo comprar valorados",
            "quiero armar mi horario",
            "ayúdame con programación",
            "hola",
            "adiós",
            "gracias"
        ]

        print("\nProbando modelo con frases de ejemplo:")
        print("-" * 50)

        for phrase in test_phrases:
            try:
                processed_phrase = self.nlp_processor.preprocess_text(phrase)
                tokenized_phrase = ' '.join(
                    self.nlp_processor.tokenize(processed_phrase))

                prediction = pipeline.predict([tokenized_phrase])[0]
                probabilities = pipeline.predict_proba([tokenized_phrase])[0]
                confidence = max(probabilities)

                print(f"Frase: '{phrase}'")
                print(f"Intención: {prediction} (Confianza: {confidence:.3f})")

                # Top 3 predicciones más probables
                classes = pipeline.classes_
                top_indices = np.argsort(probabilities)[-3:][::-1]
                print("Top 3 predicciones:")
                for i, idx in enumerate(top_indices):
                    print(f"  {i+1}. {classes[idx]}: {probabilities[idx]:.3f}")
                print()

            except Exception as e:
                print(f"Error procesando '{phrase}': {e}")
                print()


# Clase para cargar el modelo previamente guardado y hacer predicciones
class ModelLoader:
    def __init__(self, model_path: str):
        self.model_path = model_path
        self.model_data = None
        self.nlp_processor = NLPProcessor()

    # Carga el modelo desde un archivo
    def load_model(self):
        if not os.path.exists(self.model_path):
            raise FileNotFoundError(
                f"Modelo no encontrado en: {self.model_path}")

        with open(self.model_path, 'rb') as f:
            self.model_data = pickle.load(f)

        print(f"Modelo cargado exitosamente")
        print(f"Versión: {self.model_data.get('version', 'Unknown')}")
        print(f"Precisión: {self.model_data.get('accuracy', 0):.4f}")
        print(
            f"Muestras de entrenamiento: {self.model_data.get('training_samples', 'Unknown')}")
        print(f"Etiquetas: {self.model_data.get('intent_labels', [])}")
        return self.model_data

    # Realiza una predicción de intención para una frase dada
    def predict_intent(self, text: str):
        if not self.model_data:
            raise RuntimeError(
                "Modelo no cargado. Ejecuta load_model() primero.")

        processed_text = self.nlp_processor.preprocess_text(text)
        tokenized_text = ' '.join(self.nlp_processor.tokenize(processed_text))

        pipeline = self.model_data['pipeline']
        prediction = pipeline.predict([tokenized_text])[0]
        probabilities = pipeline.predict_proba([tokenized_text])[0]
        confidence = max(probabilities)

        return prediction, confidence


# Función principal para ejecutar todo el proceso de entrenamiento
def main():
    print("=== ENTRENAMIENTO DEL MODELO UMSS CHATBOT ===")

    # Detecta ruta del proyecto y posibles ubicaciones del archivo de intenciones
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(script_dir)

    possible_intents_paths = [
        os.path.join(project_root, 'data', 'intents.json'),
        os.path.join(project_root, 'src', 'data', 'intents.json'),
        os.path.join(script_dir, 'data', 'intents.json'),
        os.path.join(script_dir, '..', 'data', 'intents.json')
    ]

    intents_file = None
    for path in possible_intents_paths:
        if os.path.exists(path):
            intents_file = path
            break

    if not intents_file:
        print(
            "Error: No se encontró el archivo intents.json en las siguientes ubicaciones:")
        for path in possible_intents_paths:
            print(f"  - {path}")
        print(
            "\nPor favor, verifica que el archivo existe y está en la ubicación correcta.")
        return

    model_output_dir = os.path.join(project_root, 'models')

    print(f"Archivo de intenciones: {intents_file}")
    print(f"Directorio de salida: {model_output_dir}")
    print(f"Directorio del proyecto: {project_root}")
    print()

    try:
        trainer = ModelTrainer(intents_file, model_output_dir)

        pipeline, accuracy = trainer.train_model()
        model_path = trainer.save_model(pipeline, accuracy)
        trainer.test_model(pipeline)

        print("=== ENTRENAMIENTO COMPLETADO ===")
        print(f"Modelo guardado en: {model_path}")
        print(f"Precisión final: {accuracy:.4f}")

        # Permite al usuario probar el modelo cargado
        try:
            answer = input(
                "\n¿Quieres probar el modelo cargado? (s/n): ").strip().lower()
            if answer in ['s', 'si', 'sí', 'y', 'yes']:
                test_loaded_model(model_path)
        except KeyboardInterrupt:
            print("\nSaliendo...")

    except Exception as e:
        print(f"Error durante el entrenamiento: {e}")
        import traceback
        traceback.print_exc()


# Función para probar el modelo ya cargado con frases introducidas por el usuario
def test_loaded_model(model_path):
    print("\n=== PROBANDO MODELO CARGADO ===")

    try:
        loader = ModelLoader(model_path)
        loader.load_model()

        print("\nEscribe frases para probar el modelo (escribe 'quit', 'salir' o presiona Ctrl+C para salir)")

        while True:
            try:
                user_input = input("\nTu frase: ").strip()
                if user_input.lower() in ['quit', 'salir', 'exit']:
                    break

                if not user_input:
                    continue

                intent, confidence = loader.predict_intent(user_input)
                print(f"Intención predicha: {intent}")
                print(f"Confianza: {confidence:.3f}")

                if confidence < 0.5:
                    print("⚠️  Confianza baja - La predicción puede no ser precisa")
                elif confidence > 0.8:
                    print("✅ Confianza alta - Predicción confiable")

            except KeyboardInterrupt:
                break
            except Exception as e:
                print(f"Error al procesar: {e}")

        print("¡Gracias por probar el modelo!")

    except Exception as e:
        print(f"Error cargando el modelo: {e}")


# Punto de entrada del script
if __name__ == "__main__":
    main()
