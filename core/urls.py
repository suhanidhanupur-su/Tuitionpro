from django.urls import path
from . import views

app_name = 'core'

urlpatterns = [
    # Dashboard
    path('', views.dashboard, name='dashboard'),

    # Batches
    path('batches/',                 views.batch_list,   name='batch_list'),
    path('batches/add/',             views.batch_create, name='batch_create'),
    path('batches/<int:pk>/edit/',   views.batch_edit,   name='batch_edit'),
    path('batches/<int:pk>/delete/', views.batch_delete, name='batch_delete'),

    # Students
    path('students/',                  views.student_list,   name='student_list'),
    path('students/add/',              views.student_create, name='student_create'),
    path('students/<int:pk>/edit/',    views.student_edit,   name='student_edit'),
    path('students/<int:pk>/delete/',  views.student_delete, name='student_delete'),
    path('students/<int:pk>/ledger/',  views.student_ledger, name='student_ledger'),

    # Attendance
    path('attendance/',         views.attendance_mark,   name='attendance_mark'),
    path('attendance/report/',  views.attendance_report, name='attendance_report'),

    # Fees & Payments
    path('fees/',                 views.fee_dashboard,       name='fee_dashboard'),
    path('payments/add/',         views.payment_create,      name='payment_create'),
    path('payments/<int:pk>/',    views.payment_detail,      name='payment_detail'),
    path('payments/<int:pk>/pdf/', views.payment_receipt_pdf, name='payment_receipt_pdf'),
]
