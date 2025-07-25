#!/usr/bin/env python
import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'azhar_student_management.settings')
django.setup()

from students.models import StudentResult, Course

# التحقق من النتائج
results = StudentResult.objects.all()
print(f"عدد النتائج: {results.count()}")

if results.exists():
    result = results.first()
    print(f"course_scores: {result.course_scores}")
    print(f"المستوى: {result.level}")
    print(f"الطالب: {result.student.full_name}")

    # التحقق من المواد
    courses = Course.objects.filter(level=result.level)
    print(f"عدد المواد في المستوى: {courses.count()}")

    for course in courses:
        score = result.get_course_score(course.id)
        print(f"  {course.name}: {score}")

    # محاكاة الكود في الـ view
    student_data = {
        'result': result,
        'student': result.student,
        'course_scores': [],
        'total_score': 0,
        'max_total_score': 0,
        'percentage': 0,
        'failed_courses': []
    }

    total_score = 0
    max_total_score = 0
    failed_courses = []

    for course in courses:
        score = result.get_course_score(course.id)
        max_score = course.max_score

        if score is not None:
            if score < (max_score * 0.5):
                status = 'راسب'
                css_class = 'score-fail'
                failed_courses.append(course.name)
            elif score < (max_score * 0.65):
                status = 'ضعيف'
                css_class = 'score-weak'
            elif score < (max_score * 0.75):
                status = 'مقبول'
                css_class = 'score-acceptable'
            elif score < (max_score * 0.85):
                status = 'جيد'
                css_class = 'score-good'
            else:
                status = 'ممتاز'
                css_class = 'score-excellent'

            total_score += score
        else:
            score = 'غ'
            status = 'غائب'
            css_class = 'score-absent'
            failed_courses.append(course.name)

        max_total_score += max_score

        student_data['course_scores'].append({
            'course': course,
            'score': score,
            'status': status,
            'class': css_class
        })

    print(f"\nعدد course_scores: {len(student_data['course_scores'])}")
    for cs in student_data['course_scores']:
        print(f"  {cs['course'].name}: {cs['score']} ({cs['status']})")
