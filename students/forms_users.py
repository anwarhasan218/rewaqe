from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django.utils.translation import gettext_lazy as _
from .models_users import CustomUser
from .models import Student

class CustomUserCreationForm(UserCreationForm):
    """نموذج إنشاء مستخدم جديد"""
    class Meta(UserCreationForm.Meta):
        model = CustomUser
        fields = ('username', 'first_name', 'last_name', 'email', 'role', 'governorate')
        labels = {
            'username': _('اسم المستخدم'),
            'first_name': _('الاسم الأول'),
            'last_name': _('اسم العائلة'),
            'email': _('البريد الإلكتروني'),
            'role': _('الدور'),
            'governorate': _('المحافظة'),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['governorate'].required = False
        self.fields['governorate'].widget = forms.Select(choices=Student.GOVERNORATE_CHOICES)
        self.fields['governorate'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': _('اختر المحافظة')
        })

        # إظهار/إخفاء حقل المحافظة بناءً على الدور
        self.fields['role'].widget.attrs.update({
            'class': 'form-control',
            'onchange': 'toggleGovernorateField(this.value)'
        })

    def clean(self):
        cleaned_data = super().clean()
        role = cleaned_data.get('role')
        governorate = cleaned_data.get('governorate')

        if role == 'supervisor' and not governorate:
            raise forms.ValidationError(_('يجب تحديد المحافظة لمشرف المحافظة'))

        return cleaned_data

class CustomUserChangeForm(UserChangeForm):
    """نموذج تعديل بيانات المستخدم"""
    class Meta:
        model = CustomUser
        fields = ('username', 'first_name', 'last_name', 'email', 'role', 'governorate')
        labels = {
            'username': _('اسم المستخدم'),
            'first_name': _('الاسم الأول'),
            'last_name': _('اسم العائلة'),
            'email': _('البريد الإلكتروني'),
            'role': _('الدور'),
            'governorate': _('المحافظة'),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['governorate'].required = False
        self.fields['governorate'].widget = forms.Select(choices=Student.GOVERNORATE_CHOICES)
        self.fields['governorate'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': _('اختر المحافظة')
        })

        self.fields['role'].widget.attrs.update({
            'class': 'form-control',
            'onchange': 'toggleGovernorateField(this.value)'
        })

    def clean(self):
        cleaned_data = super().clean()
        role = cleaned_data.get('role')
        governorate = cleaned_data.get('governorate')

        if role == 'supervisor' and not governorate:
            raise forms.ValidationError(_('يجب تحديد المحافظة لمشرف المحافظة'))

        return cleaned_data