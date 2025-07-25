import os
import django
from django.utils import timezone

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'azhar_student_management.settings')
django.setup()

from students.models import Student, Batch

def assign_students_to_batch(batch_name="فبراير 2025"):
    """
    Assigns all existing students to a specific batch.
    Creates the batch if it doesn't exist.
    """
    try:
        # Get or create the batch
        batch, created = Batch.objects.get_or_create(
            name=batch_name,
            defaults={
                'start_date': timezone.now().date(),
                'is_active': True
            }
        )

        if created:
            print(f"تم إنشاء دفعة جديدة: '{batch_name}'")
        else:
            print(f"تم العثور على دفعة حالية: '{batch_name}'")

        # Get all students that are not already in the target batch
        students_to_update = Student.objects.exclude(batch=batch)
        
        if not students_to_update.exists():
            print("كل الطلاب الحاليين مضافون بالفعل إلى هذه الدفعة.")
            return

        # Assign students to the batch
        updated_count = students_to_update.update(batch=batch)

        print(f"تم تحديث {updated_count} طالبًا بنجاح وإضافتهم إلى دفعة '{batch_name}'.")

    except Exception as e:
        print(f"حدث خطأ: {e}")

if __name__ == "__main__":
    assign_students_to_batch() 