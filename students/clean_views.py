from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin
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
    export_student_comprehensive_result
)
from .new_views import bulk_upload_comprehensive_results

import csv
import pandas as pd

# Batch Management Views
class BatchListView(LoginRequiredMixin, ListView):
    model = Batch
    template_name = 'students/batch_list.html'
    context_object_name = 'batches'
    paginate_by = 20

    def get_queryset(self):
        return Batch.objects.all().order_by('-created_at')

class BatchCreateView(LoginRequiredMixin, CreateView):
    model = Batch
    template_name = 'students/batch_form.html'
    fields = ['name', 'start_date', 'end_date', 'is_active']
    success_url = reverse_lazy('students:batch_list')

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

    context = {
        'total_students': total_students,
        'total_levels': total_levels,
        'total_courses': total_courses,
        'total_results': total_results,
        'stage_stats': stage_stats,
        'result_stats': result_stats,
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
        messages.success(self.request, _('تم إضافة الطالب بنجاح'))
        return super().form_valid(form)

class StudentUpdateView(LoginRequiredMixin, UpdateView):
    model = Student
    form_class = StudentForm
    template_name = 'students/student_form.html'
    success_url = reverse_lazy('students:student_list')

    def form_valid(self, form):
        messages.success(self.request, _('تم تحديث بيانات الطالب بنجاح'))
        return super().form_valid(form)

class StudentDeleteView(LoginRequiredMixin, DeleteView):
    model = Student
    template_name = 'students/student_confirm_delete.html'
    success_url = reverse_lazy('students:student_list')

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, _('تم حذف الطالب بنجاح'))
        return super().delete(request, *args, **kwargs)

# Comprehensive Results System
class StudentResultListView(LoginRequiredMixin, ListView):
    model = StudentResult
    template_name = 'students/comprehensive_results_list.html'
    context_object_name = 'results'
    paginate_by = 50

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

# Generate Results from Comprehensive Data
@login_required
def generate_comprehensive_results(request):
    """إنشاء النتائج النهائية من البيانات الشاملة"""
    if request.method == 'POST':
        form = StudentResultsForm(request.POST)
        if form.is_valid():
            academic_year = form.cleaned_data['academic_year']
            level = form.cleaned_data['level']
            batch = form.cleaned_data['batch']

            # الحصول على جميع الطلاب في هذا المستوى
            students = Student.objects.filter(level=level)
            courses = Course.objects.filter(level=level)

            created_count = 0
            updated_count = 0

            for student in students:
                # التحقق من وجود نتيجة شاملة للطالب
                student_result, created = StudentResult.objects.get_or_create(
                    student=student,
                    level=level,
                    batch=batch,
                    academic_year=academic_year,
                    defaults={
                        'result': 'قيد المراجعة',
                        'total_score': 0,
                        'result_date': timezone.now(),
                        'course_scores': {}
                    }
                )

                if created:
                    created_count += 1
                else:
                    updated_count += 1

            if created_count > 0:
                messages.success(request, f'تم إنشاء {created_count} نتيجة جديدة')
            if updated_count > 0:
                messages.info(request, f'تم العثور على {updated_count} نتيجة موجودة مسبقاً')

            return redirect('students:results_list')
    else:
        form = StudentResultsForm()

    return render(request, 'students/generate_results.html', {'form': form})

# Export Functions
@login_required
def export_comprehensive_results_view(request, level_id):
    """تصدير النتائج الشاملة"""
    level = get_object_or_404(Level, id=level_id)
    academic_year = request.GET.get('academic_year')
    
    if not academic_year:
        messages.error(request, 'يرجى تحديد العام الدراسي')
        return redirect('students:results_list')
    
    return export_comprehensive_results(level, academic_year)

# Student Promotion Views
@login_required
def promote_students(request):
    if request.method == 'POST':
        form = StudentPromotionForm(request.POST)
        if form.is_valid():
            from_level = form.cleaned_data['from_level']
            to_level = form.cleaned_data['to_level']
            academic_year = form.cleaned_data['academic_year']

            # الحصول على الطلاب المؤهلين للترقية
            results = StudentResult.objects.filter(
                level=from_level,
                academic_year=academic_year
            ).exclude(result='باقي للإعادة')

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
