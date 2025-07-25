from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView, View
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Count, Q
from django.http import HttpResponse
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from .models import Student, Course, StudentResult, Level, Stage, Batch
from .forms import (
    StudentForm, StudentResultsForm, BulkStudentResultsForm,
    StudentPromotionForm, ImportStudentsForm
)
from .utils import (
    export_students_to_excel, export_student_certificate,
    import_students_from_excel
)
from .new_utils import (
    export_comprehensive_results_template, export_comprehensive_results,
    export_student_comprehensive_result, export_application_terms
)

import csv
import pandas as pd

def public_results(request):
    """صفحة البحث العام عن النتائج"""
    if request.method == 'POST':
        search_query = request.POST.get('search_query')
        if search_query:
            # البحث باستخدام رقم الجلوس أو الرقم القومي
            student_result = StudentResult.objects.filter(
                Q(student__current_seat_number=search_query) |
                Q(student__national_id=search_query)
            ).select_related('student', 'level').first()
            
            if student_result:
                # إعداد بيانات النتيجة
                courses = Course.objects.filter(level=student_result.level).order_by('name')
                course_scores = []
                total_score = 0
                max_total_score = 0
                
                for course in courses:
                    score = student_result.get_course_score(course.id)
                    max_score = course.max_score
                    
                    if score is not None:
                        status = 'ناجح' if score >= course.pass_score else 'راسب'
                        css_class = 'text-success' if score >= course.pass_score else 'text-danger'
                        total_score += score
                    else:
                        score = 'غ'
                        status = 'غائب'
                        css_class = 'text-warning'
                    
                    max_total_score += max_score
                    course_scores.append({
                        'course': course,
                        'score': score,
                        'status': status,
                        'class': css_class
                    })
                
                # حساب النسبة المئوية
                percentage = round((total_score / max_total_score) * 100, 1) if max_total_score > 0 else 0
                
                context = {
                    'student_result': student_result,
                    'course_scores': course_scores,
                    'total_score': total_score,
                    'max_total_score': max_total_score,
                    'percentage': percentage,
                    'search_query': search_query
                }
            else:
                messages.error(request, 'لم يتم العثور على نتيجة بهذا الرقم')
                context = {'search_query': search_query}
        else:
            messages.error(request, 'الرجاء إدخال رقم الجلوس أو الرقم القومي')
            context = {}
    else:
        context = {}
    
    return render(request, 'students/public_results.html', context)

# Batch Management Views
class BatchListView(LoginRequiredMixin, UserPassesTestMixin, ListView):
    model = Batch
    template_name = 'students/batch_list.html'
    context_object_name = 'batches'
    paginate_by = 20

    def test_func(self):
        return self.request.user.is_superuser

    def handle_no_permission(self):
        messages.error(self.request, 'عذراً، لا تملك الصلاحية للقيام بهذه العملية')
        return redirect('students:dashboard')

    def get_queryset(self):
        return Batch.objects.all().order_by('-created_at')

class BatchCreateView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    model = Batch
    template_name = 'students/batch_form.html'
    fields = ['name', 'start_date', 'end_date', 'is_active']
    success_url = reverse_lazy('students:batch_list')

    def test_func(self):
        return self.request.user.is_superuser

    def form_valid(self, form):
        messages.success(self.request, _('تم إنشاء الدفعة بنجاح'))
        return super().form_valid(form)

class BatchUpdateView(LoginRequiredMixin, UpdateView):
    model = Batch
    template_name = 'students/batch_form.html'
    fields = ['name', 'start_date', 'end_date', 'is_active']
    success_url = reverse_lazy('students:batch_list')

    def form_valid(self, form):
        messages.success(self.request, _('تم تحديث الدفعة بنجاح'))
        return super().form_valid(form)

class BatchDeleteView(LoginRequiredMixin, DeleteView):
    model = Batch
    template_name = 'students/batch_confirm_delete.html'
    success_url = reverse_lazy('students:batch_list')

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, _('تم حذف الدفعة بنجاح'))
        return super().delete(request, *args, **kwargs)

