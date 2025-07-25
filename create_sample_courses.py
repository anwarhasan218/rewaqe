#!/usr/bin/env python
"""
إنشاء مواد تجريبية لاختبار النظام
"""
import os
import sys
import django

# إعداد Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'azhar_student_management.settings')
django.setup()

from students.models import Stage, Level, Course

def create_sample_courses():
    """إنشاء مواد تجريبية لكل مستوى"""
    
    print("🔄 بدء إنشاء المواد التجريبية...")
    
    # مواد المرحلة التمهيدية
    tamheediya_courses = [
        'القرآن الكريم',
        'التجويد',
        'العقيدة الإسلامية',
        'الفقه الإسلامي',
        'السيرة النبوية',
        'اللغة العربية',
        'الخط العربي'
    ]
    
    # مواد المرحلة المتوسطة
    mutawassita_courses = [
        'القرآن الكريم وعلومه',
        'التفسير',
        'الحديث الشريف',
        'الفقه وأصوله',
        'العقيدة والأخلاق',
        'النحو والصرف',
        'البلاغة والأدب',
        'التاريخ الإسلامي'
    ]
    
    # مواد التخصصات
    fiqh_courses = [
        'الفقه المقارن',
        'أصول الفقه',
        'القواعد الفقهية',
        'فقه النوازل',
        'المعاملات المالية',
        'فقه الأسرة',
        'الفقه السياسي'
    ]
    
    tafseer_courses = [
        'التفسير التحليلي',
        'علوم القرآن',
        'الحديث وعلومه',
        'مصطلح الحديث',
        'شروح الأحاديث',
        'الجرح والتعديل',
        'السنة النبوية'
    ]
    
    arabic_courses = [
        'النحو المتقدم',
        'الصرف المتقدم',
        'البلاغة العربية',
        'الأدب العربي',
        'فقه اللغة',
        'العروض والقوافي',
        'النقد الأدبي'
    ]
    
    aqeedah_courses = [
        'العقيدة الإسلامية',
        'علم الكلام',
        'الفرق والمذاهب',
        'الفلسفة الإسلامية',
        'مقارنة الأديان',
        'الرد على الشبهات',
        'التصوف الإسلامي'
    ]
    
    # مواد الشعبة العامة المتقدمة
    general_courses = [
        'الثقافة الإسلامية',
        'الدعوة والإرشاد',
        'الإدارة الإسلامية',
        'الاقتصاد الإسلامي',
        'القانون الإسلامي',
        'التربية الإسلامية',
        'الإعلام الإسلامي'
    ]
    
    # ربط المواد بالمراحل
    stage_courses_map = {
        'تمهيدية': tamheediya_courses,
        'متوسطة': mutawassita_courses,
        'تخصصية فقه واصوله': fiqh_courses,
        'تخصصية تفسير وحديث': tafseer_courses,
        'تخصصية لغة عربية': arabic_courses,
        'تخصصية عقيدة': aqeedah_courses,
        'شعبة عامة متقدمة': general_courses,
    }
    
    created_count = 0
    
    for stage in Stage.objects.all():
        stage_name = stage.name
        courses_list = stage_courses_map.get(stage_name, [])
        
        print(f"\n📚 إنشاء مواد للمرحلة: {stage_name}")
        
        for level in stage.level_set.all():
            print(f"  📖 المستوى: {level.name}")
            
            # إنشاء مواد لهذا المستوى
            for i, course_name in enumerate(courses_list):
                # توزيع المواد على المستويات
                if stage_name in ['تمهيدية', 'متوسطة']:
                    # للمراحل التمهيدية والمتوسطة، نضع نصف المواد في كل مستوى
                    if level.name == 'المستوى الأول' and i < len(courses_list) // 2:
                        pass  # إنشاء المادة
                    elif level.name == 'المستوى الثاني' and i >= len(courses_list) // 2:
                        pass  # إنشاء المادة
                    else:
                        continue
                else:
                    # للمراحل التخصصية، نوزع المواد على الأربع مستويات
                    courses_per_level = len(courses_list) // 4
                    level_index = ['المستوى الأول', 'المستوى الثاني', 'المستوى الثالث', 'المستوى الرابع'].index(level.name)
                    start_index = level_index * courses_per_level
                    end_index = start_index + courses_per_level
                    
                    if level_index == 3:  # المستوى الرابع يأخذ المواد المتبقية
                        end_index = len(courses_list)
                    
                    if not (start_index <= i < end_index):
                        continue
                
                # إنشاء المادة
                course, created = Course.objects.get_or_create(
                    name=course_name,
                    level=level,
                    defaults={
                        'max_score': 100,
                        'pass_score': 50
                    }
                )
                
                if created:
                    created_count += 1
                    print(f"    ✅ تم إنشاء المادة: {course_name}")
                else:
                    print(f"    📋 المادة موجودة: {course_name}")
    
    print(f"\n🎉 تم الانتهاء من إنشاء {created_count} مادة جديدة!")
    
    # عرض ملخص
    print("\n📊 ملخص المواد:")
    for stage in Stage.objects.all():
        for level in stage.level_set.all():
            courses_count = level.courses.count()
            print(f"  {stage.name} - {level.name}: {courses_count} مادة")

if __name__ == '__main__':
    create_sample_courses()
