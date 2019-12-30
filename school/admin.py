from django.contrib import admin
from django.contrib.auth.models import Permission
from school.models import Subject, Teacher, Student, Classroom

admin.site.register(Classroom)
admin.site.register(Subject)
admin.site.register(Teacher)
admin.site.register(Student)
admin.site.register(Permission)