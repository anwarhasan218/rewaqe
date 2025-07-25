import pandas as pd

# إنشاء إطار بيانات فارغ مع الأعمدة المطلوبة
df = pd.DataFrame(columns=['code', 'score'])

# إضافة بعض البيانات التوضيحية
data = [
    {'code': '1001', 'score': 85},
    {'code': '1002', 'score': 90},
    {'code': '1003', 'score': 75}
]

df = pd.concat([df, pd.DataFrame(data)], ignore_index=True)

# حفظ الملف
df.to_excel('staticfiles/examples/results_template.xlsx', index=False)

print("تم إنشاء ملف النموذج بنجاح!")