# خطوات استضافة الموقع على Ubuntu Server 2024

## 1. إعداد الخادم

### تثبيت المتطلبات الأساسية
```bash
sudo apt update
sudo apt upgrade -y
sudo apt install python3 python3-pip python3-venv nginx postgresql postgresql-contrib -y
```

## 2. إعداد قاعدة البيانات

### إنشاء قاعدة البيانات وحساب المستخدم
```bash
sudo -u postgres psql
CREATE DATABASE azhar_db;
CREATE USER azhar_user WITH PASSWORD 'secure_password';
ALTER ROLE azhar_user SET client_encoding TO 'utf8';
ALTER ROLE azhar_user SET default_transaction_isolation TO 'read committed';
ALTER ROLE azhar_user SET timezone TO 'UTC';
GRANT ALL PRIVILEGES ON DATABASE azhar_db TO azhar_user;
\q
```

## 3. إعداد المشروع

### إنشاء وتفعيل البيئة الافتراضية
```bash
python3 -m venv venv
source venv/bin/activate
```

### تثبيت المتطلبات
```bash
pip install -r requirements.txt
pip install gunicorn psycopg2-binary
```

### تعديل إعدادات Django
قم بتعديل ملف `azhar_student_management/settings.py`:

```python
DEBUG = False
ALLOWED_HOSTS = ['your_domain_or_ip']

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'azhar_db',
        'USER': 'azhar_user',
        'PASSWORD': 'secure_password',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}
```

### جمع الملفات الثابتة وتطبيق الترحيلات
```bash
python manage.py collectstatic
python manage.py migrate
```

## 4. إعداد Gunicorn

### إنشاء ملف خدمة النظام
```bash
sudo nano /etc/systemd/system/gunicorn.service
```

أضف المحتوى التالي:
```ini
[Unit]
Description=gunicorn daemon
After=network.target

[Service]
User=your_user
Group=www-data
WorkingDirectory=/path/to/your/project
ExecStart=/path/to/your/project/venv/bin/gunicorn --workers 3 --bind unix:/path/to/your/project/azhar_student_management.sock azhar_student_management.wsgi:application

[Install]
WantedBy=multi-user.target
```

### تفعيل وتشغيل الخدمة
```bash
sudo systemctl start gunicorn
sudo systemctl enable gunicorn
```

## 5. إعداد Nginx

### إنشاء ملف تكوين الموقع
```bash
sudo nano /etc/nginx/sites-available/azhar_student_management
```

أضف المحتوى التالي:
```nginx
server {
    listen 80;
    server_name your_domain_or_ip;

    location = /favicon.ico { access_log off; log_not_found off; }
    
    location /static/ {
        root /path/to/your/project;
    }

    location /media/ {
        root /path/to/your/project;
    }

    location / {
        include proxy_params;
        proxy_pass http://unix:/path/to/your/project/azhar_student_management.sock;
    }
}
```

### تفعيل تكوين الموقع
```bash
sudo ln -s /etc/nginx/sites-available/azhar_student_management /etc/nginx/sites-enabled
sudo nginx -t
sudo systemctl restart nginx
```

## 6. إعداد جدار الحماية

```bash
sudo ufw allow 'Nginx Full'
sudo ufw allow ssh
sudo ufw enable
```

## 7. إعداد SSL (اختياري ولكن موصى به)

### تثبيت Certbot
```bash
sudo apt install certbot python3-certbot-nginx -y
sudo certbot --nginx -d your_domain
```

## ملاحظات هامة

1. استبدل `your_domain_or_ip` بعنوان IP الخاص بالخادم أو اسم النطاق الخاص بك
2. استبدل `your_user` باسم المستخدم الخاص بك على النظام
3. استبدل `secure_password` بكلمة مرور قوية
4. استبدل `/path/to/your/project` بالمسار الكامل لمجلد المشروع
5. تأكد من تغيير أذونات الملفات والمجلدات بشكل صحيح
6. احتفظ بنسخة احتياطية من قاعدة البيانات بشكل منتظم

## الأمان

1. تأكد من تحديث النظام بانتظام
2. استخدم كلمات مرور قوية
3. قم بتفعيل SSL
4. قم بتكوين جدار الحماية بشكل صحيح
5. قم بتقييد الوصول إلى قاعدة البيانات
6. احتفظ بسجلات النظام ومراقبتها