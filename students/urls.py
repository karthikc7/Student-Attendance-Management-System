from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('students/', views.student_list, name='student_list'),
    path('add-student/', views.add_student, name='add_student'),
    path('attendance/', views.attendance_view, name='attendance'),
    path('save-attendance/', views.save_attendance, name='save_attendance'),
    path('student-report/<int:student_id>/', views.student_report, name='student_report'),
    path('class-report/', views.class_report, name='class_report'),
    path('search/', views.search_students, name='search_students'),
]

