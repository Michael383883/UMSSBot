# from flask import Flask, render_template, request, jsonify, session
# import os
# import uuid
# from src.chatbot import UMSSChatBot

# app = Flask(__name__)
# app.secret_key = 'umss_chatbot_secret_key_2024'

# intents_file = os.path.join('src', 'data', 'intents.json')
# umss_info_file = os.path.join('src', 'data', 'umss_info.json')
# chatbot = UMSSChatBot(intents_file, umss_info_file)


# @app.route('/')
# def index():
#     if 'user_id' not in session:
#         session['user_id'] = str(uuid.uuid4())
#     return render_template('index.html')


# @app.route('/chat', methods=['POST'])
# def chat():
#     user_message = request.json.get('message', '')
#     user_id = session.get('user_id', 'default')

#     bot_response = chatbot.get_response(user_message, user_id)
#     return jsonify({'response': bot_response})


# @app.route('/schedule', methods=['GET'])
# def get_schedule():
#     user_id = session.get('user_id', 'default')
#     schedule = chatbot.response_generator.schedule_manager.get_user_schedule(
#         user_id)
#     return jsonify(schedule)


# @app.route('/clear_schedule', methods=['POST'])
# def clear_schedule():
#     user_id = session.get('user_id', 'default')
#     if user_id in chatbot.response_generator.schedule_manager.user_schedules:
#         del chatbot.response_generator.schedule_manager.user_schedules[user_id]
#     return jsonify({'success': True})


# if __name__ == '__main__':
#     app.run(debug=True)


from flask import Flask, render_template, request, jsonify, session
import os
import uuid
from src.chatbot import UMSSChatBot

app = Flask(__name__)
app.secret_key = 'umss_chatbot_secret_key_2024'

# Configurar rutas de archivos
intents_file = os.path.join('src', 'data', 'intents.json')
umss_info_file = os.path.join('src', 'data', 'umss_info.json')

# Verificar que los archivos existen
if not os.path.exists(intents_file):
    print(f"Advertencia: No se encontró {intents_file}")
if not os.path.exists(umss_info_file):
    print(f"Advertencia: No se encontró {umss_info_file}")

# Inicializar chatbot
chatbot = UMSSChatBot(intents_file, umss_info_file)


@app.route('/')
def index():
    """Página principal"""
    if 'user_id' not in session:
        session['user_id'] = str(uuid.uuid4())
    return render_template('index.html')


@app.route('/chat', methods=['POST'])
def chat():
    """Endpoint para el chat"""
    try:
        user_message = request.json.get('message', '')
        user_id = session.get('user_id', 'default')

        print(f"DEBUG - Usuario {user_id}: {user_message}")  # Debug

        bot_response = chatbot.get_response(user_message, user_id)

        print(f"DEBUG - Respuesta: {bot_response[:100]}...")  # Debug

        return jsonify({'response': bot_response})

    except Exception as e:
        print(f"Error en chat: {e}")
        return jsonify({'response': 'Lo siento, ocurrió un error. Por favor intenta de nuevo.'}), 500


@app.route('/schedule', methods=['GET'])
def get_schedule():
    """Obtener horario del usuario"""
    try:
        user_id = session.get('user_id', 'default')
        schedule = chatbot.get_schedule(user_id)

        print(f"DEBUG - Horario para {user_id}: {schedule}")  # Debug

        return jsonify(schedule)

    except Exception as e:
        print(f"Error obteniendo horario: {e}")
        return jsonify({'subjects': {}, 'schedule_grid': {}}), 500


@app.route('/clear_schedule', methods=['POST'])
def clear_schedule():
    """Limpiar horario del usuario"""
    try:
        user_id = session.get('user_id', 'default')
        success = chatbot.clear_schedule(user_id)

        print(f"DEBUG - Horario limpiado para {user_id}: {success}")  # Debug

        return jsonify({'success': success})

    except Exception as e:
        print(f"Error limpiando horario: {e}")
        return jsonify({'success': False}), 500


@app.route('/debug/schedule/<user_id>')
def debug_schedule(user_id):
    """Endpoint de debug para ver horarios"""
    try:
        schedule = chatbot.get_schedule(user_id)
        return jsonify({
            'user_id': user_id,
            'schedule': schedule,
            'all_schedules': chatbot.schedule_manager.user_schedules
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/debug/users')
def debug_users():
    """Endpoint de debug para ver todos los usuarios"""
    try:
        return jsonify({
            'all_users': list(chatbot.schedule_manager.user_schedules.keys()),
            'schedules': chatbot.schedule_manager.user_schedules
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
    print("=== UMSS ChatBot Iniciando ===")
    print(f"Archivo de intents: {intents_file}")
    print(f"Archivo de info UMSS: {umss_info_file}")
    print(f"Modelo ML: {chatbot.get_model_info()}")
    print("==============================")

    app.run(debug=True, host='0.0.0.0', port=5000)
