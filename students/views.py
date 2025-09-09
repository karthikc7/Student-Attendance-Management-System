from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.contrib import messages
from django.db.models import Q
from datetime import datetime, date
import json
from .models import Student, Attendance

def index(request):
    """Main dashboard view"""
    return render(request, 'students/index.html')

def student_list(request):
    """Display all students"""
    students = Student.objects.all().order_by('student_class', 'name')
    return render(request, 'students/student_list.html', {'students': students})

def add_student(request):
    """Add new student"""
    if request.method == 'POST':
        try:
            # Generate student ID
            student_class = int(request.POST['student_class'])
            existing_count = Student.objects.filter(student_class=student_class).count()
            student_id = f"STU{student_class:02d}{existing_count + 1:03d}"
            
            student = Student.objects.create(
                student_id=student_id,
                name=request.POST['name'],
                father_name=request.POST['father_name'],
                mother_name=request.POST['mother_name'],
                student_class=student_class,
                section=request.POST.get('section', 'A'),
                date_of_birth=request.POST['date_of_birth'],
                contact_number=request.POST.get('contact_number', ''),
                address=request.POST.get('address', '')
            )
            messages.success(request, f'Student {student.name} added successfully with ID: {student_id}')
            return redirect('student_list')
        except Exception as e:
            messages.error(request, f'Error adding student: {str(e)}')
    
    return render(request, 'students/add_student.html')

def attendance_view(request):
    """Daily attendance marking"""
    selected_date = request.GET.get('date', date.today().strftime('%Y-%m-%d'))
    selected_class = request.GET.get('class', '1')
    
    students = Student.objects.filter(student_class=selected_class).order_by('name')
    
    # Get existing attendance for the selected date
    attendance_records = {}
    if students:
        attendances = Attendance.objects.filter(
            student__in=students,
            date=selected_date
        )
        attendance_records = {att.student.id: att.is_present for att in attendances}
    
    context = {
        'students': students,
        'selected_date': selected_date,
        'selected_class': selected_class,
        'attendance_records': attendance_records,
        'classes': range(1, 11)
    }
    return render(request, 'students/attendance.html', context)

@csrf_exempt
@require_http_methods(["POST"])
def save_attendance(request):
    """Save attendance data"""
    try:
        data = json.loads(request.body)
        attendance_date = data.get('date')
        attendance_data = data.get('attendance', {})
        
        for student_id, is_present in attendance_data.items():
            student = Student.objects.get(id=student_id)
            attendance, created = Attendance.objects.get_or_create(
                student=student,
                date=attendance_date,
                defaults={'is_present': is_present}
            )
            if not created:
                attendance.is_present = is_present
                attendance.save()
        
        return JsonResponse({'success': True, 'message': 'Attendance saved successfully'})
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)})

def student_report(request, student_id):
    """Individual student attendance report"""
    student = get_object_or_404(Student, id=student_id)
    
    # Get attendance records
    attendances = Attendance.objects.filter(student=student).order_by('-date')
    
    # Calculate statistics
    total_days = attendances.count()
    present_days = attendances.filter(is_present=True).count()
    absent_days = total_days - present_days
    attendance_percentage = (present_days / total_days * 100) if total_days > 0 else 0
    
    context = {
        'student': student,
        'attendances': attendances,
        'total_days': total_days,
        'present_days': present_days,
        'absent_days': absent_days,
        'attendance_percentage': round(attendance_percentage, 2)
    }
    return render(request, 'students/student_report.html', context)

def class_report(request):
    """Class-wise attendance report"""
    selected_class = request.GET.get('class', '1')
    selected_date = request.GET.get('date', date.today().strftime('%Y-%m-%d'))
    
    students = Student.objects.filter(student_class=selected_class).order_by('name')
    
    # Get attendance for selected date
    attendance_data = []
    for student in students:
        try:
            attendance = Attendance.objects.get(student=student, date=selected_date)
            status = 'Present' if attendance.is_present else 'Absent'
        except Attendance.DoesNotExist:
            status = 'Not Marked'
        
        attendance_data.append({
            'student': student,
            'status': status
        })
    
    # Calculate class statistics
    total_students = len(attendance_data)
    present_count = sum(1 for item in attendance_data if item['status'] == 'Present')
    absent_count = sum(1 for item in attendance_data if item['status'] == 'Absent')
    not_marked_count = sum(1 for item in attendance_data if item['status'] == 'Not Marked')
    
    context = {
        'selected_class': selected_class,
        'selected_date': selected_date,
        'attendance_data': attendance_data,
        'total_students': total_students,
        'present_count': present_count,
        'absent_count': absent_count,
        'not_marked_count': not_marked_count,
        'classes': range(1, 11)
    }
    return render(request, 'students/class_report.html', context)

def search_students(request):
    """Search students by name or ID"""
    query = request.GET.get('q', '')
    students = []
    
    if query:
        students = Student.objects.filter(
            Q(name__icontains=query) | 
            Q(student_id__icontains=query)
        ).order_by('student_class', 'name')
    
    return render(request, 'students/search_results.html', {
        'students': students,
        'query': query
    })
