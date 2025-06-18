import spacy
import re
from typing import List, Dict


class NLPProcessor:
    def __init__(self):
        try:
            # Carga el modelo de idioma español de spaCy
            self.nlp = spacy.load("es_core_news_sm")
        except:
            # Si no se puede cargar, desactiva el modelo y muestra advertencia
            self.nlp = None
            print("Modelo de español no encontrado. Instalando...")

    # Preprocesamiento del texto: lo limpia y estandariza
    def preprocess_text(self, text: str) -> str:
        text = text.lower()  # Convierte a minúsculas
        text = re.sub(r'[^\w\s]', '', text)  # Elimina signos de puntuación
        # Reemplaza múltiples espacios por uno solo
        text = re.sub(r'\s+', ' ', text)
        return text.strip()  # Elimina espacios iniciales y finales

    # Tokeniza el texto y devuelve una lista de lemas, excluyendo palabras vacías y signos
    def tokenize(self, text: str) -> List[str]:
        if self.nlp:
            doc = self.nlp(text)
            return [token.lemma_ for token in doc if not token.is_stop and not token.is_punct]
        else:
            return text.split()  # Si no hay modelo, solo separa por espacios

    # Extrae entidades específicas del texto como materias, aulas, acciones, etc.
    def extract_entities(self, text: str) -> Dict[str, List[str]]:
        entities = {
            'materias': [],     # Lista de materias encontradas
            # Lista de aulas encontradas (por patrón de 3 dígitos)
            'aulas': [],
            'docentes': [],     # Reservado, pero no implementado aún
            'acciones': [],     # Acciones clave como "agregar", "ver", etc.
            # Números en el texto (útiles para aulas o cantidad)
            'numeros': []
        }

        # Palabras clave predefinidas para materias
        materias_keywords = ['algebra', 'calculo',
                             'ingles', 'fisica', 'programacion']
        # Detecta códigos de aula tipo 305, 101B, etc.
        aulas_keywords = re.findall(r'\b\d{3}[A-Z]?\b', text.upper())
        # Acciones reconocibles en texto
        acciones_keywords = ['armar', 'crear', 'ver',
                             'mostrar', 'quitar', 'eliminar', 'agregar', 'añadir']
        # Encuentra todos los números en el texto
        numeros = re.findall(r'\b\d+\b', text)

        # Verifica si cada palabra clave de materia está en el texto
        for materia in materias_keywords:
            if materia in text.lower():
                entities['materias'].append(materia)

        # Verifica si cada palabra clave de acción está en el texto
        for accion in acciones_keywords:
            if accion in text.lower():
                entities['acciones'].append(accion)

        # Guarda las aulas detectadas
        entities['aulas'] = aulas_keywords
        # Convierte los números detectados en enteros
        entities['numeros'] = [int(n) for n in numeros]

        return entities  # Retorna todas las entidades detectadas

    # Calcula la similitud entre dos textos basada en tokens compartidos
    def calculate_similarity(self, text1: str, text2: str) -> float:
        tokens1 = set(self.tokenize(text1))  # Tokeniza y convierte a conjunto
        tokens2 = set(self.tokenize(text2))

        if not tokens1 or not tokens2:
            return 0.0  # Si alguno está vacío, no hay similitud

        intersection = tokens1.intersection(tokens2)  # Palabras comunes
        union = tokens1.union(tokens2)  # Palabras totales sin repetir

        # Índice de similitud tipo Jaccard
        return len(intersection) / len(union)

    # Extrae la materia detectada desde un texto, si existe alguna palabra clave
    def extract_subject_from_text(self, text: str) -> str:
        subject_map = {
            'fisica': 'fisica',
            'algebra': 'algebra',
            'calculo': 'calculo',
            'ingles': 'ingles',
            'programacion': 'programacion',
            'matematicas': 'algebra'  # Sinónimo
        }

        text_lower = text.lower()  # Trabaja en minúsculas
        for keyword, subject in subject_map.items():
            if keyword in text_lower:
                return subject  # Devuelve la materia normalizada

        return None  # Si no encuentra, retorna None
