-- إنشاء جدول الدفعات
CREATE TABLE IF NOT EXISTS "students_batch" (
    "id" integer NOT NULL PRIMARY KEY AUTOINCREMENT,
    "name" varchar(100) NOT NULL UNIQUE,
    "start_date" date,
    "end_date" date,
    "is_active" bool NOT NULL,
    "created_at" datetime NOT NULL
);

-- إدراج دفعة أغسطس 2025
INSERT OR IGNORE INTO "students_batch" (name, is_active, created_at) 
VALUES ('أغسطس 2025', 1, datetime('now'));

-- إضافة عمود الدفعة للطلاب (إذا لم يكن موجوداً)
ALTER TABLE "students_student" ADD COLUMN "batch_id" integer;

-- تحديث الطلاب الموجودين لربطهم بدفعة أغسطس 2025
UPDATE "students_student" 
SET "batch_id" = (SELECT id FROM "students_batch" WHERE name = 'أغسطس 2025')
WHERE "batch_id" IS NULL;

-- حذف النتائج القديمة
DELETE FROM "students_courseresult";
DELETE FROM "students_studentresult";

-- إضافة عمود الدفعة لنتائج المواد
ALTER TABLE "students_courseresult" ADD COLUMN "batch_id" integer;

-- إضافة عمود الدفعة للنتائج النهائية  
ALTER TABLE "students_studentresult" ADD COLUMN "batch_id" integer;

-- حذف العمود القديم academic_year من CourseResult
-- SQLite لا يدعم DROP COLUMN مباشرة، لذا سنتركه

-- حذف العمود القديم academic_year من StudentResult
-- SQLite لا يدعم DROP COLUMN مباشرة، لذا سنتركه