# Dashboard
@login_required
def dashboard(request):
    # إحصائيات عامة
    if request.user.role == 'supervisor':
        total_students = Student.objects.filter(governorate=request.user.governorate).count()
    else:
        total_students = Student.objects.count()
    total_levels = Level.objects.count()
    total_courses = Course.objects.count()
    total_results = StudentResult.objects.count()

    # إحصائيات حسب المرحلة
    stage_stats = []
    for stage in Stage.objects.all():
        students_count = Student.objects.filter(level__stage=stage).count()
        stage_stats.append({
            'stage': stage,
            'students_count': students_count
        })

    # إحصائيات النتائج
    result_stats = []
    for choice in StudentResult.RESULT_CHOICES:
        count = StudentResult.objects.filter(result=choice[0]).count()
        result_stats.append({
            'result': choice[1],
            'count': count
        })

    students_by_level = Level.objects.annotate(student_count=Count('student')).order_by('stage__name', 'name')
    
    context = {
        'total_students': total_students,
        'total_levels': total_levels,
        'total_courses': total_courses,
        'total_results': total_results,
        'stage_stats': stage_stats,
        'result_stats': result_stats,
        'students_by_level': students_by_level,
    }

    return render(request, 'students/dashboard.html', context)

# Student Management Views
class StudentListView(LoginRequiredMixin, ListView):
    model = Student
    template_name = 'students/student_list.html'
    context_object_name = 'students'

    paginate_by = 50

    def get_queryset(self):
        queryset = super().get_queryset()
        level_id = self.request.GET.get('level')
        search_query = self.request.GET.get('q')

        # تقييد الطلاب حسب محافظة المشرف
        if not self.request.user.is_superuser and hasattr(self.request.user, 'role'):
            if self.request.user.role == 'supervisor':
                queryset = queryset.filter(governorate=self.request.user.governorate)

        if level_id:
            queryset = queryset.filter(level_id=level_id)
        if search_query:
            queryset = queryset.filter(
                Q(full_name__icontains=search_query) |
                Q(code__icontains=search_query) |
                Q(current_seat_number__icontains=search_query)
            )

        return queryset.order_by('level__stage__name', 'level__name', 'current_seat_number')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['levels'] = Level.objects.all()
        context['enrollment_statuses'] = Student.ENROLLMENT_CHOICES
        return context

class StudentDetailView(LoginRequiredMixin, DetailView):
    model = Student
    template_name = 'students/student_detail.html'
    context_object_name = 'student'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        student = self.get_object()
        # الحصول على النتائج الشاملة للطالب
        context['final_results'] = student.final_results.all().order_by('-academic_year')
        return context

class StudentCreateView(LoginRequiredMixin, CreateView):
    model = Student
    form_class = StudentForm
    template_name = 'students/student_form.html'
    success_url = reverse_lazy('students:student_list')

    def form_valid(self, form):
        if not self.request.user.is_superuser and hasattr(self.request.user, 'role'):
            if self.request.user.role == 'supervisor':
                form.instance.governorate = self.request.user.governorate
        messages.success(self.request, _('تم إضافة الطالب بنجاح'))
        return super().form_valid(form)

class StudentUpdateView(LoginRequiredMixin, UpdateView):
    model = Student
    form_class = StudentForm
    template_name = 'students/student_form.html'
    success_url = reverse_lazy('students:student_list')

    def get_queryset(self):
        queryset = super().get_queryset()
        if not self.request.user.is_superuser and hasattr(self.request.user, 'role'):
            if self.request.user.role == 'supervisor':
                return queryset.filter(governorate=self.request.user.governorate)
        return queryset

    def form_valid(self, form):
        if not self.request.user.is_superuser and hasattr(self.request.user, 'role'):
            if self.request.user.role == 'supervisor':
                form.instance.governorate = self.request.user.governorate
        messages.success(self.request, _('تم تحديث بيانات الطالب بنجاح'))
        return super().form_valid(form)

