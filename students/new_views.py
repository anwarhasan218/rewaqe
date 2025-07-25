from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponse
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from .models import Student, Course, StudentResult, Level, Stage, Batch
from .forms import BulkStudentResultsForm, StudentResultsForm

import pandas as pd
import csv
import io

@login_required
def bulk_upload_comprehensive_results(request):
    """رفع النتائج الشاملة بالجملة"""
    
    # تصدير نموذج إذا تم طلب ذلك
    if request.method == 'GET' and 'export_template' in request.GET:
        level_id = request.GET.get('level')
        academic_year = request.GET.get('academic_year')
        
        if level_id:
            level = get_object_or_404(Level, id=level_id)
            return export_comprehensive_results_template(level, academic_year)
        else:
            messages.error(request, 'يرجى اختيار المستوى أولاً')

    if request.method == 'POST':
        form = BulkStudentResultsForm(request.POST, request.FILES)
        if form.is_valid():
            level = form.cleaned_data['level']
            batch = form.cleaned_data['batch']
            academic_year = form.cleaned_data['academic_year']
            results_file = request.FILES.get('results_file')

            if results_file and results_file.name.endswith(('.xlsx', '.xls')):
                try:
                    # قراءة ملف Excel
                    df = pd.read_excel(results_file)
                    
                    # التحقق من الأعمدة المطلوبة بمرونة
                    # نستخدم strip للأعمدة ونجعل المقارنة غير حساسة للمسافات الزائدة
                    df_columns_stripped = [str(col).strip() for col in df.columns]
                    courses = Course.objects.filter(level=level)
                    required_columns = ['رقم الجلوس الحالي'] + [course.name for course in courses]
                    missing_columns = [col for col in required_columns if col.strip() not in df_columns_stripped]
                    context = {'form': form, 'df_columns': list(df.columns), 'title': 'رفع النتائج الشاملة بالجملة'}
                    if missing_columns:
                        messages.error(request, f'الأعمدة التالية مفقودة: {", ".join(missing_columns)}')
                        return render(request, 'students/bulk_upload_comprehensive_results.html', context)

                    imported_count = 0
                    updated_count = 0
                    errors = []

                    for _, row in df.iterrows():
                        try:
                            # البحث عن الطالب
                            seat_number = str(row['رقم الجلوس الحالي']).strip()
                            
                            try:
                                student = Student.objects.get(current_seat_number=seat_number)
                            except Student.DoesNotExist:
                                errors.append(f"الطالب برقم الجلوس {seat_number} غير موجود")
                                continue

                            # إنشاء أو تحديث النتيجة الشاملة
                            student_result, created = StudentResult.objects.get_or_create(
                                student=student,
                                level=level,
                                batch=batch,
                                academic_year=academic_year,
                                defaults={
                                    'result': 'قيد المراجعة',
                                    'total_score': 0,
                                    'result_date': timezone.now()
                                }
                            )

                            # حفظ درجات المواد
                            course_scores = {}
                            total_score = 0
                            failed_courses = []

                            for course in courses:
                                if course.name in row and not pd.isna(row[course.name]):
                                    value = row[course.name]
                                    # إذا كانت الدرجة غائب أو نص غير رقمي
                                    if str(value).strip() == "غـ" or (isinstance(value, str) and not value.strip().isdigit()):
                                        course_scores[str(course.id)] = "غـ"
                                        failed_courses.append(course)
                                    else:
                                        try:
                                            score = int(float(value))
                                            # التحقق من صحة الدرجة
                                            if 0 <= score <= course.max_score:
                                                course_scores[str(course.id)] = score
                                                total_score += score
                                                # تحديد المواد الراسب فيها
                                                if score < course.pass_score:
                                                    failed_courses.append(course)
                                            else:
                                                errors.append(f'درجة غير صحيحة للطالب {student.full_name} في مادة {course.name}: {score}')
                                        except (ValueError, TypeError):
                                            errors.append(f'درجة غير صالحة للطالب {student.full_name} في مادة {course.name}')

                            # تحديد النتيجة النهائية
                            if len(failed_courses) == 0:
                                result_status = 'ناجح ومنقول'
                            elif len(failed_courses) <= 2:
                                result_status = 'ناجح بمواد'
                            else:
                                result_status = 'راسب'

                            # تحديث النتيجة
                            student_result.course_scores = course_scores
                            student_result.total_score = total_score
                            student_result.result = result_status
                            student_result.result_date = timezone.now()
                            student_result.save()

                            # تحديث المواد المتعثر فيها
                            student_result.failed_courses.set(failed_courses)

                            if created:
                                imported_count += 1
                            else:
                                updated_count += 1

                        except Exception as e:
                            errors.append(f'خطأ في معالجة الطالب {seat_number}: {str(e)}')

                    # عرض النتائج
                    if imported_count > 0:
                        messages.success(request, f'تم إنشاء {imported_count} نتيجة جديدة')
                    if updated_count > 0:
                        messages.success(request, f'تم تحديث {updated_count} نتيجة')
                    if errors:
                        for error in errors[:10]:  # عرض أول 10 أخطاء فقط
                            messages.error(request, error)
                        if len(errors) > 10:
                            messages.warning(request, f'وهناك {len(errors) - 10} أخطاء أخرى')

                    return redirect('students:results_list')

                except Exception as e:
                    messages.error(request, f'خطأ في قراءة الملف: {str(e)}')
            else:
                messages.error(request, 'يرجى رفع ملف Excel فقط')
    else:
        form = BulkStudentResultsForm()

    context = {
        'form': form,
        'title': 'رفع النتائج الشاملة بالجملة'
    }
    if 'df_columns' not in context:
        context['df_columns'] = None
    return render(request, 'students/bulk_upload_comprehensive_results.html', context)


