from django.urls import path

from school.views import (
		ClassroomListView, StudentListView,
		TeacherListView, SubjectListView
	)

urlpatterns = [
    path('classrooms/', ClassroomListView.as_view(), name='classroom-list'),
    path('students/', StudentListView.as_view(), name='student-list'),
    path('teachers/', TeacherListView.as_view(), name='teacher-list'),
    path('subjects/', SubjectListView.as_view(), name='subject-list'),
]
