from django.contrib import admin
from .models import Batch, Student, Attendance, Payment


@admin.register(Batch)
class BatchAdmin(admin.ModelAdmin):
    list_display  = ['name', 'subject', 'monthly_fee', 'start_date', 'student_count', 'is_active']
    list_filter   = ['is_active', 'subject']
    search_fields = ['name', 'subject']
    ordering      = ['-created_at']


@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display  = ['name', 'phone', 'email', 'batch', 'enrollment_date', 'is_active']
    list_filter   = ['is_active', 'batch']
    search_fields = ['name', 'phone', 'email']
    ordering      = ['name']


@admin.register(Attendance)
class AttendanceAdmin(admin.ModelAdmin):
    list_display  = ['student', 'batch', 'date', 'status', 'marked_at']
    list_filter   = ['status', 'batch', 'date']
    search_fields = ['student__name', 'batch__name']
    ordering      = ['-date', 'student__name']


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display  = ['receipt_no', 'student', 'amount', 'date', 'mode', 'reference', 'created_at']
    list_filter   = ['mode', 'date']
    search_fields = ['receipt_no', 'student__name', 'reference']
    ordering      = ['-date', '-created_at']
