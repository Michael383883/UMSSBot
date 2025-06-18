# Importación de módulos necesarios para la aplicación Flask
from flask import Flask, render_template, request, jsonify, session
import os  # Para manejar rutas del sistema
import uuid  # Para generar identificadores únicos de usuario
from src.chatbot import UMSSChatBot  # Importa la clase principal del chatbot

# Inicializa la aplicación Flask
app = Flask(__name__)

# Clave secreta necesaria para manejar sesiones de usuario
app.secret_key = 'umss_chatbot_secret_key_2024'

# Rutas a los archivos de configuración del chatbot
intents_file = os.path.join(
    'src', 'data', 'intents.json')  # Archivo de intenciones
# Archivo con datos de materias/docentes
umss_info_file = os.path.join('src', 'data', 'umss_info.json')

# Verificaciones para asegurar que los archivos existen antes de usarlos
if not os.path.exists(intents_file):
    print(f"Advertencia: No se encontró {intents_file}")
if not os.path.exists(umss_info_file):
    print(f"Advertencia: No se encontró {umss_info_file}")

# Inicializa la instancia del chatbot pasando los archivos necesarios
chatbot = UMSSChatBot(intents_file, umss_info_file)


@app.route('/')
def index():
    """Ruta principal que muestra la interfaz del chatbot"""
    if 'user_id' not in session:
        session['user_id'] = str(uuid.uuid4())  # Asigna un ID único al usuario
    return render_template('index.html')  # Renderiza la página HTML principal


@app.route('/chat', methods=['POST'])
def chat():
    """Ruta POST para recibir mensajes del usuario y devolver respuestas del bot"""
    try:
        # Obtiene mensaje JSON del frontend
        user_message = request.json.get('message', '')
        # Recupera ID del usuario desde la sesión
        user_id = session.get('user_id', 'default')

        # Log para depuración
        print(f"DEBUG - Usuario {user_id}: {user_message}")

        bot_response = chatbot.get_response(
            user_message, user_id)  # Obtiene respuesta del chatbot

        # Muestra parte de la respuesta para depurar
        print(f"DEBUG - Respuesta: {bot_response[:100]}...")

        # Devuelve respuesta al frontend
        return jsonify({'response': bot_response})

    except Exception as e:
        print(f"Error en chat: {e}")  # Muestra errores si hay fallos
        return jsonify({'response': 'Lo siento, ocurrió un error. Por favor intenta de nuevo.'}), 500


@app.route('/schedule', methods=['GET'])
def get_schedule():
    """Ruta GET para obtener el horario del usuario actual"""
    try:
        # Recupera el ID de la sesión
        user_id = session.get('user_id', 'default')
        # Obtiene el horario usando el chatbot
        schedule = chatbot.get_schedule(user_id)

        # Log para depuración
        print(f"DEBUG - Horario para {user_id}: {schedule}")

        return jsonify(schedule)  # Devuelve el horario en formato JSON

    except Exception as e:
        print(f"Error obteniendo horario: {e}")
        return jsonify({'subjects': {}, 'schedule_grid': {}}), 500


@app.route('/clear_schedule', methods=['POST'])
def clear_schedule():
    """Ruta POST para borrar el horario del usuario"""
    try:
        user_id = session.get('user_id', 'default')
        # Limpia el horario en la clase del chatbot
        success = chatbot.clear_schedule(user_id)

        print(f"DEBUG - Horario limpiado para {user_id}: {success}")  # Debug

        # Devuelve confirmación al frontend
        return jsonify({'success': success})

    except Exception as e:
        print(f"Error limpiando horario: {e}")
        return jsonify({'success': False}), 500


@app.route('/debug/schedule/<user_id>')
def debug_schedule(user_id):
    """Ruta para ver el horario completo de un usuario específico (modo debug)"""
    try:
        schedule = chatbot.get_schedule(user_id)
        return jsonify({
            'user_id': user_id,
            'schedule': schedule,
            'all_schedules': chatbot.schedule_manager.user_schedules  # Muestra todos los horarios
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/debug/users')
def debug_users():
    """Ruta para listar todos los usuarios registrados en el sistema (modo debug)"""
    try:
        return jsonify({
            'all_users': list(chatbot.schedule_manager.user_schedules.keys()),
            'schedules': chatbot.schedule_manager.user_schedules
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# Bloque principal que se ejecuta al iniciar el servidor Flask
if __name__ == '__main__':
    print("=== UMSS ChatBot Iniciando ===")
    # Muestra la ruta del archivo de intenciones
    print(f"Archivo de intents: {intents_file}")
    # Muestra la ruta del archivo de info
    print(f"Archivo de info UMSS: {umss_info_file}")
    # Información del modelo de lenguaje usado
    print(f"Modelo ML: {chatbot.get_model_info()}")
    print("==============================")

    # Inicia la aplicación en modo debug y accesible desde cualquier IP
    app.run(debug=True, host='0.0.0.0', port=5000)