def export_comprehensive_results_template(level, academic_year=None):
    """تصدير نموذج النتائج الشاملة كملف Excel (xlsx)"""
    
    # إعداد الأعمدة
    courses = Course.objects.filter(level=level).order_by('name')
    columns = ['رقم الجلوس الحالي', 'اسم الطالب'] + [course.name for course in courses]

    # إعداد البيانات
    students = Student.objects.filter(level=level).order_by('current_seat_number')
    data = []
    for student in students:
        row = [student.current_seat_number, student.full_name]
        row += ['' for _ in courses]  # خلايا فارغة للدرجات
        data.append(row)

    df = pd.DataFrame(data, columns=columns)

    # إنشاء ملف Excel في الذاكرة
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='النموذج')
    output.seek(0)

    response = HttpResponse(output.read(), content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = f'attachment; filename="comprehensive_results_template_{level.name}.xlsx"'
    return response


@login_required
def export_comprehensive_results(request, level_id):
    """تصدير النتائج الشاملة"""
    level = get_object_or_404(Level, id=level_id)
    academic_year = request.GET.get('academic_year')
    
    if not academic_year:
        messages.error(request, 'يرجى تحديد العام الدراسي')
        return redirect('students:results_list')
    
    # إنشاء ملف CSV
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="comprehensive_results_{level.name}_{academic_year}.csv"'
    response.write('\ufeff')  # BOM for Excel to recognize UTF-8

    writer = csv.writer(response)
    
    # إنشاء العناوين
    headers = ['الكود', 'رقم الجلوس', 'الاسم']
    courses = Course.objects.filter(level=level).order_by('name')
    
    for course in courses:
        headers.append(course.name)
    
    headers.extend(['المجموع', 'النتيجة', 'المواد المتعثر فيها'])
    writer.writerow(headers)
    
    # الحصول على النتائج
    results = StudentResult.objects.filter(
        level=level, 
        academic_year=academic_year
    ).order_by('student__code')
    
    for result in results:
        student = result.student
        row = [student.code, student.current_seat_number, student.full_name]
        
        # إضافة درجات المواد
        for course in courses:
            score = result.get_course_score(course.id)
            row.append(score if score is not None else 'غ')
        
        # إضافة المجموع والنتيجة
        row.append(result.total_score)
        row.append(result.result)
        
        # إضافة المواد المتعثر فيها
        failed_courses = result.failed_courses.all()
        if failed_courses:
            notes = ', '.join([course.name for course in failed_courses])
            row.append(notes)
        else:
            row.append('')
        
        writer.writerow(row)
    
    return response
