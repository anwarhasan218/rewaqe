#!/usr/bin/env python
"""
إعادة تعيين المراحل والمستويات لنظام رواق العلوم الشرعية والعربية
"""
import os
import sys
import django

# إعداد Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'azhar_student_management.settings')
django.setup()

from students.models import Stage, Level, Student

def reset_stages_and_levels():
    """حذف وإعادة إنشاء المراحل والمستويات"""
    
    print("🔄 بدء إعادة تعيين المراحل والمستويات...")
    
    # التحقق من وجود طلاب مرتبطين
    students_count = Student.objects.count()
    if students_count > 0:
        print(f"⚠️  تحذير: يوجد {students_count} طالب في النظام")
        print("سيتم الاحتفاظ بالطلاب وتحديث مراجعهم للمستويات الجديدة")
    
    # حذف المراحل والمستويات القديمة (سيتم حذف المستويات تلقائياً)
    print("🗑️  حذف المراحل والمستويات القديمة...")
    
    # حفظ بيانات الطلاب المرتبطة بالمستويات القديمة
    student_level_mapping = {}
    for student in Student.objects.all():
        student_level_mapping[student.id] = {
            'stage_name': student.level.stage.name,
            'level_name': student.level.name
        }
    
    # حذف المراحل القديمة
    Stage.objects.all().delete()
    
    # تعريف المراحل والمستويات الجديدة
    stages_levels = {
        'تمهيدية': ['المستوى الأول', 'المستوى الثاني'],
        'متوسطة': ['المستوى الأول', 'المستوى الثاني'],
        'تخصصية فقه واصوله': ['المستوى الأول', 'المستوى الثاني', 'المستوى الثالث', 'المستوى الرابع'],
        'تخصصية تفسير وحديث': ['المستوى الأول', 'المستوى الثاني', 'المستوى الثالث', 'المستوى الرابع'],
        'تخصصية لغة عربية': ['المستوى الأول', 'المستوى الثاني', 'المستوى الثالث', 'المستوى الرابع'],
        'تخصصية عقيدة': ['المستوى الأول', 'المستوى الثاني', 'المستوى الثالث', 'المستوى الرابع'],
        'شعبة عامة متقدمة': ['المستوى الأول', 'المستوى الثاني', 'المستوى الثالث', 'المستوى الرابع'],
    }
    
    print("✨ إنشاء المراحل والمستويات الجديدة...")
    
    # إنشاء المراحل والمستويات الجديدة
    new_levels = {}
    for stage_name, levels in stages_levels.items():
        # إنشاء المرحلة
        stage = Stage.objects.create(name=stage_name)
        print(f"✅ تم إنشاء المرحلة: {stage_name}")
        
        # إنشاء المستويات لهذه المرحلة
        for level_name in levels:
            level = Level.objects.create(stage=stage, name=level_name)
            new_levels[f"{stage_name}_{level_name}"] = level
            print(f"  ✅ تم إنشاء المستوى: {level_name}")
    
    # إعادة ربط الطلاب بالمستويات الجديدة
    if student_level_mapping:
        print("🔗 إعادة ربط الطلاب بالمستويات الجديدة...")
        
        for student_id, old_data in student_level_mapping.items():
            try:
                student = Student.objects.get(id=student_id)
                old_stage = old_data['stage_name']
                old_level = old_data['level_name']
                
                # تحويل المراحل القديمة إلى الجديدة
                if old_stage == 'تخصصية':
                    # للمراحل التخصصية القديمة، نضعها في تخصصية فقه واصوله كافتراضي
                    new_stage_name = 'تخصصية فقه واصوله'
                else:
                    new_stage_name = old_stage
                
                # البحث عن المستوى الجديد
                key = f"{new_stage_name}_{old_level}"
                if key in new_levels:
                    student.level = new_levels[key]
                    student.save()
                    print(f"  🔗 تم ربط الطالب {student.full_name} بـ {new_stage_name} - {old_level}")
                else:
                    # إذا لم يوجد المستوى، نضعه في المستوى الأول من نفس المرحلة
                    fallback_key = f"{new_stage_name}_المستوى الأول"
                    if fallback_key in new_levels:
                        student.level = new_levels[fallback_key]
                        student.save()
                        print(f"  ⚠️  تم ربط الطالب {student.full_name} بـ {new_stage_name} - المستوى الأول (افتراضي)")
                    
            except Student.DoesNotExist:
                continue
    
    print("\n🎉 تم الانتهاء من إعادة تعيين جميع المراحل والمستويات!")
    
    # عرض ملخص
    print("\n📊 ملخص النظام الجديد:")
    for stage in Stage.objects.all().order_by('id'):
        levels_count = stage.level_set.count()
        print(f"  {stage.name}: {levels_count} مستوى")
    
    print(f"\n👥 إجمالي الطلاب: {Student.objects.count()}")

if __name__ == '__main__':
    reset_stages_and_levels()