class StudentDeleteView(LoginRequiredMixin, DeleteView):
    model = Student
    template_name = 'students/student_confirm_delete.html'
    success_url = reverse_lazy('students:student_list')

    def get_queryset(self):
        queryset = super().get_queryset()
        if not self.request.user.is_superuser and hasattr(self.request.user, 'role'):
            if self.request.user.role == 'supervisor':
                return queryset.filter(governorate=self.request.user.governorate)
        return queryset

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, _('تم حذف الطالب بنجاح'))
        return super().delete(request, *args, **kwargs)

# Comprehensive Results System
class StudentResultListView(LoginRequiredMixin, ListView):
    model = StudentResult
    template_name = 'students/comprehensive_results_list.html'
    context_object_name = 'results'
    # paginate_by = 50

    def get_queryset(self):
        queryset = super().get_queryset()
        level_id = self.request.GET.get('level')
        batch_id = self.request.GET.get('batch')
        academic_year = self.request.GET.get('academic_year')
        result_status = self.request.GET.get('status')
        search_query = self.request.GET.get('q')

        filters = {}
        if level_id:
            filters['level_id'] = level_id
        if batch_id:
            filters['batch_id'] = batch_id
        if academic_year and academic_year.strip():
            filters['academic_year'] = academic_year
        if result_status:
            filters['result'] = result_status
        if search_query:
            filters['student__full_name__icontains'] = search_query

        # تقييد النتائج لمشرف المحافظة
        if not self.request.user.is_superuser and hasattr(self.request.user, 'role'):
            if self.request.user.role == 'supervisor':
                filters['student__governorate'] = self.request.user.governorate

        return queryset.filter(**filters).order_by('-academic_year', 'student__full_name')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['levels'] = Level.objects.all()
        context['batches'] = Batch.objects.filter(is_active=True).order_by('-created_at')
        context['academic_years'] = StudentResult.objects.values_list('academic_year', flat=True).distinct().order_by('-academic_year')
        context['result_statuses'] = StudentResult.RESULT_CHOICES

        level_id = self.request.GET.get('level')
        academic_year = self.request.GET.get('academic_year')

        if level_id and academic_year:
            level = Level.objects.get(id=level_id)
            courses = Course.objects.filter(level=level).order_by('name')
            context['courses'] = courses

            # إعداد البيانات للعرض الشامل
            results_with_scores = []
            for result in context['results']:
                student_data = {
                    'result': result,
                    'course_scores': []
                }

                for course in courses:
                    score = result.get_course_score(course.id)
                    if score is not None:
                        is_passed = score >= course.pass_score
                        score_data = {
                            'course': course,
                            'score': score,
                            'status': 'ناجح' if is_passed else 'راسب',
                            'class': 'text-success' if is_passed else 'text-danger'
                        }
                    else:
                        score_data = {
                            'course': course,
                            'score': 'غ',
                            'status': 'غائب',
                            'class': 'text-warning'
                        }

                    student_data['course_scores'].append(score_data)

                results_with_scores.append(student_data)

            context['results_with_scores'] = results_with_scores

        return context

