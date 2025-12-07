HOW TO USE (Windows)
1. Create virtualenv:
   python -m venv venv
   venv\Scripts\activate
2. Install:
   pip install -r requirements.txt
3. Initialize data (runs migrations, creates superuser admin/admin123, loads demo products):
   python manage.py initdata
4. Run server:
   python manage.py runserver
Admin: http://127.0.0.1:8000/admin/  (admin/admin123)
