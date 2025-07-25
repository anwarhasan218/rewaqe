#!/usr/bin/env python
import os
import django

# إعداد Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'azhar_student_management.settings')
django.setup()

from students.models import StudentResult, Student, Level, Batch
from django.utils import timezone
import random

def create_sample_results():
    """إنشاء نتائج تجريبية للطلاب"""

    # الحصول على البيانات الأساسية
    batch = Batch.objects.first()
    levels = Level.objects.all()[:3]  # أول 3 مستويات

    if not batch:
        print("لا توجد دفعات في النظام")
        return

    print(f"إنشاء نتائج تجريبية للدفعة: {batch.name}")

    total_created = 0

    for level in levels:
        students = Student.objects.filter(level=level)[:10]  # أول 10 طلاب لكل مستوى

        print(f"\nالمستوى: {level.name} - عدد الطلاب: {students.count()}")

        for student in students:
            # إنشاء درجات عشوائية واقعية
            course_scores = {}
            total_score = 0

            # الحصول على المواد الفعلية للمستوى
            from students.models import Course
            courses = Course.objects.filter(level=level)

            if courses.exists():
                for course in courses:
                    # درجات عشوائية بناءً على الحد الأقصى للمادة
                    max_score = course.max_score
                    # توزيع الدرجات: 70% ناجح، 20% ضعيف، 10% راسب
                    rand = random.random()
                    if rand < 0.7:  # 70% ناجح
                        score = random.randint(int(max_score * 0.65), max_score)
                    elif rand < 0.9:  # 20% ضعيف
                        score = random.randint(int(max_score * 0.5), int(max_score * 0.64))
                    else:  # 10% راسب
                        score = random.randint(int(max_score * 0.2), int(max_score * 0.49))

                    course_scores[str(course.id)] = score
                    total_score += score
            else:
                # إذا لم توجد مواد، استخدم مواد افتراضية
                for i in range(1, 6):
                    score = random.randint(60, 100)
                    course_scores[str(i)] = score
                    total_score += score

            # تحديد النتيجة بناءً على المجموع
            if total_score >= 400:
                result = 'ناجح ومنقول'
            elif total_score >= 300:
                result = 'ناجح بمواد'
            else:
                result = 'راسب'

            # إنشاء النتيجة
            student_result, created = StudentResult.objects.get_or_create(
                student=student,
                level=level,
                batch=batch,
                defaults={
                    'result': result,
                    'total_score': total_score,
                    'result_date': timezone.now(),
                    'course_scores': course_scores
                }
            )

            if created:
                print(f"  ✓ {student.full_name}: {total_score} - {result}")
                total_created += 1
            else:
                print(f"  - {student.full_name}: موجود مسبقاً")

    print(f"\n🎉 تم إنشاء {total_created} نتيجة جديدة")
    print(f"إجمالي النتائج في النظام: {StudentResult.objects.count()}")

if __name__ == "__main__":
    create_sample_results()
