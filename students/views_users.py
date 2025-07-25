from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.contrib import messages
from django.utils.translation import gettext_lazy as _
from .models_users import CustomUser
from .forms_users import CustomUserCreationForm, CustomUserChangeForm

class SuperUserRequiredMixin(UserPassesTestMixin):
    def test_func(self):
        return self.request.user.is_superuser

class UserListView(LoginRequiredMixin, SuperUserRequiredMixin, ListView):
    model = CustomUser
    template_name = 'students/user_list.html'
    context_object_name = 'users'

class UserCreateView(LoginRequiredMixin, SuperUserRequiredMixin, CreateView):
    model = CustomUser
    form_class = CustomUserCreationForm
    template_name = 'students/user_form.html'
    success_url = reverse_lazy('students:user_list')

    def form_valid(self, form):
        messages.success(self.request, _('تم إنشاء المستخدم بنجاح'))
        return super().form_valid(form)

class UserUpdateView(LoginRequiredMixin, SuperUserRequiredMixin, UpdateView):
    model = CustomUser
    form_class = CustomUserChangeForm
    template_name = 'students/user_form.html'
    success_url = reverse_lazy('students:user_list')

    def form_valid(self, form):
        messages.success(self.request, _('تم تحديث بيانات المستخدم بنجاح'))
        return super().form_valid(form)

class UserDeleteView(LoginRequiredMixin, SuperUserRequiredMixin, DeleteView):
    model = CustomUser
    template_name = 'students/user_confirm_delete.html'
    success_url = reverse_lazy('students:user_list')

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, _('تم حذف المستخدم بنجاح'))
        return super().delete(request, *args, **kwargs)