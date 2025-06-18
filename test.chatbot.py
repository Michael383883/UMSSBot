#!/usr/bin/env python3
"""
Script de prueba para el Chatbot UMSS - Facultad de Tecnología
Ejecuta todas las preguntas posibles para verificar las respuestas del bot
"""

import requests
import json
import time
from colorama import init, Fore, Back, Style
import sys

# Inicializar colorama para colores en terminal
init(autoreset=True)


class ChatbotTester:
    def __init__(self, base_url="http://localhost:5000"):
        self.base_url = base_url
        self.session = requests.Session()
        self.total_tests = 0
        self.passed_tests = 0
        self.failed_tests = 0

    def print_header(self, text):
        print(f"\n{Fore.CYAN}{'='*60}")
        print(f"{Fore.CYAN}{text:^60}")
        print(f"{Fore.CYAN}{'='*60}")

    def print_test_result(self, question, response, expected_keywords=None):
        self.total_tests += 1
        print(f"\n{Fore.YELLOW}🤖 Pregunta: {question}")
        print(
            f"{Fore.GREEN}📝 Respuesta: {response[:200]}{'...' if len(response) > 200 else ''}")

        if expected_keywords:
            found_keywords = [
                kw for kw in expected_keywords if kw.lower() in response.lower()]
            if found_keywords:
                print(f"{Fore.GREEN}✅ Palabras clave encontradas: {found_keywords}")
                self.passed_tests += 1
            else:
                print(
                    f"{Fore.RED}❌ No se encontraron palabras clave esperadas: {expected_keywords}")
                self.failed_tests += 1
        else:
            if len(response) > 10:  # Respuesta básica válida
                self.passed_tests += 1
                print(f"{Fore.GREEN}✅ Respuesta válida")
            else:
                self.failed_tests += 1
                print(f"{Fore.RED}❌ Respuesta muy corta o inválida")

    def send_message(self, message):
        try:
            response = self.session.post(
                f"{self.base_url}/chat",
                json={"message": message},
                headers={'Content-Type': 'application/json'}
            )
            if response.status_code == 200:
                return response.json().get('response', 'Sin respuesta')
            else:
                return f"Error {response.status_code}: {response.text}"
        except Exception as e:
            return f"Error de conexión: {str(e)}"

    def test_saludos(self):
        self.print_header("PRUEBAS DE SALUDOS")
        preguntas_saludo = [
            "hola",
            "buenos días",
            "hey",
            "qué tal",
            "buenas tardes",
            "como estas"
        ]

        for pregunta in preguntas_saludo:
            respuesta = self.send_message(pregunta)
            self.print_test_result(pregunta, respuesta, [
                                   "asistente", "facultad", "ayudar"])
            time.sleep(0.5)

    def test_recomendaciones_docentes(self):
        self.print_header("PRUEBAS DE RECOMENDACIONES DE DOCENTES")
        preguntas_docentes = [
            "qué docente me recomiendas para álgebra",
            "cuál es el mejor profesor de cálculo",
            "recomiéndame un docente para programación",
            "qué profesor es bueno para física",
            "mejor docente para inglés",
            "quien enseña bien matemáticas"
        ]

        for pregunta in preguntas_docentes:
            respuesta = self.send_message(pregunta)
            self.print_test_result(pregunta, respuesta, [
                                   "profesor", "docente", "recomiendo"])
            time.sleep(0.5)

    def test_materias_especificas(self):
        self.print_header("PRUEBAS DE MATERIAS ESPECÍFICAS")
        preguntas_materias = [
            "álgebra",
            "cálculo 1",
            "física general",
            "programación",
            "inglés",
            "introducción a la programación",
            "matemáticas"
        ]

        for pregunta in preguntas_materias:
            respuesta = self.send_message(pregunta)
            self.print_test_result(pregunta, respuesta, [
                                   "profesor", "horario", "aula"])
            time.sleep(0.5)

    def test_horarios(self):
        self.print_header("PRUEBAS DE HORARIOS")
        preguntas_horarios = [
            "armar horario",
            "crear mi horario",
            "planificar horario",
            "organizar materias",
            "diseñar horario",
            "horario personalizado"
        ]

        for pregunta in preguntas_horarios:
            respuesta = self.send_message(pregunta)
            self.print_test_result(pregunta, respuesta, [
                                   "horario", "materia", "semestre"])
            time.sleep(0.5)

    def test_ubicaciones(self):
        self.print_header("PRUEBAS DE UBICACIONES")
        preguntas_ubicacion = [
            "dónde está el aula 661",
            "ubicación aula 692E",
            "cómo llego al aula 625",
            "donde esta el laboratorio",
            "edificio principal",
            "aula 612"
        ]

        for pregunta in preguntas_ubicacion:
            respuesta = self.send_message(pregunta)
            self.print_test_result(pregunta, respuesta, [
                                   "aula", "edificio", "piso", "ubicación"])
            time.sleep(0.5)

    def test_valorados(self):
        self.print_header("PRUEBAS DE VALORADOS Y MATERIAL")
        preguntas_valorados = [
            "donde comprar valorados",
            "2da instancia",
            "exámenes pasados",
            "fotocopias",
            "material de estudio",
            "ejercicios resueltos"
        ]

        for pregunta in preguntas_valorados:
            respuesta = self.send_message(pregunta)
            self.print_test_result(pregunta, respuesta, [
                                   "fotocopiadora", "centro", "librería"])
            time.sleep(0.5)

    def test_servicios(self):
        self.print_header("PRUEBAS DE SERVICIOS")
        preguntas_servicios = [
            "biblioteca",
            "laboratorios",
            "trámites",
            "inscripción",
            "matrícula",
            "certificados"
        ]

        for pregunta in preguntas_servicios:
            respuesta = self.send_message(pregunta)
            self.print_test_result(pregunta, respuesta, [
                                   "horario", "ubicación", "servicio"])
            time.sleep(0.5)

    def test_informacion_general(self):
        self.print_header("PRUEBAS DE INFORMACIÓN GENERAL")
        preguntas_info = [
            "qué materias hay",
            "ayuda",
            "contacto",
            "teléfono",
            "materias disponibles",
            "plan de estudios"
        ]

        for pregunta in preguntas_info:
            respuesta = self.send_message(pregunta)
            self.print_test_result(pregunta, respuesta, [
                                   "información", "facultad", "disponible"])
            time.sleep(0.5)

    def test_despedidas(self):
        self.print_header("PRUEBAS DE DESPEDIDAS")
        preguntas_despedida = [
            "adiós",
            "hasta luego",
            "gracias",
            "chau",
            "nos vemos",
            "bye"
        ]

        for pregunta in preguntas_despedida:
            respuesta = self.send_message(pregunta)
            self.print_test_result(pregunta, respuesta, [
                                   "luego", "éxito", "estudios"])
            time.sleep(0.5)

    def test_casos_complejos(self):
        self.print_header("PRUEBAS DE CASOS COMPLEJOS")
        preguntas_complejas = [
            "necesito un horario con álgebra y programación para la mañana",
            "qué docente me recomiendas para cálculo que sea paciente",
            "donde puedo encontrar valorados de física y cuánto cuestan",
            "quiero armar un horario sin cruces con las mejores materias",
            "información completa sobre la biblioteca y sus servicios"
        ]

        for pregunta in preguntas_complejas:
            respuesta = self.send_message(pregunta)
            self.print_test_result(pregunta, respuesta)
            time.sleep(0.5)

    def test_casos_no_reconocidos(self):
        self.print_header("PRUEBAS DE CASOS NO RECONOCIDOS")
        preguntas_invalidas = [
            "djfklsjdfklsj",
            "123456789",
            "¿cuál es el sentido de la vida?",
            "háblame del clima",
            "receta de pizza"
        ]

        for pregunta in preguntas_invalidas:
            respuesta = self.send_message(pregunta)
            self.print_test_result(pregunta, respuesta, [
                                   "no entendí", "reformular", "ayuda"])
            time.sleep(0.5)

    def run_all_tests(self):
        print(f"{Fore.MAGENTA}{Style.BRIGHT}")
        print("🤖 INICIANDO PRUEBAS COMPLETAS DEL CHATBOT UMSS")
        print("=" * 60)

        # Verificar conexión
        try:
            response = self.session.get(self.base_url)
            if response.status_code != 200:
                print(
                    f"{Fore.RED}❌ Error: No se puede conectar al servidor en {self.base_url}")
                print(
                    f"{Fore.YELLOW}   Asegúrate de que el servidor Flask esté ejecutándose")
                return False
        except Exception as e:
            print(f"{Fore.RED}❌ Error de conexión: {str(e)}")
            print(f"{Fore.YELLOW}   Ejecuta: python app.py")
            return False

        print(f"{Fore.GREEN}✅ Conexión exitosa al servidor")

        # Ejecutar todas las pruebas
        self.test_saludos()
        self.test_recomendaciones_docentes()
        self.test_materias_especificas()
        self.test_horarios()
        self.test_ubicaciones()
        self.test_valorados()
        self.test_servicios()
        self.test_informacion_general()
        self.test_despedidas()
        self.test_casos_complejos()
        self.test_casos_no_reconocidos()

        # Resumen final
        self.print_header("RESUMEN DE PRUEBAS")
        print(f"{Fore.WHITE}📊 Total de pruebas: {self.total_tests}")
        print(f"{Fore.GREEN}✅ Pruebas exitosas: {self.passed_tests}")
        print(f"{Fore.RED}❌ Pruebas fallidas: {self.failed_tests}")

        success_rate = (self.passed_tests / self.total_tests) * \
            100 if self.total_tests > 0 else 0
        print(f"{Fore.CYAN}📈 Tasa de éxito: {success_rate:.1f}%")

        if success_rate >= 80:
            print(f"{Fore.GREEN}{Style.BRIGHT}🎉 ¡CHATBOT FUNCIONANDO CORRECTAMENTE!")
        elif success_rate >= 60:
            print(f"{Fore.YELLOW}{Style.BRIGHT}⚠️  CHATBOT FUNCIONANDO PARCIALMENTE")
        else:
            print(f"{Fore.RED}{Style.BRIGHT}🚨 CHATBOT NECESITA MEJORAS")

        return True


def main():
    print(f"{Fore.BLUE}{Style.BRIGHT}")
    print("🤖 TESTER DEL CHATBOT UMSS - FACULTAD DE TECNOLOGÍA")
    print("=" * 60)

    # Verificar argumentos
    if len(sys.argv) > 1:
        base_url = sys.argv[1]
    else:
        base_url = "http://localhost:5000"

    print(f"🌐 URL del servidor: {base_url}")
    print(f"⏰ Iniciando en 3 segundos...")
    time.sleep(3)

    # Crear y ejecutar tester
    tester = ChatbotTester(base_url)
    success = tester.run_all_tests()

    if not success:
        sys.exit(1)


if __name__ == "__main__":
    main()
