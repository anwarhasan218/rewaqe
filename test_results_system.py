#!/usr/bin/env python
"""
اختبار نظام النتائج بعد الإصلاحات
"""

import os
import sys
import django

# إعداد Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'azhar_student_management.settings')
django.setup()

from students.models import Student, Course, CourseResult, StudentResult, Level, Stage, Batch

def test_result_choices():
    """اختبار خيارات النتائج"""
    print("🔍 اختبار خيارات النتائج...")
    
    # التحقق من أن جميع خيارات النتائج متوفرة
    expected_choices = [
        'ناجح',
        'ناجح ومنقول', 
        'ناجح بمواد',
        'منقول بمواد',
        'راسب',
        'باقي للإعادة',
        'غائب'
    ]
    
    available_choices = [choice[0] for choice in StudentResult.RESULT_CHOICES]
    
    for choice in expected_choices:
        if choice in available_choices:
            print(f"✅ خيار '{choice}' متوفر")
        else:
            print(f"❌ خيار '{choice}' غير متوفر")
    
    print(f"📊 إجمالي الخيارات المتوفرة: {len(available_choices)}")
    print()

def test_model_fields():
    """اختبار حقول النماذج"""
    print("🔍 اختبار حقول النماذج...")
    
    # اختبار حقول StudentResult
    student_result_fields = [field.name for field in StudentResult._meta.fields]
    required_fields = ['total_score', 'result_date', 'academic_year']
    
    for field in required_fields:
        if field in student_result_fields:
            print(f"✅ حقل '{field}' موجود في StudentResult")
        else:
            print(f"❌ حقل '{field}' غير موجود في StudentResult")
    
    # اختبار حقول CourseResult
    course_result_fields = [field.name for field in CourseResult._meta.fields]
    if 'academic_year' in course_result_fields:
        print("✅ حقل 'academic_year' موجود في CourseResult")
    else:
        print("❌ حقل 'academic_year' غير موجود في CourseResult")
    
    print()

def test_related_names():
    """اختبار أسماء العلاقات"""
    print("🔍 اختبار أسماء العلاقات...")
    
    # التحقق من related_name
    try:
        # يجب أن يعمل هذا إذا كان related_name صحيح
        student_field = StudentResult._meta.get_field('student')
        related_name = student_field.related_query_name()
        print(f"✅ related_name للطالب: {related_name}")
    except Exception as e:
        print(f"❌ خطأ في related_name: {e}")
    
    print()

def test_database_connection():
    """اختبار الاتصال بقاعدة البيانات"""
    print("🔍 اختبار الاتصال بقاعدة البيانات...")
    
    try:
        # محاولة عد السجلات
        students_count = Student.objects.count()
        courses_count = Course.objects.count()
        results_count = StudentResult.objects.count()
        
        print(f"✅ عدد الطلاب: {students_count}")
        print(f"✅ عدد المواد: {courses_count}")
        print(f"✅ عدد النتائج: {results_count}")
        
    except Exception as e:
        print(f"❌ خطأ في الاتصال بقاعدة البيانات: {e}")
    
    print()

def test_create_sample_result():
    """اختبار إنشاء نتيجة تجريبية"""
    print("🔍 اختبار إنشاء نتيجة تجريبية...")
    
    try:
        # البحث عن أول طالب ومستوى ودفعة
        student = Student.objects.first()
        level = Level.objects.first()
        batch = Batch.objects.first()
        
        if student and level and batch:
            # محاولة إنشاء نتيجة تجريبية
            result, created = StudentResult.objects.get_or_create(
                student=student,
                level=level,
                batch=batch,
                academic_year='2024-2025',
                defaults={
                    'result': 'ناجح ومنقول',
                    'total_score': 450
                }
            )
            
            if created:
                print("✅ تم إنشاء نتيجة تجريبية بنجاح")
                # حذف النتيجة التجريبية
                result.delete()
                print("✅ تم حذف النتيجة التجريبية")
            else:
                print("✅ النتيجة موجودة مسبقاً")
                
        else:
            print("⚠️ لا توجد بيانات كافية لإنشاء نتيجة تجريبية")
            
    except Exception as e:
        print(f"❌ خطأ في إنشاء النتيجة التجريبية: {e}")
    
    print()

def main():
    """تشغيل جميع الاختبارات"""
    print("🚀 بدء اختبار نظام النتائج بعد الإصلاحات")
    print("=" * 50)
    
    test_result_choices()
    test_model_fields()
    test_related_names()
    test_database_connection()
    test_create_sample_result()
    
    print("✅ انتهاء جميع الاختبارات")
    print("=" * 50)

if __name__ == "__main__":
    main()
