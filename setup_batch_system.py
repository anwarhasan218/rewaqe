#!/usr/bin/env python
"""
Script لإعداد نظام الدفعات وإنشاء البيانات الأساسية
"""
import os
import sys
import django

# إعداد Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'azhar_student_management.settings')
django.setup()

from django.contrib.auth.models import User
from students.models import *

def main():
    print("🚀 بدء إعداد نظام الدفعات...")
    
    # 1. إنشاء superuser
    if not User.objects.filter(username='admin').exists():
        User.objects.create_superuser('admin', 'admin@example.com', 'admin123')
        print("✅ تم إنشاء superuser: admin/admin123")
    else:
        print("ℹ️  superuser موجود مسبقاً")
    
    # 2. إنشاء دفعة أغسطس 2025
    batch, created = Batch.objects.get_or_create(
        name='أغسطس 2025',
        defaults={
            'is_active': True
        }
    )
    if created:
        print("✅ تم إنشاء دفعة: أغسطس 2025")
    else:
        print("ℹ️  دفعة أغسطس 2025 موجودة مسبقاً")
    
    # 3. إنشاء المراحل الدراسية
    stages_data = [
        'تمهيدية',
        'متوسطة', 
        'تخصصية فقه واصوله',
        'تخصصية تفسير وحديث',
        'تخصصية لغة عربية',
        'تخصصية عقيدة',
        'شعبة عامة متقدمة'
    ]
    
    for stage_name in stages_data:
        stage, created = Stage.objects.get_or_create(name=stage_name)
        if created:
            print(f"✅ تم إنشاء مرحلة: {stage_name}")
    
    # 4. إنشاء المستويات
    levels_data = [
        ('تمهيدية', ['المستوى الأول', 'المستوى الثاني']),
        ('متوسطة', ['المستوى الأول', 'المستوى الثاني']),
        ('تخصصية فقه واصوله', ['المستوى الأول', 'المستوى الثاني', 'المستوى الثالث', 'المستوى الرابع']),
        ('تخصصية تفسير وحديث', ['المستوى الأول', 'المستوى الثاني', 'المستوى الثالث', 'المستوى الرابع']),
        ('تخصصية لغة عربية', ['المستوى الأول', 'المستوى الثاني', 'المستوى الثالث', 'المستوى الرابع']),
        ('تخصصية عقيدة', ['المستوى الأول', 'المستوى الثاني', 'المستوى الثالث', 'المستوى الرابع']),
        ('شعبة عامة متقدمة', ['المستوى الأول', 'المستوى الثاني', 'المستوى الثالث', 'المستوى الرابع'])
    ]
    
    for stage_name, level_names in levels_data:
        try:
            stage = Stage.objects.get(name=stage_name)
            for level_name in level_names:
                level, created = Level.objects.get_or_create(
                    stage=stage,
                    name=level_name
                )
                if created:
                    print(f"✅ تم إنشاء مستوى: {stage_name} - {level_name}")
        except Stage.DoesNotExist:
            print(f"❌ المرحلة غير موجودة: {stage_name}")
    
    # 5. تحديث الطلاب الموجودين لربطهم بالدفعة
    students_updated = Student.objects.filter(batch__isnull=True).update(batch=batch)
    if students_updated > 0:
        print(f"✅ تم ربط {students_updated} طالب بدفعة أغسطس 2025")
    
    # 6. إحصائيات نهائية
    print("\n📊 الإحصائيات النهائية:")
    print(f"   الدفعات: {Batch.objects.count()}")
    print(f"   المراحل: {Stage.objects.count()}")
    print(f"   المستويات: {Level.objects.count()}")
    print(f"   الطلاب: {Student.objects.count()}")
    print(f"   المواد: {Course.objects.count()}")
    
    print("\n🎉 تم إعداد نظام الدفعات بنجاح!")
    print("🌐 يمكنك الآن الوصول للنظام على: http://192.168.1.4:8000")
    print("👤 بيانات الدخول: admin / admin123")

if __name__ == '__main__':
    main()
