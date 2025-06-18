import json
from typing import Dict, List, Any


class KnowledgeBase:
    def __init__(self, umss_info_file: str):
        with open(umss_info_file, 'r', encoding='utf-8') as f:
            self.data = json.load(f)

    def get_docente_info(self, materia: str) -> List[Dict[str, Any]]:
        return self.data.get('docentes', {}).get(materia, [])

    def get_valorados_info(self) -> List[Dict[str, str]]:
        return self.data.get('valorados', [])

    def get_aula_info(self, aula: str) -> Dict[str, Any]:
        aulas = self.data.get('aulas', {})

        for edificio, pisos in aulas.items():
            if isinstance(pisos, dict):
                for piso, aulas_list in pisos.items():
                    if aula in aulas_list:
                        return {
                            'aula': aula,
                            'edificio': edificio,
                            'piso': piso,
                            'ubicacion': f"{edificio} - {piso}"
                        }

        return {'aula': aula, 'ubicacion': 'No encontrada'}

    def search_docente_by_name(self, nombre: str) -> List[Dict[str, Any]]:
        results = []
        for materia, docentes in self.data.get('docentes', {}).items():
            for docente in docentes:
                if nombre.lower() in docente['nombre'].lower():
                    result = docente.copy()
                    result['materia'] = materia
                    results.append(result)
        return results

    def get_horarios_atencion(self) -> Dict[str, str]:
        return self.data.get('horarios_atencion', {})
