from django.db import models
from django.contrib import messages
from django.contrib.auth.models import AbstractUser, Permission
from django.core.validators import (RegexValidator, MaxValueValidator, 
    MinValueValidator)
from django.core.exceptions import ValidationError

# Create your models here.

class Subject(models.Model):
    name = models.CharField(max_length=30)
    total_duration = models.IntegerField(
            help_text='Total duration in minutes')
    per_class_duration = models.IntegerField(default=30,
            validators=[MaxValueValidator(60), MinValueValidator(30)],
            help_text='Per class duration in minutes')

    def save(self): 
        if self.per_class_duration > self.total_duration:
            raise ValidationError({'per-class-duration': ["Cannot be greater than total duration",]})
        super(Subject, self).save()


    @property
    def total_teachers(self):
        return Teacher.objects.filter(
            subjects__pk=self.pk).distinct().count()
    
    @property
    def total_students(self):
        return Student.objects.filter(
            subjects__pk=self.pk).distinct().count()

    @property
    def total_duration_hours(self):
        if not self.total_duration:
            self.total_duration = 0
        hours = int(self.total_duration/60)
        minutes = self.total_duration%60
        return str(hours) + ':' + str(minutes)
    

    def __str__(self):
        return self.name


class Classroom(models.Model):
    SHAPE_OVAL, SHAPE_RECTANGULAR, SHAPE_CANOPY, SHAPE_ELEVATED = range(0, 4)
    SHAPE = (
        (SHAPE_OVAL, 'Oval'),
        (SHAPE_RECTANGULAR, 'Rectangular'),
        (SHAPE_CANOPY, 'Canopy'),
        (SHAPE_ELEVATED, 'Elevated')
    )
    name = models.CharField(max_length=50)
    seating_capacity = models.IntegerField(default=15,
            validators=[MaxValueValidator(100), MinValueValidator(15)]
        )
    web_lecture_support = models.BooleanField(default=False)
    shape = models.IntegerField(default=SHAPE_OVAL, choices=SHAPE)
    subjects = models.ManyToManyField(Subject,
        related_name='taught_in_classrooms')

    @property
    def shape_string(self):
        return self.SHAPE[self.shape][1]

    @property
    def number_of_students(self):
        return Student.objects.filter(
            subjects__id__in=self.subjects.values_list('id')).distinct().count()

    @property
    def number_of_teachers(self):
        teachers = Teacher.objects.filter(
            subjects__id__in=self.subjects.values_list('id')).distinct()
        if self.web_lecture_support == True:
            total_teachers = 0
            for teacher in teachers:
                if teacher.has_perm('school.can_teach_weblecture'):
                    total_teachers+=1
            return total_teachers
        return teachers.count()

    @property
    def number_of_subjects(self):
        return self.subjects.count()
    
    def __str__(self):
        return self.name


class User(AbstractUser):
    date_of_joining = models.DateField(null=True, blank=True)
    phone_regex = RegexValidator(regex=r'^[6-9]\d{9}$',
        message="Invalid mobile number")
    phone_number = models.CharField(max_length=10, 
        validators=[phone_regex], blank=True, null=True)

    @property
    def full_name(self):
        if self.last_name:
            return self.first_name + ' ' + self.last_name
        return self.first_name

    @property
    def phone_number_(self):
        phone_number = self.phone_number if self.phone_number else 'Not available'
        return phone_number
    


class Student(User):
    roll_number = models.IntegerField(unique=True)
    standard = models.IntegerField(
            validators=[MaxValueValidator(12), MinValueValidator(1)],
            help_text='Between [1, 12]'
        )    
    ranking = models.IntegerField()
    point_of_contact = models.ManyToManyField(User,
        related_name='related_students')
    subjects = models.ManyToManyField(Subject,
        related_name='opted_by')


    def save(self): 
        try:
            top = Student.objects.order_by('-ranking', 'roll_number')[0]
        except:
            top = Student.objects.none()
            top.ranking = 0
            top.roll_number = 0
        if not self.ranking:
            self.ranking = top.ranking + 1
        if self.ranking > top.ranking + 1 and self != top:
            messages.error(request,'Top rank available: ' + str(top.ranking + 1))
        if not self.roll_number:
            self.roll_number = top.roll_number + 1
        super(Student, self).save()

    class Meta:
        verbose_name = 'Student'
        verbose_name_plural = 'Students'

    def __str__(self):
        return super(User, self).username

    @property
    def total_relatives(self):
        names = ', '.join(self.point_of_contact.values_list(
            'username', flat=True)
        ) if self.point_of_contact.count() > 0 else 'No Relatives'
        return names.title()

    @property
    def total_teachers(self):
        return Teacher.objects.filter(
                subjects__id__in=self.subjects.values_list('id')
            ).distinct().count()

    @property
    def total_classrooms(self):
        return Classroom.objects.filter(
            subjects__id__in=self.subjects.values_list('id')).distinct().count()

    @property
    def teachers_salary_sum(self):
        salary_sum = Teacher.objects.filter(
            subjects__id__in=self.subjects.values_list('id')
            ).aggregate(models.Sum('salary')).get('salary__sum')
        if salary_sum:
            return salary_sum
        return 0


class Teacher(User):
    salary = models.FloatField(help_text='Salary in LPA')
    subjects = models.ManyToManyField(Subject,
        related_name='taught_by')

    @property
    def total_classrooms(self, kwargs = {}):
        if self.has_perm('can_teach_weblecture'):
            kwargs['web_lecture_support'] = True
        return Classroom.objects.filter(
                subjects__in=self.subjects.values_list('id'),
                **kwargs).distinct().count()

    @property
    def total_subjects(self):
        return self.subjects.count()

    @property
    def total_students(self):
        return Student.objects.filter(
            subjects__id__in=self.subjects.values_list('id')).distinct().count()

    class Meta:
        verbose_name = 'Teacher'
        verbose_name_plural = 'Teachers'
        permissions = [
            ("can_teach_weblecture", "Can teach web-lecture")
        ]

    def __str__(self):
        return super(User, self).username