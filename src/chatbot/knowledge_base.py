# Importación de librerías necesarias
import json                             # Para leer y trabajar con archivos JSON
# Para indicar tipos más claros y estructurados
from typing import Dict, List, Any

# Clase que representa una base de conocimiento con datos de la UMSS (docentes, aulas, valorados, etc.)


class KnowledgeBase:
    def __init__(self, umss_info_file: str):
        # Abre y carga el archivo JSON que contiene la información
        with open(umss_info_file, 'r', encoding='utf-8') as f:
            # Guarda los datos en memoria como diccionario
            self.data = json.load(f)

    # Devuelve una lista de información de docentes para una materia específica
    def get_docente_info(self, materia: str) -> List[Dict[str, Any]]:
        # Si no encuentra, retorna lista vacía
        return self.data.get('docentes', {}).get(materia, [])

    # Devuelve una lista con la información de valorados (segunda instancia, fotocopias, etc.)
    def get_valorados_info(self) -> List[Dict[str, str]]:
        # Si no hay datos, devuelve lista vacía
        return self.data.get('valorados', [])

    # Busca una aula específica y devuelve su ubicación exacta (edificio y piso)
    def get_aula_info(self, aula: str) -> Dict[str, Any]:
        # Extrae toda la estructura de aulas
        aulas = self.data.get('aulas', {})

        # Recorre edificios y pisos para encontrar el aula
        for edificio, pisos in aulas.items():
            # Asegura que los pisos estén bien definidos como diccionario
            if isinstance(pisos, dict):
                for piso, aulas_list in pisos.items():
                    if aula in aulas_list:
                        return {
                            'aula': aula,
                            'edificio': edificio,
                            'piso': piso,
                            'ubicacion': f"{edificio} - {piso}"
                        }

        # Si no se encuentra, retorna mensaje por defecto
        return {'aula': aula, 'ubicacion': 'No encontrada'}

    # Busca docentes por nombre (coincidencias parciales, no exactas)
    def search_docente_by_name(self, nombre: str) -> List[Dict[str, Any]]:
        results = []
        # Recorre todas las materias y sus docentes
        for materia, docentes in self.data.get('docentes', {}).items():
            for docente in docentes:
                # Comparación sin importar mayúsculas
                if nombre.lower() in docente['nombre'].lower():
                    result = docente.copy()       # Copia los datos del docente
                    # Agrega la materia correspondiente
                    result['materia'] = materia
                    results.append(result)
        return results  # Devuelve lista de coincidencias

    # Retorna los horarios de atención administrativa o general
    def get_horarios_atencion(self) -> Dict[str, str]:
        # Devuelve diccionario o vacío si no existe
        return self.data.get('horarios_atencion', {})
