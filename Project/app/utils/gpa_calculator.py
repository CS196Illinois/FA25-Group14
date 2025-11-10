import csv
from pathlib import Path
from functools import lru_cache
from typing import Dict, List, Optional

GRADE_VALUES = {
    'A+': 4.0,
    'A': 4.0,
    'A-': 3.67,
    'B+': 3.33,
    'B': 3.0,
    'B-': 2.67,
    'C+': 2.33,
    'C': 2.0,
    'C-': 1.67,
    'D+': 1.33,
    'D': 1.0,
    'D-': 0.67,
    'F': 0.0
}

GPA_DATA_PATH = Path(__file__).resolve().parent.parent / 'gpa_data.csv'


@lru_cache(maxsize=1)
def load_gpa_data() -> List[Dict]:
    """Load GPA from CSV file"""
    gpa_records = []

    if not GPA_DATA_PATH.exists():
        return gpa_records

    with GPA_DATA_PATH.open('r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            gpa_records.append(row)

    return gpa_records


def calculate_section_gpa(row: Dict) -> Optional[float]:
    """Calculate GPA per section"""
    try:
        total_points = 0.0
        total_students = 0

        for grade, value in GRADE_VALUES.items():
            count = int(row.get(grade, 0) or 0)
            total_points += count * value
            total_students += count

        if total_students == 0:
            return None

        return round(total_points / total_students, 2)
    except (ValueError, TypeError):
        return None


def format_semester(year_term: str) -> str:
    """Convert '2025-sp' to 'Spring 2025' and the rest as well"""
    if not year_term or '-' not in year_term:
        return year_term

    year, term = year_term.split('-')
    term_map = {
        'sp': 'Spring',
        'fa': 'Fall',
        'su': 'Summer',
        'wi': 'Winter'
    }
    term_name = term_map.get(term.lower(), term)
    return f"{term_name} {year}"


def get_course_gpa_stats(course_code: str) -> Optional[Dict]:
    """
    Get comprehensive GPA statistics for a course

    Returns dict with:
        - overall_gpa: average GPA across all time
        - recent_gpa: average GPA from last 3 semesters
        - total_students: total number of students
        - top_professors: list of top 5 professors by GPA
        - recent_semesters: list of last 3 semester averages
    """
    gpa_data = load_gpa_data()

    if not gpa_data:
        return None

    # parse course code (EX 123 -> subject="EX", number="123")
    parts = course_code.strip().split()
    if len(parts) != 2:
        return None

    subject, number = parts[0], parts[1]

    course_sections = [
        row for row in gpa_data
        if row.get('Subject') == subject and row.get('Number') == number
    ]

    if not course_sections:
        return None

    # overall statistics
    total_weighted_gpa = 0.0
    total_students = 0
    professor_stats = {}  
    semester_gpas = {}  

    for row in course_sections:
        section_gpa = calculate_section_gpa(row)
        if section_gpa is None:
            continue

        students = int(row.get('Students', 0) or 0)
        if students == 0:
            continue

        total_weighted_gpa += section_gpa * students
        total_students += students

        # professor tracker
        professor = row.get('Primary Instructor', '').strip()
        if professor:
            if professor not in professor_stats:
                professor_stats[professor] = {'total_gpa': 0, 'total_students': 0}
            professor_stats[professor]['total_gpa'] += section_gpa * students
            professor_stats[professor]['total_students'] += students

        # semester tracker
        year_term = row.get('YearTerm', '')
        if year_term:
            if year_term not in semester_gpas:
                semester_gpas[year_term] = {'total_gpa': 0, 'total_students': 0}
            semester_gpas[year_term]['total_gpa'] += section_gpa * students
            semester_gpas[year_term]['total_students'] += students

    if total_students == 0:
        return None

    # overall average GPA
    overall_gpa = round(total_weighted_gpa / total_students, 2)

    # average gpa from past 3 semester
    recent_semesters_list = sorted(semester_gpas.keys(), reverse=True)[:3]
    recent_gpa = None
    if recent_semesters_list:
        recent_total_gpa = 0
        recent_total_students = 0
        for sem in recent_semesters_list:
            recent_total_gpa += semester_gpas[sem]['total_gpa']
            recent_total_students += semester_gpas[sem]['total_students']
        if recent_total_students > 0:
            recent_gpa = round(recent_total_gpa / recent_total_students, 2)

    # top 5 professors by GPA
    top_professors = []
    for prof, stats in professor_stats.items():
        if stats['total_students'] >= 30:  # must have at least 30 students
            avg_gpa = round(stats['total_gpa'] / stats['total_students'], 2)
            top_professors.append({
                'name': prof,
                'gpa': avg_gpa,
                'students': stats['total_students']
            })
    top_professors.sort(key=lambda x: x['gpa'], reverse=True)
    top_professors = top_professors[:5]

    # recent semester averages, last 3 semesters
    recent_semester_trends = []
    for year_term in sorted(semester_gpas.keys(), reverse=True)[:3]:
        sem_data = semester_gpas[year_term]
        sem_gpa = round(sem_data['total_gpa'] / sem_data['total_students'], 2)
        recent_semester_trends.append({
            'semester': format_semester(year_term),
            'gpa': sem_gpa,
            'students': sem_data['total_students']
        })

    return {
        'overall_gpa': overall_gpa,
        'recent_gpa': recent_gpa,
        'total_students': total_students,
        'top_professors': top_professors,
        'recent_semesters': recent_semester_trends
    }
