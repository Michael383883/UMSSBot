from typing import Dict, List, Tuple, Optional
import re


class ScheduleManager:
    def __init__(self):
        self.user_schedules = {}
        self.day_map = {
            'LU': 'Lunes',
            'MA': 'Martes',
            'MI': 'Miércoles',
            'JU': 'Jueves',
            'VI': 'Viernes'
        }

    def create_user_schedule(self, user_id: str) -> None:
        if user_id not in self.user_schedules:
            self.user_schedules[user_id] = {
                'subjects': {},
                'schedule_grid': {}
            }

    def parse_time(self, time_str: str) -> Tuple[str, int, int]:
        match = re.match(r'([A-Z]{2})\s+(\d{3,4})-(\d{3,4})', time_str)
        if match:
            day, start_time, end_time = match.groups()
            start_hour = int(start_time[:2]) if len(
                start_time) == 4 else int(start_time[:1])
            start_min = int(start_time[2:]) if len(
                start_time) == 4 else int(start_time[1:])
            end_hour = int(end_time[:2]) if len(
                end_time) == 4 else int(end_time[:1])
            end_min = int(end_time[2:]) if len(
                end_time) == 4 else int(end_time[1:])

            return day, start_hour * 60 + start_min, end_hour * 60 + end_min
        return None, 0, 0

    def check_time_conflict(self, user_id: str, new_schedule: str) -> List[str]:
        if user_id not in self.user_schedules:
            return []

        day, start_time, end_time = self.parse_time(new_schedule)
        if not day:
            return []

        conflicts = []
        user_schedule = self.user_schedules[user_id]['schedule_grid']

        if day in user_schedule:
            for existing_schedule in user_schedule[day]:
                existing_day, existing_start, existing_end = self.parse_time(
                    existing_schedule['time'])

                if (start_time < existing_end and end_time > existing_start):
                    conflicts.append(
                        f"{existing_schedule['subject']} - {existing_schedule['teacher']} ({existing_schedule['time']})")

        return conflicts

    def add_subject_to_schedule(self, user_id: str, subject: str, teacher: str, schedules: List[str], classroom: str) -> bool:
        self.create_user_schedule(user_id)

        all_conflicts = []
        for schedule in schedules:
            conflicts = self.check_time_conflict(user_id, schedule)
            all_conflicts.extend(conflicts)

        if all_conflicts:
            return False

        self.user_schedules[user_id]['subjects'][subject] = {
            'teacher': teacher,
            'schedules': schedules,
            'classroom': classroom
        }

        for schedule in schedules:
            day, _, _ = self.parse_time(schedule)
            if day:
                if day not in self.user_schedules[user_id]['schedule_grid']:
                    self.user_schedules[user_id]['schedule_grid'][day] = []

                self.user_schedules[user_id]['schedule_grid'][day].append({
                    'subject': subject,
                    'teacher': teacher,
                    'time': schedule,
                    'classroom': classroom
                })

        return True

    def get_user_schedule(self, user_id: str) -> Dict:
        if user_id not in self.user_schedules:
            return {'subjects': {}, 'schedule_grid': {}}
        return self.user_schedules[user_id]

    def remove_subject(self, user_id: str, subject: str) -> bool:
        if user_id not in self.user_schedules or subject not in self.user_schedules[user_id]['subjects']:
            return False

        subject_info = self.user_schedules[user_id]['subjects'][subject]

        for schedule in subject_info['schedules']:
            day, _, _ = self.parse_time(schedule)
            if day and day in self.user_schedules[user_id]['schedule_grid']:
                self.user_schedules[user_id]['schedule_grid'][day] = [
                    item for item in self.user_schedules[user_id]['schedule_grid'][day]
                    if item['subject'] != subject
                ]

                if not self.user_schedules[user_id]['schedule_grid'][day]:
                    del self.user_schedules[user_id]['schedule_grid'][day]

        del self.user_schedules[user_id]['subjects'][subject]
        return True

    def format_schedule_display(self, user_id: str) -> str:
        schedule = self.get_user_schedule(user_id)

        if not schedule['subjects']:
            return "Tu horario está vacío. ¡Empieza agregando materias!"

        result = "🗓️ **TU HORARIO ACTUAL:**\n\n"

        for day_code in ['LU', 'MA', 'MI', 'JU', 'VI']:
            if day_code in schedule['schedule_grid']:
                result += f"**{self.day_map[day_code]}:**\n"

                day_classes = sorted(schedule['schedule_grid'][day_code],
                                     key=lambda x: self.parse_time(x['time'])[1])

                for class_info in day_classes:
                    time_display = class_info['time'].replace(
                        day_code + ' ', '')
                    result += f"  • {class_info['subject']} - {time_display}\n"
                    result += f"    👨‍🏫 {class_info['teacher']}\n"
                    result += f"    📍 Aula {class_info['classroom']}\n\n"

        result += f"📚 **Total de materias:** {len(schedule['subjects'])}\n"
        return result

    def get_alternative_schedules(self, user_id: str, teacher_options: List[Dict]) -> List[Dict]:
        alternatives = []

        for option in teacher_options:
            conflicts = []
            for i, schedule in enumerate(option['horarios']):
                schedule_conflicts = self.check_time_conflict(
                    user_id, schedule)
                if schedule_conflicts:
                    conflicts.extend([(i, conflict)
                                     for conflict in schedule_conflicts])

            alternatives.append({
                'teacher': option,
                'conflicts': conflicts,
                'has_conflicts': len(conflicts) > 0
            })

        alternatives.sort(key=lambda x: len(x['conflicts']))
        return alternatives
