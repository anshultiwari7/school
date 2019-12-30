from django.shortcuts import render
# Create your views here.
from django.db import models
from django.views.generic.list import ListView
from django.views.generic.detail import DetailView
from datetime import datetime
from lendenclub.utils import CustomDecorators
from .models import Classroom, Subject, Student, Teacher


class ClassroomListView(ListView):
    model = Classroom
    paginate_by = 7
    template_name = 'classroom_list.html'

    def get_queryset(self, **kwargs):
        queryset = super().get_queryset()
        params = {}
        if self.request.GET.get('student'):
            try:
                params['subjects__id__in'] = Student.objects.get(
                    id=self.request.GET['student']).subjects.values_list('id')
            except:
                queryset = Classroom.objects.none()
        if params:
            return queryset.filter(**params).distinct()
        return queryset

    @CustomDecorators.paginate
    def get_context_data(self, **kwargs):
        context = self.__class__.context               
        return context


class StudentListView(ListView):
    model = Student
    paginate_by = 7
    template_name = 'student_list.html'

    def get_queryset(self, **kwargs):
        queryset = super().get_queryset()
        params = {}
        if self.request.GET.get('teacher'):
            try:
                params['subjects__id__in'] = Teacher.objects.get(
                    id=self.request.GET['teacher']
                    ).subjects.values_list('id')
            except Exception as e:
                queryset = Student.objects.none()

        if self.request.GET.get('classroom'):
            try:
                params['subjects__id__in'] = Classroom.objects.get(
                    id=self.request.GET['classroom']
                    ).subjects.values_list('id')
            except:
                queryset = Student.objects.none()
        if params:
            return queryset.filter(**params).distinct()
        return queryset

    @CustomDecorators.paginate
    def get_context_data(self, **kwargs):
        context = self.__class__.context
        if self.request.GET.get('teacher'):
            context['selected_teacher'] = Teacher.objects.get(
                pk=self.request.GET['teacher']
            )
        context['teacher_list'] = Teacher.objects.all()
        return context


class TeacherListView(ListView):
    model = Teacher
    paginate_by = 7
    template_name = 'teacher_list.html'

    def get_queryset(self, **kwargs):
        queryset = super().get_queryset()
        params = {}
        if self.request.GET.get('classroom'):
            try:
                params['subjects__id__in'] = Classroom.objects.get(
                    id=self.request.GET['classroom']).subjects.values_list('id')
            except:
                queryset = Teacher.objects.none()
        if self.request.GET.get('student'):
            if params.get('subjects__id__in'):
                params['subjects__id__in'] += Student.objects.get(
                    id=self.request.GET['student']).subjects.values_list('id')
            else:
                params['subjects__id__in'] = Student.objects.get(
                    id=self.request.GET['student']).subjects.values_list('id')
        if self.request.GET.get('salary_pm'):
            params['salary__gt'] = int(self.request.GET['salary_pm']) * 12
        if params:
            return queryset.filter(**params).distinct()
        return queryset

    @CustomDecorators.paginate
    def get_context_data(self, **kwargs):
        context = self.__class__.context
        if self.request.GET.get('salary_pm'):
            context['salary_check'] = True
        context['total_salary'] = round(sum(
            [object_.salary for object_ in context.get('object_list')]), 
            ndigits=2)
        context['total_salary_pm'] = round(float(
            context['total_salary'])/12, ndigits=2
            ) if context['total_salary'] !=0 else 0
        return context


class SubjectListView(ListView):
    model = Subject
    paginate_by = 7
    template_name = 'subject_list.html'

    def get_queryset(self, **kwargs):
        queryset = super().get_queryset()
        params = {}
        if self.request.GET.get('teacher'):
            try:
                params['pk__in'] = Teacher.objects.get(
                        pk=self.request.GET['teacher']
                    ).subjects.values_list('id', flat=True)
            except:
                queryset = Subject.objects.none()
        if self.request.GET.get('taught_by'):
            if params.get('pk__in'):
                params['pk__in'] += Teacher.objects.all().values('subjects'
                    ).annotate(taught_by_count=models.Count('subjects')
                    ).filter(taught_by_count__gt=self.request.GET['taught_by']
                    ).values_list('subjects')
            else:
                params['pk__in'] = Teacher.objects.all().values('subjects'
                    ).annotate(taught_by_count=models.Count('subjects')
                    ).filter(taught_by_count__gt=self.request.GET['taught_by']
                    ).values_list('subjects')
        if self.request.GET.get('student'):
            if params.get('pk__in'):
                params['pk__in'] += Student.objects.get(id=self.request.GET['student']
                    ).values_list('subjects')
            else:
                params['pk__in'] = Student.objects.get(id=self.request.GET['student']
                    ).values_list('subjects')
        if params:
            return queryset.filter(**params).distinct()
        return queryset

    @CustomDecorators.paginate
    def get_context_data(self, **kwargs):
        context = self.__class__.context
        if self.request.GET.get('taught_by'):
            context['teacher_check'] = True
        return context