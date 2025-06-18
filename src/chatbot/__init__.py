import os
# Clasificador de intenciones (usa modelo entrenado)
from .intent_classifier import IntentClassifier
# Generador de respuestas basadas en la intención detectada
from .response_generator import ResponseGenerator
# Procesador de texto (tokenización, limpieza, etc.)
from .nlp_processor import NLPProcessor
# Base de conocimiento de la UMSS (datos, ubicaciones, etc.)
from .knowledge_base import KnowledgeBase
# Gestor de horarios del usuario
from .schedule_manager import ScheduleManager

class UMSSChatBot:
    def __init__(self, intents_file: str, umss_info_file: str, model_path: str = None):
        # Si no se proporciona una ruta del modelo, se usa la ruta por defecto
        if model_path is None:
            base_dir = os.path.dirname(
                # Subir 3 niveles en el directorio
                os.path.dirname(os.path.dirname(__file__)))
            model_path = os.path.join(
                base_dir, 'models', 'intent_classifier.pkl')  # Ruta por defecto del modelo

        # Inicializa el clasificador de intenciones con el archivo de intenciones y el modelo entrenado
        self.intent_classifier = IntentClassifier(
            intents_file,
            # Usa el modelo solo si existe
            model_path if os.path.exists(model_path) else None
        )

        # Crea un gestor de horarios (compartido entre módulos)
        self.schedule_manager = ScheduleManager()

        # Inicializa el generador de respuestas, pasándole el gestor de horarios
        self.response_generator = ResponseGenerator(
            intents_file, umss_info_file, self.schedule_manager
        )

    # Método para obtener la respuesta a una frase del usuario
    def get_response(self, user_input: str, user_id: str = "default") -> str:
        # Clasifica la intención del texto ingresado
        intent, confidence = self.intent_classifier.classify_intent(user_input)

        # Mensaje de depuración con intención y nivel de confianza
        print(f"DEBUG - Intent: {intent}, Confidence: {confidence:.3f}")

        # Genera una respuesta basada en la intención detectada
        response = self.response_generator.generate_response(
            intent, user_input, user_id)
        return response

    # Retorna el horario actual del usuario
    def get_schedule(self, user_id: str = "default"):
        """Obtener el horario del usuario"""
        return self.schedule_manager.get_user_schedule(user_id)

    # Limpia (borra) el horario del usuario
    def clear_schedule(self, user_id: str = "default"):
        """Limpiar el horario del usuario"""
        if user_id in self.schedule_manager.user_schedules:
            del self.schedule_manager.user_schedules[user_id]
        return True

    # Devuelve información del modelo de clasificación cargado
    def get_model_info(self):
        return self.intent_classifier.get_model_info()

    # Devuelve la intención y confianza estimada para una entrada de texto
    def get_intent_confidence(self, user_input: str) -> tuple:
        return self.intent_classifier.classify_intent(user_input)