# Comprehensive Results List
@login_required
def comprehensive_results_list(request):
    """عرض النتائج الشاملة"""
    # الحصول على الفلاتر
    level_id = request.GET.get('level')
    batch_id = request.GET.get('batch')
    academic_year = request.GET.get('academic_year')
    status = request.GET.get('status')
    search_query = request.GET.get('q')

    # بناء الاستعلام
    results = StudentResult.objects.all()

    # تقييد النتائج لمشرف المحافظة
    if not request.user.is_superuser and hasattr(request.user, 'role'):
        if request.user.role == 'supervisor':
            results = results.filter(student__governorate=request.user.governorate)

    if level_id:
        results = results.filter(level_id=level_id)
    if batch_id:
        results = results.filter(batch_id=batch_id)
    if academic_year:
        results = results.filter(academic_year=academic_year)
    if status:
        results = results.filter(result=status)
    if search_query:
        results = results.filter(
            Q(student__full_name__icontains=search_query) |
            Q(student__code__icontains=search_query)
        )

    results = results.select_related('student', 'level', 'batch').order_by('student__code')

    # إعداد البيانات للعرض التفصيلي
    results_with_scores = []
    courses = []

    # إذا لم يتم اختيار مستوى، استخدم المستوى الأول
    if not level_id and results.exists():
        # الحصول على أول مستوى متاح
        first_result = results.first()
        if first_result:
            level_id = first_result.level.id

    # معالجة النتائج سواء تم اختيار مستوى أم لا
    if level_id:
        try:
            level = Level.objects.get(id=level_id)
            courses = Course.objects.filter(level=level).order_by('name')
        except Level.DoesNotExist:
            # عرض جميع المستويات المتاحة في حالة الخطأ
            available_levels = Level.objects.all()
            level_list = ', '.join([f'{l.id}: {l.name}' for l in available_levels])
            messages.error(request, f'المستوى برقم {level_id} غير موجود. المستويات المتاحة: {level_list}')
            return redirect('students:comprehensive_results_list')

    # معالجة كل نتيجة على حدة
    for result in results:
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

        # استخدام المواد المحددة مسبقاً
        for course in courses:
            score = result.get_course_score(course.id)
            max_score = course.max_score

            # تحديد حالة المادة
            if score is not None:
                if score < (max_score * 0.5):  # أقل من 50% = راسب
                    status = 'راسب'
                    css_class = 'score-fail'
                    failed_courses.append(course.name)
                elif score < (max_score * 0.65):  # أقل من 65% = ضعيف
                    status = 'ضعيف'
                    css_class = 'score-weak'
                elif score < (max_score * 0.75):  # أقل من 75% = مقبول
                    status = 'مقبول'
                    css_class = 'score-acceptable'
                elif score < (max_score * 0.85):  # أقل من 85% = جيد
                    status = 'جيد'
                    css_class = 'score-good'
                else:  # 85% فأكثر = ممتاز
                    status = 'ممتاز'
                    css_class = 'score-excellent'

                total_score += score
            else:
                score = 'غ'  # غائب
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

        # حساب النسبة المئوية
        if max_total_score > 0:
            percentage = round((total_score / max_total_score) * 100, 1)
        else:
            percentage = 0

        student_data['total_score'] = total_score
        student_data['max_total_score'] = max_total_score
        student_data['percentage'] = percentage
        student_data['failed_courses'] = failed_courses

        results_with_scores.append(student_data)

    # إذا لم توجد مواد مشتركة، استخدم مواد أول نتيجة
    if not courses and results_with_scores:
        courses = Course.objects.filter(level=results_with_scores[0]['result'].level).order_by('name')

    # إعداد البيانات للسياق

    # عرض رسالة توضيحية إذا لم يتم اختيار مستوى
    if not level_id:
        all_levels = Level.objects.all()
        if all_levels.exists():
            level_debug = ', '.join([f'{l.stage.name} - {l.name} (ID: {l.id})' for l in all_levels])
            messages.info(request, f'يرجى اختيار مستوى لعرض النتائج التفصيلية. المستويات المتاحة: {level_debug}')
        else:
            messages.warning(request, 'لا توجد مستويات في النظام')

    context = {
        'results': results,
        'results_with_scores': results_with_scores,
        'courses': courses,
        'levels': Level.objects.all(),
        'batches': Batch.objects.all(),
        'result_statuses': StudentResult.RESULT_CHOICES,
        'selected_level': level_id,
        'selected_batch': batch_id,
        'selected_status': status,
        'search_query': search_query,
        'current_level_id': level_id,  # للاستخدام في الروابط

    }

    return render(request, 'students/comprehensive_results_list.html', context)


