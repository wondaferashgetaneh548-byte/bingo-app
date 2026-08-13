from django.http import JsonResponse
from .models import Student

def add_and_list_students(request):
    if not Student.objects(name="Abebe Bikila"):
        Student(name="Abebe Bikila", age=25, department="Computer Science").save()

    students = Student.objects()

    data = []
    for s in students:
        data.append({
            'id': str(s.id),
            'name': s.name,
            'age': s.age,
            'department': s.department
        })

    return JsonResponse({'students': data})