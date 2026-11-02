from django.db import models


class Batch(models.Model):
    """
    Represents a tuition batch (e.g. 'Class 10 Maths – Evening').
    A batch has many students (reverse relation: batch.students).
    """
    name = models.CharField(max_length=100, help_text="e.g. Class 10 Maths")
    subject = models.CharField(max_length=100)
    schedule = models.CharField(
        max_length=200,
        help_text="e.g. Mon / Wed / Fri  6:00 PM – 7:30 PM"
    )
    monthly_fee = models.DecimalField(max_digits=8, decimal_places=2)
    start_date = models.DateField()
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Batch'
        verbose_name_plural = 'Batches'

    def __str__(self):
        return f"{self.name} ({self.subject})"

    @property
    def student_count(self):
        return self.students.count()


class Student(models.Model):
    """
    Represents an enrolled student.
    Linked to a Batch via FK (nullable so we can delete a batch safely).
    """
    name = models.CharField(max_length=200)
    email = models.EmailField(blank=True)
    phone = models.CharField(max_length=15)
    address = models.TextField(blank=True)
    batch = models.ForeignKey(
        Batch,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='students'
    )
    enrollment_date = models.DateField(auto_now_add=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name