# Bulk upload comprehensive results
@login_required
def bulk_upload_comprehensive_results(request):
    """رفع النتائج الشاملة بالجملة"""
    if not request.user.is_superuser:
        messages.error(request, 'عذراً، ليس لديك صلاحية للوصول إلى هذه الصفحة')
        return redirect('students:results_list')

    # تصدير نموذج إذا تم طلب ذلك
    if request.method == 'GET' and 'export_template' in request.GET:
        level_id = request.GET.get('level')

        if level_id:
            level = get_object_or_404(Level, id=level_id)
            return export_comprehensive_results_template(level)
        else:
            messages.error(request, 'يرجى اختيار المستوى أولاً')

    if request.method == 'POST':
        form = BulkStudentResultsForm(request.POST, request.FILES)
        if form.is_valid():
            level = form.cleaned_data['level']
            batch = form.cleaned_data['batch']
            results_file = request.FILES.get('results_file')

            if results_file and results_file.name.endswith(('.xlsx', '.xls')):
                try:
                    # قراءة ملف Excel
                    df = pd.read_excel(results_file)

                    # التحقق من الأعمدة المطلوبة
                    required_columns = ['رقم الجلوس الحالي']
                    courses = Course.objects.filter(level=level)

                    for course in courses:
                        required_columns.append(course.name)

                    missing_columns = [col for col in required_columns if col not in df.columns]
                    if missing_columns:
                        messages.error(request, f'الأعمدة التالية مفقودة: {", ".join(missing_columns)}')
                        return render(request, 'students/bulk_upload_comprehensive_results.html', {'form': form})

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
    return render(request, 'students/bulk_upload_comprehensive_results.html', context)

# Export Functions
@login_required
def export_comprehensive_results_view(request, level_id):
    """تصدير النتائج الشاملة"""
    level = get_object_or_404(Level, id=level_id)
    batch_id = request.GET.get('batch')

    return export_comprehensive_results(level, batch_id)

# Student Promotion Views
@login_required
def promote_students(request):
    # التحقق من أن المستخدم هو مدير النظام
    if not request.user.is_superuser:
        messages.error(request, 'عذراً، لا تملك الصلاحية للقيام بهذه العملية')
        return redirect('students:dashboard')
    if request.method == 'POST':
        form = StudentPromotionForm(request.POST)
        if form.is_valid():
            from_level = form.cleaned_data['from_level']
            to_level = form.cleaned_data['to_level']
            batch = form.cleaned_data['batch']

            # الحصول على الطلاب المؤهلين للترقية
            results = StudentResult.objects.filter(
                level=from_level,
                batch=batch
            ).exclude(result='راسب')

            promoted_count = 0
            for result in results:
                student = result.student

                # تحديث بيانات الطالب
                student.level = to_level
                student.previous_seat_number = student.current_seat_number
                student.enrollment_status = 'منقول' if result.result == 'ناجح ومنقول' else 'منقول بمواد'
                student.save()

                promoted_count += 1

            messages.success(
                request,
                f'تم ترقية {promoted_count} طالب من {from_level} إلى {to_level}'
            )
            return redirect('students:student_list')
    else:
        form = StudentPromotionForm()

    return render(request, 'students/promote_students.html', {'form': form})

# Export and Import Functions
@login_required
def export_students(request):
    level_id = request.GET.get('level_id')
    academic_year = request.GET.get('academic_year')

    if level_id:
        students = Student.objects.filter(level_id=level_id)
    else:
        students = Student.objects.all()

    response = export_students_to_excel(students, academic_year)
    return response

@login_required
def export_student_results(request, pk):
    student = get_object_or_404(Student, pk=pk)
    academic_year = request.GET.get('academic_year')

    response = export_student_comprehensive_result(student, academic_year)
    return response

@login_required
def print_student_certificate(request, pk):
    student = get_object_or_404(Student, pk=pk)
    response = export_student_certificate(student)
    return response

