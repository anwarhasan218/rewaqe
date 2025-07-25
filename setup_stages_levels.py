#!/usr/bin/env python
"""
إعداد المراحل والمستويات الأساسية لنظام رواق العلوم الشرعية والعربية
"""
import os
import sys
import django

# إعداد Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'azhar_student_management.settings')
django.setup()

from students.models import Stage, Level

def setup_stages_and_levels():
    """إنشاء المراحل والمستويات الأساسية"""
    
    # تعريف المراحل والمستويات المطلوبة
    stages_levels = {
        'تمهيدية': ['المستوى الأول', 'المستوى الثاني'],
        'متوسطة': ['المستوى الأول', 'المستوى الثاني'],
        'تخصصية فقه واصوله': ['المستوى الأول', 'المستوى الثاني', 'المستوى الثالث', 'المستوى الرابع'],
        'تخصصية تفسير وحديث': ['المستوى الأول', 'المستوى الثاني', 'المستوى الثالث', 'المستوى الرابع'],
        'تخصصية لغة عربية': ['المستوى الأول', 'المستوى الثاني', 'المستوى الثالث', 'المستوى الرابع'],
        'تخصصية عقيدة': ['المستوى الأول', 'المستوى الثاني', 'المستوى الثالث', 'المستوى الرابع'],
        'شعبة عامة متقدمة': ['المستوى الأول', 'المستوى الثاني', 'المستوى الثالث', 'المستوى الرابع'],
    }
    
    print("بدء إعداد المراحل والمستويات...")
    
    for stage_name, levels in stages_levels.items():
        # إنشاء أو الحصول على المرحلة
        stage, created = Stage.objects.get_or_create(name=stage_name)
        if created:
            print(f"✅ تم إنشاء المرحلة: {stage_name}")
        else:
            print(f"📋 المرحلة موجودة بالفعل: {stage_name}")
        
        # إنشاء المستويات لهذه المرحلة
        for level_name in levels:
            level, created = Level.objects.get_or_create(
                stage=stage,
                name=level_name
            )
            if created:
                print(f"  ✅ تم إنشاء المستوى: {level_name}")
            else:
                print(f"  📋 المستوى موجود بالفعل: {level_name}")
    
    print("\n🎉 تم الانتهاء من إعداد جميع المراحل والمستويات!")
    
    # عرض ملخص
    print("\n📊 ملخص النظام:")
    for stage in Stage.objects.all():
        levels_count = stage.level_set.count()
        print(f"  {stage.name}: {levels_count} مستوى")

if __name__ == '__main__':
    setup_stages_and_levels()
