import spacy
import re
from typing import List, Dict


class NLPProcessor:
    def __init__(self):
        try:
            self.nlp = spacy.load("es_core_news_sm")
        except:
            self.nlp = None
            print("Modelo de español no encontrado. Instalando...")

    def preprocess_text(self, text: str) -> str:
        text = text.lower()
        text = re.sub(r'[^\w\s]', '', text)
        text = re.sub(r'\s+', ' ', text)
        return text.strip()

    def tokenize(self, text: str) -> List[str]:
        if self.nlp:
            doc = self.nlp(text)
            return [token.lemma_ for token in doc if not token.is_stop and not token.is_punct]
        else:
            return text.split()

    def extract_entities(self, text: str) -> Dict[str, List[str]]:
        entities = {
            'materias': [],
            'aulas': [],
            'docentes': [],
            'acciones': [],
            'numeros': []
        }

        materias_keywords = ['algebra', 'calculo',
                             'ingles', 'fisica', 'programacion']
        aulas_keywords = re.findall(r'\b\d{3}[A-Z]?\b', text.upper())
        acciones_keywords = ['armar', 'crear', 'ver',
                             'mostrar', 'quitar', 'eliminar', 'agregar', 'añadir']
        numeros = re.findall(r'\b\d+\b', text)

        for materia in materias_keywords:
            if materia in text.lower():
                entities['materias'].append(materia)

        for accion in acciones_keywords:
            if accion in text.lower():
                entities['acciones'].append(accion)

        entities['aulas'] = aulas_keywords
        entities['numeros'] = [int(n) for n in numeros]

        return entities

    def calculate_similarity(self, text1: str, text2: str) -> float:
        tokens1 = set(self.tokenize(text1))
        tokens2 = set(self.tokenize(text2))

        if not tokens1 or not tokens2:
            return 0.0

        intersection = tokens1.intersection(tokens2)
        union = tokens1.union(tokens2)

        return len(intersection) / len(union)

    def extract_subject_from_text(self, text: str) -> str:
        subject_map = {
            'fisica': 'fisica',
            'algebra': 'algebra',
            'calculo': 'calculo',
            'ingles': 'ingles',
            'programacion': 'programacion',
            'matematicas': 'algebra'
        }

        text_lower = text.lower()
        for keyword, subject in subject_map.items():
            if keyword in text_lower:
                return subject

        return None