@login_required
def print_student_result(request, pk):
    """طباعة نتيجة الطالب"""
    student = get_object_or_404(Student, pk=pk)
    level_id = request.GET.get('level')
    batch_id = request.GET.get('batch')

    # الحصول على نتيجة الطالب
    result = None
    if level_id and batch_id:
        result = StudentResult.objects.filter(
            student=student,
            level_id=level_id,
            batch_id=batch_id
        ).first()

    if not result:
        # البحث عن أحدث نتيجة
        result = StudentResult.objects.filter(student=student).order_by('-result_date').first()

    if not result:
        messages.error(request, 'لا توجد نتيجة لهذا الطالب')
        return redirect('students:student_detail', pk=pk)

    # إعداد بيانات الطباعة
    level = result.level
    courses = Course.objects.filter(level=level).order_by('name')

    course_results = []
    total_score = 0
    max_total_score = 0
    failed_courses = []

    for course in courses:
        score_val = result.get_course_score(course.id)
        max_score = course.max_score
        
        display_score = score_val
        status = ''

        if score_val is not None:
            try:
                score = float(score_val)
                if score < (max_score * 0.5):
                    status = 'راسب'
                    failed_courses.append(course.name)
                elif score < (max_score * 0.65):
                    status = 'ضعيف'
                elif score < (max_score * 0.75):
                    status = 'مقبول'
                elif score < (max_score * 0.85):
                    status = 'جيد'
                else:
                    status = 'ممتاز'

                total_score += score
            except (ValueError, TypeError):
                display_score = 'غ'
                status = 'غائب'
                failed_courses.append(course.name)
        else:
            display_score = 'غ'
            status = 'غائب'
            failed_courses.append(course.name)

        max_total_score += max_score

        course_results.append({
            'course': course,
            'score': display_score,
            'status': status
        })

    # حساب النسبة المئوية
    percentage = round((total_score / max_total_score) * 100, 1) if max_total_score > 0 else 0

    context = {
        'student': student,
        'result': result,
        'course_results': course_results,
        'total_score': total_score,
        'max_total_score': max_total_score,
        'percentage': percentage,
        'failed_courses': failed_courses,
        'level': level,
        'batch': result.batch
    }

    return render(request, 'students/print_student_result.html', context)

@login_required
def import_students(request):
    if request.method == 'POST':
        form = ImportStudentsForm(request.POST, request.FILES)
        if form.is_valid():
            file = request.FILES['file']
            update_existing = form.cleaned_data['update_existing']

            success, message = import_students_from_excel(file, update_existing)

            if success:
                messages.success(request, message)
            else:
                messages.error(request, message)

            return redirect('students:student_list')
    else:
        form = ImportStudentsForm()

    return render(request, 'students/import_students.html', {'form': form})

# Search and Utility Functions
@login_required
def search_student(request):
    query = request.GET.get('q', '')
    students = None

    if query:
        students = Student.objects.filter(
            Q(full_name__icontains=query) |
            Q(code__icontains=query) |
            Q(current_seat_number__icontains=query) |
            Q(national_id__icontains=query)
        )

    context = {
        'students': students,
        'query': query
    }

    return render(request, 'students/search_results.html', context)

@login_required
def delete_all_students(request):
    if request.method == 'POST':
        password_confirmation = request.POST.get('password_confirmation')

        if password_confirmation == 'DELETE_ALL_STUDENTS':
            students_count = Student.objects.count()
            Student.objects.all().delete()

            messages.success(request, f'تم حذف {students_count} طالب بنجاح')
            return redirect('students:student_list')
        else:
            messages.error(request, 'كلمة التأكيد غير صحيحة. يجب كتابة "DELETE_ALL_STUDENTS" بالضبط')

    students_count = Student.objects.count()
    context = {
        'students_count': students_count,
    }

    return render(request, 'students/delete_all_students.html', context)

