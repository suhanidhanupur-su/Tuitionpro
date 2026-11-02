from django.contrib import admin
from .models import Batch, Student


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
