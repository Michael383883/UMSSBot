# import os
# from .intent_classifier import IntentClassifier
# from .response_generator import ResponseGenerator
# from .nlp_processor import NLPProcessor
# from .knowledge_base import KnowledgeBase
# from .schedule_manager import ScheduleManager


# class UMSSChatBot:
#     def __init__(self, intents_file: str, umss_info_file: str, model_path: str = None):
#         if model_path is None:
#             base_dir = os.path.dirname(
#                 os.path.dirname(os.path.dirname(__file__)))
#             model_path = os.path.join(
#                 base_dir, 'models', 'intent_classifier.pkl')

#         self.intent_classifier = IntentClassifier(
#             intents_file,
#             model_path if os.path.exists(model_path) else None
#         )
#         self.response_generator = ResponseGenerator(
#             intents_file, umss_info_file)

#     def get_response(self, user_input: str, user_id: str = "default") -> str:
#         intent, confidence = self.intent_classifier.classify_intent(user_input)
#         response = self.response_generator.generate_response(
#             intent, user_input, user_id)
#         return response

#     def get_model_info(self):
#         return self.intent_classifier.get_model_info()

#     def get_intent_confidence(self, user_input: str) -> tuple:
#         return self.intent_classifier.classify_intent(user_input)

import os
from .intent_classifier import IntentClassifier
from .response_generator import ResponseGenerator
from .nlp_processor import NLPProcessor
from .knowledge_base import KnowledgeBase
from .schedule_manager import ScheduleManager


class UMSSChatBot:
    def __init__(self, intents_file: str, umss_info_file: str, model_path: str = None):
        if model_path is None:
            base_dir = os.path.dirname(
                os.path.dirname(os.path.dirname(__file__)))
            model_path = os.path.join(
                base_dir, 'models', 'intent_classifier.pkl')

        # Inicializar componentes
        self.intent_classifier = IntentClassifier(
            intents_file,
            model_path if os.path.exists(model_path) else None
        )

        # Crear schedule_manager compartido
        self.schedule_manager = ScheduleManager()

        # Pasar schedule_manager al response_generator
        self.response_generator = ResponseGenerator(
            intents_file, umss_info_file, self.schedule_manager
        )

    def get_response(self, user_input: str, user_id: str = "default") -> str:
        intent, confidence = self.intent_classifier.classify_intent(user_input)

        # Debug
        print(f"DEBUG - Intent: {intent}, Confidence: {confidence:.3f}")

        response = self.response_generator.generate_response(
            intent, user_input, user_id)
        return response

    def get_schedule(self, user_id: str = "default"):
        """Obtener el horario del usuario"""
        return self.schedule_manager.get_user_schedule(user_id)

    def clear_schedule(self, user_id: str = "default"):
        """Limpiar el horario del usuario"""
        if user_id in self.schedule_manager.user_schedules:
            del self.schedule_manager.user_schedules[user_id]
        return True

    def get_model_info(self):
        return self.intent_classifier.get_model_info()

    def get_intent_confidence(self, user_input: str) -> tuple:
        return self.intent_classifier.classify_intent(user_input)
