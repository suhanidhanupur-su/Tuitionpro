from django.urls import path
from . import views

app_name = 'core'

urlpatterns = [
    # Dashboard
    path('', views.dashboard, name='dashboard'),

    # Batches
    path('batches/',              views.batch_list,   name='batch_list'),
    path('batches/add/',          views.batch_create, name='batch_create'),
    path('batches/<int:pk>/edit/', views.batch_edit,  name='batch_edit'),
    path('batches/<int:pk>/delete/', views.batch_delete, name='batch_delete'),

    # Students
    path('students/',               views.student_list,   name='student_list'),
    path('students/add/',           views.student_create, name='student_create'),
    path('students/<int:pk>/edit/', views.student_edit,   name='student_edit'),
    path('students/<int:pk>/delete/', views.student_delete, name='student_delete'),
]