# AJAX Views
def load_levels(request):
    stage_id = request.GET.get('stage_id')
    levels = Level.objects.filter(stage_id=stage_id).order_by('name')
    return render(request, 'students/level_dropdown_list_options.html', {'levels': levels})

@login_required
def export_application_terms_view(request):
    """تصدير ملف المسميات والمصطلحات المستخدمة في التطبيق"""
    return export_application_terms()

# StudentResult Delete View
class StudentResultDeleteView(LoginRequiredMixin, DeleteView):
    model = StudentResult
    template_name = 'students/studentresult_confirm_delete.html'
    success_url = reverse_lazy('students:results_list')

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, _('تم حذف النتيجة بنجاح'))
        return super().delete(request, *args, **kwargs)

# Delete All Filtered Results
@login_required
def delete_all_results(request):
    """حذف جميع النتائج التي تطابق الفلاتر الحالية"""
    # الحصول على نفس الفلاتر المستخدمة في عرض القائمة
    level_id = request.GET.get('level')
    batch_id = request.GET.get('batch')
    status = request.GET.get('status')
    search_query = request.GET.get('q')

    # بناء الاستعلام
    results_to_delete = StudentResult.objects.all()

    filters = {}
    if level_id:
        results_to_delete = results_to_delete.filter(level_id=level_id)
        filters['level'] = level_id
    if batch_id:
        results_to_delete = results_to_delete.filter(batch_id=batch_id)
        filters['batch'] = batch_id
    if status:
        results_to_delete = results_to_delete.filter(result=status)
        filters['status'] = status
    if search_query:
        results_to_delete = results_to_delete.filter(
            Q(student__full_name__icontains=search_query) |
            Q(student__code__icontains=search_query)
        )
        filters['q'] = search_query

    count = results_to_delete.count()

    if request.method == 'POST':
        # التحقق من كلمة التأكيد
        if request.POST.get('confirmation') == 'DELETE_ALL':
            deleted_count, _ = results_to_delete.delete()
            messages.success(request, f'تم حذف {deleted_count} نتيجة بنجاح.')
            return redirect('students:results_list')
        else:
            messages.error(request, 'كلمة التأكيد غير صحيحة. لم يتم حذف أي شيء.')
            # إعادة توجيه مع نفس الفلاتر
            return redirect(f"{reverse('students:delete_all_results')}?{request.GET.urlencode()}")

    context = {
        'count': count,
        'filters_query': request.GET.urlencode()
    }
    return render(request, 'students/delete_all_results_confirm.html', context)

@login_required
def bulk_delete_results(request):
    """حذف نتائج حسب المرحلة والمستوى والدفعة"""
    if request.method == 'POST':
        level_id = request.POST.get('level')
        batch_id = request.POST.get('batch')
        confirmation = request.POST.get('confirmation')

        if not level_id or not batch_id:
            messages.error(request, 'يرجى اختيار المرحلة والمستوى والدفعة أولاً.')
            return redirect('students:bulk_delete_results')

        level = get_object_or_404(Level, id=level_id)
        batch = get_object_or_404(Batch, id=batch_id)
        
        # More robust confirmation
        if confirmation == f'DELETE_{level.id}_{batch.id}':
            results_to_delete = StudentResult.objects.filter(level=level, batch=batch)
            deleted_count, _ = results_to_delete.delete()
            messages.success(request, f'تم حذف {deleted_count} نتيجة بنجاح للمستوى "{level.name}" ودفعة "{batch.name}".')
            return redirect('students:results_list')
        else:
            messages.error(request, 'كلمة التأكيد غير صحيحة. لم يتم حذف أي شيء.')
            return redirect('students:bulk_delete_results')

    stages = Stage.objects.all()
    batches = Batch.objects.filter(is_active=True).order_by('-name')
    context = {
        'stages': stages,
        'batches': batches,
    }
    return render(request, 'students/bulk_delete_results.html', context)
