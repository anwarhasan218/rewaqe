from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Batch, Stage, Level, Course, Student, StudentResult
from .models_users import CustomUser
from .forms_users import CustomUserCreationForm, CustomUserChangeForm

@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    add_form = CustomUserCreationForm
    form = CustomUserChangeForm
    model = CustomUser
    list_display = ('username', 'email', 'first_name', 'last_name', 'role', 'governorate', 'is_staff')
    list_filter = ('role', 'is_staff', 'is_superuser', 'groups')
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('المعلومات الشخصية', {'fields': ('first_name', 'last_name', 'email')}),
        ('الصلاحيات', {'fields': ('role', 'governorate', 'is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'password1', 'password2', 'first_name', 'last_name', 'email', 'role', 'governorate'),
        }),
    )
    search_fields = ('username', 'first_name', 'last_name', 'email')
    ordering = ('username',)

@admin.register(Batch)
class BatchAdmin(admin.ModelAdmin):
    list_display = ('name', 'start_date', 'end_date', 'is_active', 'created_at')
    list_filter = ('is_active', 'created_at')
    search_fields = ('name',)
    list_editable = ('is_active',)

@admin.register(Stage)
class StageAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)

@admin.register(Level)
class LevelAdmin(admin.ModelAdmin):
    list_display = ('name', 'stage')
    list_filter = ('stage',)
    search_fields = ('name',)

@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ('name', 'level', 'max_score', 'pass_score')
    list_filter = ('level__stage', 'level')
    search_fields = ('name',)

@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ('code', 'full_name', 'current_seat_number', 'level', 'enrollment_status')
    list_filter = ('level__stage', 'level', 'gender', 'enrollment_status', 'study_type', 'vision_status', 'special_needs')
    search_fields = ('code', 'full_name', 'current_seat_number', 'previous_seat_number', 'national_id')
    fieldsets = (
        ('البيانات الأساسية', {
            'fields': ('code', 'full_name', 'gender', 'national_id', 'phone_number')
        }),
        ('بيانات الدراسة', {
            'fields': ('level', 'previous_seat_number', 'current_seat_number', 'enrollment_status', 'study_type', 'madhhab')
        }),
        ('بيانات خاصة', {
            'fields': ('vision_status', 'special_needs')
        }),
    )

# تم حذف CourseResult من النظام

@admin.register(StudentResult)
class StudentResultAdmin(admin.ModelAdmin):
    list_display = ('student', 'level', 'batch', 'result')
    list_filter = ('batch', 'level', 'result')
    search_fields = ('student__full_name', 'student__code')
    filter_horizontal = ('failed_courses',)
