start cmd.exe /k "env\Scripts\activate && pip install -r requirements.txt && cd InstaShare && python manage.py makemigrations restAPI && python manage.py migrate && python manage.py runserver"
