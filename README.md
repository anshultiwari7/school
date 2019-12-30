
School


Setup-
  - Required Python3.7.5 - Project created upon.
  - Create virtual environment - virtualenv -p python3 envname
  - Install requirements.txt residing in lendenclub project.
  - Use built-in django sqlite3 and test data file db.sqlite3 residing in lendenclub project.
  - Read ER-diagram residing in lendenclub project as er-diagram.png.
 
 
 
Project Structure -

Procfile
README.md
db.sqlite3
er-diagram.png
lendenclub/
    __init__.py
    __pycache__
    asgi.py
    settings.py
    urls.py
    utils.py
    wsgi.py
manage.py
requirements.txt
school/
    __init__.py
    __pycache__
    admin.py
    apps.py
    migrations/
        0001_initial.py
        0002_delete_chapter.py
        __init__.py
        __pycache__
    models.py
    templates/
        classroom_list.html
        student_list.html
        subject_list.html
        teacher_list.html
    tests.py
    urls.py
    views.py




Assumptions and extras - 
  - Classroom can be taught by multiple teachers and can be attended by multiple students.
  - Teacher has no model field for web-lecture support, it is set as a permission in built-in django Permission under the same     model.
  - A classroom have subjects which are available but not taught by any teacher or opted by any student.
  - All the links shown in the count representing columns redirects to listing page of column values.
