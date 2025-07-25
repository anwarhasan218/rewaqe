from django.db import models
from django.contrib.auth.models import AbstractUser, Group, Permission
from django.utils.translation import gettext_lazy as _

class CustomUser(AbstractUser):
    """نموذج المستخدم المخصص"""
    ROLE_CHOICES = [
        ('admin', 'مدير النظام'),
        ('supervisor', 'مشرف محافظة')
    ]
    GOVERNORATE_CHOICES = [
        ('القاهرة', 'القاهرة'),
        ('الجيزة', 'الجيزة'),
        ('الإسكندرية', 'الإسكندرية'),
        ('الدقهلية', 'الدقهلية'),
        ('البحر الأحمر', 'البحر الأحمر'),
        ('البحيرة', 'البحيرة'),
        ('الفيوم', 'الفيوم'),
        ('الغربية', 'الغربية'),
        ('الإسماعيلية', 'الإسماعيلية'),
        ('المنوفية', 'المنوفية'),
        ('المنيا', 'المنيا'),
        ('القليوبية', 'القليوبية'),
        ('الوادي الجديد', 'الوادي الجديد'),
        ('السويس', 'السويس'),
        ('اسوان', 'اسوان'),
        ('اسيوط', 'اسيوط'),
        ('بني سويف', 'بني سويف'),
        ('بورسعيد', 'بورسعيد'),
        ('دمياط', 'دمياط'),
        ('الشرقية', 'الشرقية'),
        ('جنوب سيناء', 'جنوب سيناء'),
        ('كفر الشيخ', 'كفر الشيخ'),
        ('مطروح', 'مطروح'),
        ('الأقصر', 'الأقصر'),
        ('قنا', 'قنا'),
        ('شمال سيناء', 'شمال سيناء'),
        ('سوهاج', 'سوهاج'),
        ('أخرى', 'أخرى'),
    ]
    role = models.CharField(_('الدور'), max_length=20, choices=ROLE_CHOICES)
    governorate = models.CharField(_('المحافظة'), max_length=50, choices=GOVERNORATE_CHOICES, blank=True, null=True)

    class Meta:
        verbose_name = _('مستخدم')
        verbose_name_plural = _('المستخدمين')
        permissions = [
            ('can_manage_all_students', 'يمكنه إدارة جميع الطلاب'),
            ('can_manage_governorate_students', 'يمكنه إدارة طلاب محافظته فقط'),
        ]

    def __str__(self):
        return f"{self.get_full_name()} - {self.get_role_display()}"

    def save(self, *args, **kwargs):
        is_new = self.pk is None
        super().save(*args, **kwargs)
        
        if is_new:
            if self.role == 'admin':
                admin_group, _ = Group.objects.get_or_create(name='Administrators')
                admin_permission = Permission.objects.get(codename='can_manage_all_students')
                admin_group.permissions.add(admin_permission)
                self.groups.add(admin_group)
            
            elif self.role == 'supervisor':
                supervisor_group, _ = Group.objects.get_or_create(name='Supervisors')
                supervisor_permission = Permission.objects.get(codename='can_manage_governorate_students')
                supervisor_group.permissions.add(supervisor_permission)
                self.groups.add(supervisor_group)