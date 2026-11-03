import uuid
from datetime import date
from decimal import Decimal
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
        help_text="e.g. Mon / Wed / Fri  6:00 PM - 7:30 PM"
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

    @property
    def total_paid(self):
        """Sum of all payments made by this student."""
        total = self.payments.aggregate(models.Sum('amount'))['amount__sum']
        return total if total is not None else Decimal('0.00')

    @property
    def months_enrolled(self):
        """Calculates number of months since enrollment (minimum 1)."""
        today = date.today()
        enrolled = self.enrollment_date or today
        diff = (today.year - enrolled.year) * 12 + (today.month - enrolled.month) + 1
        return max(1, diff)

    @property
    def total_fee_expected(self):
        """Total expected fee = months enrolled * batch monthly fee."""
        if self.batch and self.batch.monthly_fee:
            return Decimal(self.months_enrolled) * self.batch.monthly_fee
        return Decimal('0.00')

    @property
    def pending_balance(self):
        """Expected fee minus total paid. Positive = due, negative = advance."""
        return self.total_fee_expected - self.total_paid

    @property
    def is_fully_paid(self):
        return self.pending_balance <= Decimal('0.00')


class Attendance(models.Model):
    """
    Records whether a student was present or absent on a specific date.
    unique_together ensures one record per student per day.
    """
    STATUS_PRESENT = 'P'
    STATUS_ABSENT  = 'A'
    STATUS_CHOICES = [
        (STATUS_PRESENT, 'Present'),
        (STATUS_ABSENT,  'Absent'),
    ]

    student = models.ForeignKey(
        Student,
        on_delete=models.CASCADE,
        related_name='attendances'
    )
    batch = models.ForeignKey(
        Batch,
        on_delete=models.CASCADE,
        related_name='attendances'
    )
    date   = models.DateField()
    status = models.CharField(max_length=1, choices=STATUS_CHOICES, default=STATUS_PRESENT)
    marked_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('student', 'date')
        ordering = ['-date', 'student__name']

    def __str__(self):
        return f"{self.student.name} | {self.date} | {self.get_status_display()}"

    @property
    def is_present(self):
        return self.status == self.STATUS_PRESENT


class Payment(models.Model):
    """
    Records a fee payment made by a student.
    Generates a unique receipt number automatically.
    """
    MODE_CASH   = 'CASH'
    MODE_UPI    = 'UPI'
    MODE_BANK   = 'BANK'
    MODE_CHEQUE = 'CHEQUE'
    MODE_CARD   = 'CARD'

    MODE_CHOICES = [
        (MODE_CASH,   'Cash'),
        (MODE_UPI,    'UPI (GPay / PhonePe / Paytm)'),
        (MODE_BANK,   'Bank Transfer (NEFT / IMPS)'),
        (MODE_CHEQUE, 'Cheque'),
        (MODE_CARD,   'Debit / Credit Card'),
    ]

    receipt_no = models.CharField(max_length=32, unique=True, editable=False)
    student = models.ForeignKey(
        Student,
        on_delete=models.CASCADE,
        related_name='payments'
    )
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    date = models.DateField(default=date.today)
    mode = models.CharField(max_length=10, choices=MODE_CHOICES, default=MODE_CASH)
    reference = models.CharField(
        max_length=100,
        blank=True,
        help_text="e.g. UTR / UPI Ref / Cheque No."
    )
    remarks = models.CharField(
        max_length=255,
        blank=True,
        help_text="e.g. November fee installment"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-date', '-created_at']

    def save(self, *args, **kwargs):
        if not self.receipt_no:
            date_prefix = (self.date or date.today()).strftime('%Y%m')
            random_suffix = uuid.uuid4().hex[:6].upper()
            self.receipt_no = f"TP-{date_prefix}-{random_suffix}"
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.receipt_no} — {self.student.name} (Rs. {self.amount})"
