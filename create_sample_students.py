#!/usr/bin/env python
"""
إنشاء طلاب تجريبيين لاختبار النظام
"""
import os
import sys
import django

# إعداد Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'azhar_student_management.settings')
django.setup()

from students.models import Stage, Level, Student

def create_sample_students():
    """إنشاء طلاب تجريبيين"""
    
    print("🔄 بدء إنشاء الطلاب التجريبيين...")
    
    # أسماء تجريبية
    student_names = [
        'أحمد محمد علي',
        'محمود أحمد حسن',
        'فاطمة محمد سعيد',
        'عائشة أحمد محمود',
        'عبد الله محمد أحمد',
        'خديجة علي حسن',
        'يوسف أحمد علي',
        'زينب محمد حسن',
        'عمر علي محمود',
        'مريم أحمد سعيد'
    ]
    
    created_count = 0
    
    # إنشاء طلاب لكل مستوى
    for stage in Stage.objects.all():
        print(f"\n👥 إنشاء طلاب للمرحلة: {stage.name}")
        
        for level in stage.level_set.all():
            print(f"  📚 المستوى: {level.name}")
            
            # إنشاء 5 طلاب لكل مستوى
            for i in range(5):
                student_name = student_names[i % len(student_names)]
                
                # تعديل الاسم ليكون فريد
                if i > 0:
                    student_name = f"{student_name} ({i+1})"
                
                # إنشاء كود فريد
                stage_code = stage.name[:2]
                level_code = level.name[-2:]
                student_code = f"{stage_code}{level_code}{i+1:03d}"
                
                # إنشاء رقم جلوس
                seat_number = f"{i+1:03d}"
                
                # إنشاء رقم قومي تجريبي
                national_id = f"1234567890{i:02d}{created_count:02d}"
                
                # تحديد النوع
                gender = 'ذكر' if i % 2 == 0 else 'أنثى'
                
                # إنشاء الطالب
                student, created = Student.objects.get_or_create(
                    code=student_code,
                    defaults={
                        'full_name': student_name,
                        'current_seat_number': seat_number,
                        'national_id': national_id,
                        'gender': gender,
                        'phone_number': f"0100000{i:04d}",
                        'governorate': 'القاهرة',
                        'vision_status': 'مبصر',
                        'special_needs': False,
                        'level': level,
                        'madhhab': 'شافعي',
                        'study_type': 'مباشر',
                        'enrollment_status': 'مستجد'
                    }
                )
                
                if created:
                    created_count += 1
                    print(f"    ✅ تم إنشاء الطالب: {student_name} (كود: {student_code})")
                else:
                    print(f"    📋 الطالب موجود: {student_name}")
    
    print(f"\n🎉 تم الانتهاء من إنشاء {created_count} طالب جديد!")
    
    # عرض ملخص
    print("\n📊 ملخص الطلاب:")
    for stage in Stage.objects.all():
        for level in stage.level_set.all():
            students_count = level.student_set.count()
            print(f"  {stage.name} - {level.name}: {students_count} طالب")

if __name__ == '__main__':
    create_sample_students()
