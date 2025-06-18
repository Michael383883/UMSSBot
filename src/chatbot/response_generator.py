import json
import random
import re
from typing import Dict, List, Optional
from .schedule_manager import ScheduleManager
from .knowledge_base import KnowledgeBase


class ResponseGenerator:
    def __init__(self, intents_file: str, umss_info_file: str, schedule_manager: ScheduleManager = None):
        # Cargar intents
        with open(intents_file, 'r', encoding='utf-8') as f:
            self.intents_data = json.load(f)

        # Cargar datos reales de UMSS
        with open(umss_info_file, 'r', encoding='utf-8') as f:
            self.umss_data = json.load(f)

        # Inicializar componentes
        self.knowledge_base = KnowledgeBase(umss_info_file)
        self.schedule_manager = schedule_manager or ScheduleManager()

        # Mapear intents a respuestas
        self.intent_responses = {}
        for intent in self.intents_data['intents']:
            self.intent_responses[intent['tag']] = intent['responses']

        # Mapeo de materias a las claves en el JSON
        self.subject_mapping = {
            'algebra': 'algebra_1',
            'álgebra': 'algebra_1',
            'calculo': 'calculo_1',
            'cálculo': 'calculo_1',
            'fisica': 'fisica_general',
            'física': 'fisica_general',
            'programacion': 'introduccion_programacion',
            'programación': 'introduccion_programacion',
            'ingles': 'ingles_1',
            'inglés': 'ingles_1'
        }

        # Almacenar las últimas opciones mostradas por usuario
        self.pending_selections = {}

    def generate_response(self, intent: str, user_input: str, user_id: str) -> str:
        """Generar respuesta basada en el intent y el input del usuario"""

        # Debug
        print(
            f"DEBUG - Generando respuesta para: intent={intent}, input='{user_input}'")

        # Verificar si está seleccionando una opción de horario
        option_response = self._handle_option_selection(user_input, user_id)
        if option_response:
            return option_response

        # Manejar intents relacionados con horarios
        if intent == 'horario' or 'horario' in user_input.lower():
            return self._handle_schedule_intent(user_input, user_id)

        # Manejar intents de materias específicas
        if intent in ['algebra', 'fisica', 'calculo', 'programacion', 'ingles']:
            return self._handle_subject_intent(intent, user_input, user_id)

        # Verificar si es una consulta de horario
        if any(keyword in user_input.lower() for keyword in ['mi horario', 'ver horario', 'mostrar horario']):
            return self._show_user_schedule(user_id)

        # Respuestas estándar
        if intent in self.intent_responses:
            base_response = random.choice(self.intent_responses[intent])

            # Agregar información específica según el intent
            if intent == 'aulas':
                return self._handle_classroom_query(user_input, base_response)
            elif intent == 'recomendacion_docente':
                return self._handle_teacher_recommendation(user_input, base_response)
            elif intent == 'valorados':
                return self._handle_valorados_query(base_response)

            return base_response

        # Respuesta por defecto
        return "No estoy seguro de cómo ayudarte con eso. ¿Podrías ser más específico? Puedo ayudarte con horarios, materias, ubicaciones y más."

    def _handle_schedule_intent(self, user_input: str, user_id: str) -> str:
        """Manejar intents relacionados con horarios"""

        # Detectar si quiere ver su horario actual
        if any(keyword in user_input.lower() for keyword in ['mi horario', 'ver horario', 'mostrar horario']):
            return self._show_user_schedule(user_id)

        # Detectar si quiere armar horario con una materia específica
        if 'armar' in user_input.lower() or 'crear' in user_input.lower():
            return self._handle_schedule_creation(user_input, user_id)

        # Respuesta general sobre horarios
        return """🗓️ **Gestión de Horarios**

Te puedo ayudar a:
• **Ver tu horario actual**: Di "ver mi horario"
• **Armar horario con materias**: Di "armar horario con [materia]"
• **Agregar materias**: Di "agregar [materia] a mi horario"

¿Qué te gustaría hacer?"""

    def _handle_subject_intent(self, subject: str, user_input: str, user_id: str) -> str:
        """Manejar intents de materias específicas usando datos reales"""

        # Si menciona horario, ofrecer agregar la materia
        if any(keyword in user_input.lower() for keyword in ['horario', 'armar', 'agregar']):
            return self._offer_subject_addition(subject, user_id)

        # Obtener información real de la materia
        return self._get_subject_info(subject)

    def _get_subject_info(self, subject: str) -> str:
        """Obtener información real de la materia desde el JSON"""

        # Mapear el subject al nombre en el JSON
        json_key = self.subject_mapping.get(subject.lower())

        if not json_key or json_key not in self.umss_data['docentes']:
            return f"No tengo información disponible sobre {subject}."

        docentes = self.umss_data['docentes'][json_key]

        # Nombres de materias para mostrar
        subject_names = {
            'algebra_1': 'Álgebra I',
            'calculo_1': 'Cálculo I',
            'fisica_general': 'Física General',
            'introduccion_programacion': 'Introducción a la Programación',
            'ingles_1': 'Inglés I'
        }

        subject_name = subject_names.get(json_key, subject.title())

        response = f"📚 **{subject_name}**\n\n"
        response += "👨‍🏫 **Docentes disponibles:**\n"

        for i, docente in enumerate(docentes, 1):
            response += f"\n**{i}. {docente['nombre']}**\n"
            response += f"💡 {docente['recomendacion']}\n"

            # Mostrar horarios
            horarios_formatted = []
            for horario in docente['horarios']:
                horario_readable = self._format_schedule_readable(horario)
                horarios_formatted.append(horario_readable)

            response += f"🕒 Horarios: {', '.join(horarios_formatted)}\n"

            # Mostrar aulas
            if docente['aulas']:
                response += f"📍 Aulas: {', '.join(docente['aulas'])}\n"

        response += f"\n¿Te gustaría que te ayude a armar tu horario con {subject_name}? Solo di \"armar horario con {subject}\""

        return response

    def _handle_option_selection(self, user_input: str, user_id: str) -> Optional[str]:
        """Manejar selección de opciones de horario"""

        # Verificar si hay opciones pendientes para este usuario
        if user_id not in self.pending_selections:
            return None

        # Buscar número de opción en el input
        option_patterns = [
            r'opci[oó]n\s*(\d+)',
            r'opci[oó]n\s*n[uú]mero\s*(\d+)',
            r'^(\d+)$',
            r'la\s*(\d+)',
            r'n[uú]mero\s*(\d+)'
        ]

        selected_option = None
        for pattern in option_patterns:
            match = re.search(pattern, user_input.lower().strip())
            if match:
                selected_option = int(match.group(1))
                break

        if selected_option is None:
            return None

        # Obtener las opciones pendientes
        pending_data = self.pending_selections[user_id]
        subject_name = pending_data['subject_name']
        docentes = pending_data['docentes']

        # Verificar que la opción sea válida
        if selected_option < 1 or selected_option > len(docentes):
            return f"❌ Opción inválida. Por favor selecciona un número entre 1 y {len(docentes)}."

        # Obtener el docente seleccionado (índice base 0)
        selected_docente = docentes[selected_option - 1]

        # Verificar conflictos de horario
        conflicts = []
        for horario in selected_docente['horarios']:
            schedule_conflicts = self.schedule_manager.check_time_conflict(
                user_id, horario)
            conflicts.extend(schedule_conflicts)

        if conflicts:
            response = f"❌ **La Opción {selected_option} tiene conflictos de horario:**\n\n"
            for conflict in conflicts:
                response += f"• Choca con: {conflict}\n"
            response += "\n¿Quieres seleccionar otra opción?"
            return response

        # Agregar la materia al horario
        success = self.schedule_manager.add_subject_to_schedule(
            user_id,
            subject_name,
            selected_docente['nombre'],
            selected_docente['horarios'],
            ', '.join(selected_docente['aulas'])
        )

        if success:
            # Limpiar opciones pendientes
            del self.pending_selections[user_id]

            # Obtener estadísticas del horario actualizado
            user_schedule = self.schedule_manager.get_user_schedule(user_id)
            total_subjects = len(user_schedule['subjects'])

            response = f"🎉 **¡Materia agregada exitosamente!**\n\n"
            response += f"📚 **{subject_name}** ha sido agregado a tu horario\n"
            response += f"👨‍🏫 **Profesor:** {selected_docente['nombre']}\n"

            # Formatear horarios de manera legible
            horarios_formatted = []
            for horario in selected_docente['horarios']:
                horario_readable = self._format_schedule_readable(horario)
                horarios_formatted.append(horario_readable)

            response += f"🕒 **Horarios:** {', '.join(horarios_formatted)}\n"
            response += f"📍 **Aulas:** {', '.join(selected_docente['aulas'])}\n\n"
            response += f"📊 **Tienes {total_subjects} materia{'s' if total_subjects != 1 else ''} en tu horario**\n\n"
            response += "¿Quieres ver tu horario completo? Di 'ver mi horario'"

            return response
        else:
            return "❌ Hubo un error al agregar la materia. Por favor intenta de nuevo."

    def _offer_subject_addition(self, subject: str, user_id: str) -> str:
        """Ofrecer agregar una materia al horario usando datos reales"""

        # Mapear el subject al nombre en el JSON
        json_key = self.subject_mapping.get(subject.lower())

        if not json_key or json_key not in self.umss_data['docentes']:
            return f"Aún no tengo información de horarios para {subject}. ¿Te puedo ayudar con otra materia?"

        docentes = self.umss_data['docentes'][json_key]

        # Nombres de materias para mostrar
        subject_names = {
            'algebra_1': 'Álgebra I',
            'calculo_1': 'Cálculo I',
            'fisica_general': 'Física General',
            'introduccion_programacion': 'Introducción a la Programación',
            'ingles_1': 'Inglés I'
        }

        subject_name = subject_names.get(json_key, subject.title())

        # Guardar opciones para selección posterior
        self.pending_selections[user_id] = {
            'subject_name': subject_name,
            'docentes': docentes
        }

        response = f"🗓️ **Horarios disponibles para {subject_name}:**\n\n"

        for i, docente in enumerate(docentes, 1):
            response += f"**Opción {i}:**\n"
            response += f"👨‍🏫 {docente['nombre']}\n"

            # Formatear horarios de manera legible
            horarios_formatted = []
            for horario in docente['horarios']:
                horario_readable = self._format_schedule_readable(horario)
                horarios_formatted.append(horario_readable)

            response += f"🕒 {', '.join(horarios_formatted)}\n"

            if docente['aulas']:
                response += f"📍 Aulas: {', '.join(docente['aulas'])}\n"

            response += f"💡 {docente['recomendacion']}\n\n"

        # Verificar conflictos con horario actual
        user_schedule = self.schedule_manager.get_user_schedule(user_id)
        if user_schedule['subjects']:
            response += "🔍 **Verificando conflictos con tu horario actual...**\n\n"

            for i, docente in enumerate(docentes, 1):
                conflicts = []
                for horario in docente['horarios']:
                    schedule_conflicts = self.schedule_manager.check_time_conflict(
                        user_id, horario)
                    conflicts.extend(schedule_conflicts)

                if conflicts:
                    response += f"❌ **Opción {i}**: Tiene conflictos\n"
                    for conflict in conflicts:
                        response += f"   • Choca con: {conflict}\n"
                else:
                    response += f"✅ **Opción {i}**: Sin conflictos - ¡Disponible!\n"

                response += "\n"

        response += "Para seleccionar una opción, simplemente escribe:\n"
        response += "• **'opción 1'** o **'1'** para la primera opción\n"
        response += "• **'opción 2'** o **'2'** para la segunda opción\n"
        response += "• **'opción 3'** o **'3'** para la tercera opción\n"
        response += "• **'opción 4'** o **'4'** para la cuarta opción\n"

        return response

    def _format_schedule_readable(self, schedule: str) -> str:
        """Convertir formato de horario a legible (ej: 'LU 645-0815' -> 'Lun 06:45-08:15')"""

        day_map = {
            'LU': 'Lun',
            'MA': 'Mar',
            'MI': 'Mié',
            'JU': 'Jue',
            'VI': 'Vie',
            'SA': 'Sáb',
            'DO': 'Dom'
        }

        parts = schedule.split()
        if len(parts) != 2:
            return schedule

        day_code = parts[0]
        time_range = parts[1]

        # Convertir día
        day_readable = day_map.get(day_code, day_code)

        # Convertir horario
        if '-' in time_range:
            start_time, end_time = time_range.split('-')

            # Formatear tiempo (agregar : si no está presente)
            def format_time(time_str):
                if len(time_str) == 3:  # ej: 645
                    return f"0{time_str[0]}:{time_str[1:]}"
                elif len(time_str) == 4:  # ej: 1245
                    return f"{time_str[:2]}:{time_str[2:]}"
                return time_str

            start_formatted = format_time(start_time)
            end_formatted = format_time(end_time)

            return f"{day_readable} {start_formatted}-{end_formatted}"

        return schedule

    def _handle_schedule_creation(self, user_input: str, user_id: str) -> str:
        """Manejar creación de horarios"""

        # Detectar materia mencionada usando el mapeo
        materia_detectada = None
        for materia_key in self.subject_mapping.keys():
            if materia_key in user_input.lower():
                # Usar la clave normalizada
                materia_detectada = materia_key.replace('álgebra', 'algebra').replace('física', 'fisica').replace(
                    'cálculo', 'calculo').replace('programación', 'programacion').replace('inglés', 'ingles')
                break

        if materia_detectada:
            return self._offer_subject_addition(materia_detectada, user_id)

        return """🗓️ **Armar Horario**

¿Con qué materia quieres armar tu horario?

📚 **Materias disponibles:**
• Álgebra I
• Física General
• Cálculo I
• Introducción a la Programación
• Inglés I

Solo di "armar horario con [materia]" y te mostraré las opciones disponibles."""

    def _show_user_schedule(self, user_id: str) -> str:
        """Mostrar el horario actual del usuario"""
        return self.schedule_manager.format_schedule_display(user_id)

    def _handle_classroom_query(self, user_input: str, base_response: str) -> str:
        """Manejar consultas sobre aulas usando datos reales"""

        # Extraer número de aula si está presente
        aula_match = re.search(r'(\d+[A-Z]?)', user_input)
        if aula_match:
            aula = aula_match.group(1)

            # Buscar el aula en los datos reales
            aulas_info = self.umss_data.get('aulas', {})
            edificio_principal = aulas_info.get('edificio_principal', {})

            ubicacion = None
            for piso, aulas_piso in edificio_principal.items():
                if aula in aulas_piso:
                    piso_num = piso.replace('piso_', '')
                    ubicacion = f"Edificio principal, piso {piso_num}"
                    break

            # Verificar si es laboratorio
            laboratorios = aulas_info.get('laboratorios', {})
            for tipo_lab, aulas_lab in laboratorios.items():
                if aula in aulas_lab:
                    lab_name = tipo_lab.replace('_', ' ').title()
                    ubicacion = f"{lab_name} - {ubicacion}" if ubicacion else lab_name
                    break

            if ubicacion:
                return f"🏛️ **Ubicación del Aula {aula}**\n\n📍 {ubicacion}\n\n{base_response}"
            else:
                return f"🏛️ **Aula {aula}**\n\n{base_response}\n\n📍 No encontré la ubicación específica del aula {aula}. Te recomiendo preguntar en secretaría."

        return base_response

    def _handle_teacher_recommendation(self, user_input: str, base_response: str) -> str:
        """Manejar recomendaciones de docentes usando datos reales"""

        # Detectar materia mencionada
        materia_detectada = None
        for materia_key in self.subject_mapping.keys():
            if materia_key in user_input.lower():
                materia_detectada = self.subject_mapping[materia_key]
                break

        if materia_detectada and materia_detectada in self.umss_data['docentes']:
            docentes = self.umss_data['docentes'][materia_detectada]

            subject_names = {
                'algebra_1': 'Álgebra I',
                'calculo_1': 'Cálculo I',
                'fisica_general': 'Física General',
                'introduccion_programacion': 'Introducción a la Programación',
                'ingles_1': 'Inglés I'
            }

            subject_name = subject_names.get(
                materia_detectada, materia_detectada)

            response = f"👨‍🏫 **Recomendaciones para {subject_name}:**\n\n"

            for docente in docentes:
                response += f"• **{docente['nombre']}** - {docente['recomendacion']}\n"

            response += f"\n{base_response}"
            return response

        return base_response

    def _handle_valorados_query(self, base_response: str) -> str:
        """Manejar consultas sobre valorados usando datos reales"""

        valorados = self.umss_data.get('valorados', [])

        if not valorados:
            return base_response

        response = "📄 **Dónde conseguir valorados:**\n\n"

        for lugar in valorados:
            response += f"🏪 **{lugar['lugar']}**\n"
            response += f"📍 {lugar['ubicacion']}\n"
            response += f"🕒 Horario: {lugar['horario']}\n"
            if 'contacto' in lugar:
                response += f"📞 Contacto: {lugar['contacto']}\n"
            response += "\n"

        response += "💡 **Consejos adicionales:**\n"
        response += "• Pregunta por material específico de tu materia\n"
        response += "• Algunos profesores tienen sus propias fotocopiadoras recomendadas\n"
        response += "• Consulta con estudiantes de semestres superiores"

        return response
