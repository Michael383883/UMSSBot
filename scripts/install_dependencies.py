
import subprocess
import sys
import os


def install_requirements():
    try:
        subprocess.check_call(
            [sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("✅ Dependencias instaladas correctamente")
    except subprocess.CalledProcessError:
        print("❌ Error al instalar dependencias")
        return False
    return True


def download_spacy_model():
    try:
        subprocess.check_call(
            [sys.executable, "-m", "spacy", "download", "es_core_news_sm"])
        print("✅ Modelo de español de spaCy descargado")
    except subprocess.CalledProcessError:
        print("⚠️ No se pudo descargar el modelo de español de spaCy")
        print("💡 El chatbot funcionará con funcionalidad limitada")
        return False
    return True


def create_directories():
    directories = [
        "src/data",
        "templates",
        "scripts"
    ]

    for directory in directories:
        os.makedirs(directory, exist_ok=True)
        print(f"📁 Directorio creado: {directory}")


def main():
    print("🚀 Instalando UMSS ChatBot...")
    print("=" * 50)

    create_directories()

    if install_requirements():
        download_spacy_model()

    print("=" * 50)
    print("✅ Instalación completada!")
    print("🎯 Para ejecutar el chatbot:")
    print("   python app.py")


if __name__ == "__main__":
    main()
