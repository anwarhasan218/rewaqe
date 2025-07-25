from django.db import models
from django.utils.translation import gettext_lazy as _
from .models_users import CustomUser

class Batch(models.Model):
    """الدفعة الدراسية"""
    name = models.CharField(_('اسم الدفعة'), max_length=100, unique=True)
    start_date = models.DateField(_('تاريخ البداية'), null=True, blank=True)
    end_date = models.DateField(_('تاريخ النهاية'), null=True, blank=True)
    is_active = models.BooleanField(_('نشطة'), default=True)
    created_at = models.DateTimeField(_('تاريخ الإنشاء'), auto_now_add=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = _('الدفعة')
        verbose_name_plural = _('الدفعات')
        ordering = ['-created_at']

class Stage(models.Model):
    """مرحلة دراسية"""
    STAGE_CHOICES = [
        ('تمهيدية', 'تمهيدية'),
        ('متوسطة', 'متوسطة'),
        ('تخصصية فقه واصوله', 'تخصصية فقه واصوله'),
        ('تخصصية تفسير وحديث', 'تخصصية تفسير وحديث'),
        ('تخصصية لغة عربية', 'تخصصية لغة عربية'),
        ('تخصصية عقيدة', 'تخصصية عقيدة'),
        ('شعبة عامة متقدمة', 'شعبة عامة متقدمة'),
    ]
    name = models.CharField(_('المرحلة'), max_length=50, choices=STAGE_CHOICES)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = _('المرحلة الدراسية')
        verbose_name_plural = _('المراحل الدراسية')

class Level(models.Model):
    """المستوى الدراسي"""
    LEVEL_CHOICES = [
        ('المستوى الأول', 'المستوى الأول'),
        ('المستوى الثاني', 'المستوى الثاني'),
        ('المستوى الثالث', 'المستوى الثالث'),
        ('المستوى الرابع', 'المستوى الرابع'),
    ]

    stage = models.ForeignKey(Stage, on_delete=models.CASCADE, verbose_name=_('المرحلة'))
    name = models.CharField(_('اسم المستوى'), max_length=50, choices=LEVEL_CHOICES)

    def __str__(self):
        return f"{self.stage} - {self.name}"

    class Meta:
        verbose_name = _('المستوى الدراسي')
        verbose_name_plural = _('المستويات الدراسية')

class Course(models.Model):
    """المادة الدراسية"""
    name = models.CharField(_('اسم المادة'), max_length=100)
    level = models.ForeignKey(Level, on_delete=models.CASCADE, related_name='courses', verbose_name=_('المستوى'))
    max_score = models.PositiveIntegerField(_('الدرجة النهائية'), default=100)
    pass_score = models.PositiveIntegerField(_('درجة النجاح'), default=50)

    def __str__(self):
        return f"{self.name} - {self.level}"

    class Meta:
        verbose_name = _('المادة الدراسية')
        verbose_name_plural = _('المواد الدراسية')

class Student(models.Model):
    """الطالب"""
    GENDER_CHOICES = [
        ('ذكر', 'ذكر'),
        ('أنثى', 'أنثى'),
    ]
    ENROLLMENT_CHOICES = [
        ('مستجد', 'مستجد'),
        ('منقول', 'منقول'),
        ('منقول بمواد', 'منقول بمواد'),
        ('باقي للإعادة', 'باقي للإعادة'),
    ]
    STUDY_TYPE_CHOICES = [
        ('مباشر', 'مباشر'),
        ('عن بعد', 'عن بعد'),
    ]
    VISION_STATUS_CHOICES = [
        ('مبصر', 'مبصر'),
        ('كفيف', 'كفيف'),
    ]
    MADHHAB_CHOICES = [
        ('حنفي', 'حنفي'),
        ('مالكي', 'مالكي'),
        ('شافعي', 'شافعي'),
        ('حنبلي', 'حنبلي'),
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

    code = models.CharField(_('الكود'), max_length=20, unique=True)
    previous_seat_number = models.CharField(_('رقم الجلوس السابق'), max_length=20, blank=True, null=True)
    current_seat_number = models.CharField(_('رقم الجلوس الحالي'), max_length=20)
    full_name = models.CharField(_('الاسم رباعي'), max_length=100)
    gender = models.CharField(_('النوع'), max_length=5, choices=GENDER_CHOICES)
    national_id = models.CharField(_('الرقم القومي'), max_length=14, unique=True)
    phone_number = models.CharField(_('رقم التليفون'), max_length=20)
    governorate = models.CharField(_('المحافظة'), max_length=20, choices=GOVERNORATE_CHOICES, default='القاهرة')
    vision_status = models.CharField(_('حالة البصر'), max_length=10, choices=VISION_STATUS_CHOICES)
    special_needs = models.BooleanField(_('من ذوي الهمم'), default=False)
    level = models.ForeignKey(Level, on_delete=models.CASCADE, verbose_name=_('المستوى'))
    batch = models.ForeignKey(Batch, on_delete=models.CASCADE, verbose_name=_('الدفعة'), null=True, blank=True)
    madhhab = models.CharField(_('المذهب الفقهي'), max_length=10, choices=MADHHAB_CHOICES)
    study_type = models.CharField(_('نوع الدراسة'), max_length=10, choices=STUDY_TYPE_CHOICES)
    enrollment_status = models.CharField(_('حالة القيد'), max_length=20, choices=ENROLLMENT_CHOICES)

    def __str__(self):
        return f"{self.full_name} - {self.code}"

    class Meta:
        verbose_name = _('الطالب')
        verbose_name_plural = _('الطلاب')

# تم حذف نموذج CourseResult واستبداله بحقل course_scores في StudentResult

class StudentResult(models.Model):
    """نتيجة الطالب الشاملة"""
    RESULT_CHOICES = [
        ('ناجح', 'ناجح'),
        ('ناجح ومنقول', 'ناجح ومنقول'),
        ('ناجح بمواد', 'ناجح بمواد'),
        ('منقول بمواد', 'منقول بمواد'),
        ('راسب', 'راسب'),
        ('باقي للإعادة', 'باقي للإعادة'),
        ('غائب', 'غائب'),
    ]

    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='final_results', verbose_name=_('الطالب'))
    level = models.ForeignKey(Level, on_delete=models.CASCADE, verbose_name=_('المستوى'))
    batch = models.ForeignKey(Batch, on_delete=models.CASCADE, verbose_name=_('الدفعة'))
    result = models.CharField(_('النتيجة'), max_length=20, choices=RESULT_CHOICES)
    failed_courses = models.ManyToManyField(Course, blank=True, verbose_name=_('المواد المتبقية'))
    academic_year = models.CharField(_('العام الدراسي'), max_length=20)
    total_score = models.PositiveIntegerField(_('المجموع الكلي'), default=0)
    result_date = models.DateTimeField(_('تاريخ النتيجة'), null=True, blank=True)

    # حفظ درجات المواد في حقل JSON
    course_scores = models.JSONField(_('درجات المواد'), default=dict, blank=True)
    # مثال: {'1': 85, '2': 90, '3': 75} حيث 1,2,3 هي IDs المواد

    def get_course_score(self, course_id):
        """الحصول على درجة مادة معينة"""
        return self.course_scores.get(str(course_id), None)

    def set_course_score(self, course_id, score):
        """تحديد درجة مادة معينة"""
        self.course_scores[str(course_id)] = score
        self.save()

    def get_all_scores(self):
        """الحصول على جميع الدرجات مع أسماء المواد"""
        scores = []
        for course_id, score in self.course_scores.items():
            try:
                course = Course.objects.get(id=course_id)
                scores.append({
                    'course': course,
                    'score': score,
                    'passed': score >= course.pass_score if score is not None else False
                })
            except Course.DoesNotExist:
                continue
        return scores

    def calculate_total_score(self):
        """حساب المجموع الكلي"""
        total = 0
        for score in self.course_scores.values():
            if score is not None:
                total += score
        return total

    def get_failed_courses_list(self):
        """الحصول على قائمة المواد الراسب فيها"""
        failed = []
        for course_id, score in self.course_scores.items():
            try:
                course = Course.objects.get(id=course_id)
                if score is not None and score < course.pass_score:
                    failed.append(course)
            except Course.DoesNotExist:
                continue
        return failed

    @property
    def percentage(self):
        """حساب النسبة المئوية لمجموع درجات الطالب"""
        from .models import Course  # تجنب الاستيراد الدائري
        courses = Course.objects.filter(level=self.level)
        max_total_score = sum(course.max_score for course in courses)
        if max_total_score > 0:
            return round((self.total_score / max_total_score) * 100, 1)
        return 0

    def __str__(self):
        return f"{self.student.full_name} - {self.level} - {self.result}"

    class Meta:
        verbose_name = _('النتيجة النهائية')
        verbose_name_plural = _('النتائج النهائية')
        unique_together = ['student', 'level', 'batch', 'academic_year']
