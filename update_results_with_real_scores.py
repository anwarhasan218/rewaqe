#!/usr/bin/env python
import os
import django

# إعداد Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'azhar_student_management.settings')
django.setup()

from students.models import StudentResult, Course
import random

def update_results_with_real_scores():
    """تحديث النتائج الموجودة بدرجات واقعية"""
    
    results = StudentResult.objects.all()
    print(f"تحديث {results.count()} نتيجة بدرجات واقعية...")
    
    updated_count = 0
    
    for result in results:
        level = result.level
        courses = Course.objects.filter(level=level)
        
        if not courses.exists():
            print(f"لا توجد مواد للمستوى {level.name}")
            continue
        
        course_scores = {}
        total_score = 0
        max_total_score = 0
        failed_courses = []
        
        for course in courses:
            max_score = course.max_score
            max_total_score += max_score
            
            # توزيع الدرجات: 70% ناجح، 20% ضعيف، 10% راسب
            rand = random.random()
            if rand < 0.7:  # 70% ناجح
                score = random.randint(int(max_score * 0.65), max_score)
            elif rand < 0.9:  # 20% ضعيف
                score = random.randint(int(max_score * 0.5), int(max_score * 0.64))
            else:  # 10% راسب
                score = random.randint(int(max_score * 0.2), int(max_score * 0.49))
                failed_courses.append(course)
            
            course_scores[str(course.id)] = score
            total_score += score
        
        # تحديد النتيجة النهائية
        if not failed_courses:
            if total_score >= (max_total_score * 0.85):
                final_result = 'ناجح ومنقول'
            else:
                final_result = 'ناجح ومنقول'
        elif len(failed_courses) <= 2:
            final_result = 'ناجح بمواد'
        else:
            final_result = 'راسب'
        
        # تحديث النتيجة
        result.course_scores = course_scores
        result.total_score = total_score
        result.result = final_result
        
        # تحديث المواد المتعثر فيها
        result.failed_courses.clear()
        for course in failed_courses:
            result.failed_courses.add(course)
        
        result.save()
        updated_count += 1
        
        print(f"  ✓ {result.student.full_name}: {total_score}/{max_total_score} - {final_result}")
        if failed_courses:
            failed_names = [c.name for c in failed_courses]
            print(f"    مواد الرسوب: {', '.join(failed_names)}")
    
    print(f"\n🎉 تم تحديث {updated_count} نتيجة بنجاح!")

if __name__ == "__main__":
    update_results_with_real_scores()
