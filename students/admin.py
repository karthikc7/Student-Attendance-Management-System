from django.contrib import admin
from .models import Student, Attendance

@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ['student_id', 'name', 'father_name', 'student_class', 'section', 'contact_number']
    list_filter = ['student_class', 'section']
    search_fields = ['name', 'student_id', 'father_name', 'mother_name']
    ordering = ['student_class', 'name']

@admin.register(Attendance)
class AttendanceAdmin(admin.ModelAdmin):
    list_display = ['student', 'date', 'is_present']
    list_filter = ['date', 'is_present', 'student__student_class']
    search_fields = ['student__name', 'student__student_id']
    date_hierarchy = 'date'
    ordering = ['-date', 'student__name']
