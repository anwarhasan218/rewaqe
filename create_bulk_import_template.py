import pandas as pd
import os

# إنشاء مجلد examples إذا لم يكن موجودًا
os.makedirs('staticfiles/examples', exist_ok=True)

# قائمة المواد الافتراضية (يمكن تعديلها حسب المواد الفعلية في النظام)
subjects = ['القرآن الكريم', 'التفسير', 'الحديث', 'الفقه', 'أصول الفقه', 'النحو', 'الصرف', 'البلاغة']

# إنشاء قائمة بأسماء الأعمدة
columns = ['كود_الطالب', 'اسم_الطالب'] + subjects

# إنشاء DataFrame فارغ مع بيانات توضيحية
data = [
    ['ST001', 'أحمد محمد علي', 85, 90, 88, 92, 87, 94, 89, 91],
    ['ST002', 'محمود أحمد حسن', 82, 88, 90, 85, 89, 87, 92, 86],
    ['ST003', 'فاطمة محمد سعيد', 90, 94, 87, 89, 92, 88, 85, 93]
]

# إنشاء DataFrame
df = pd.DataFrame(data, columns=columns)

# حفظ الملف
output_path = 'staticfiles/examples/bulk_import_template.xlsx'
df.to_excel(output_path, index=False)

print(f"تم إنشاء ملف القالب بنجاح في: {output_path}")

# نسخ الملف إلى مجلد static أيضًا
os.makedirs('static/examples', exist_ok=True)
df.to_excel('static/examples/bulk_import_template.xlsx', index=False)
print("تم نسخ الملف إلى مجلد static/examples أيضًا")