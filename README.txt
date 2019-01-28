Requirements:
	Python
	VirtualENV, with an ENV in workspace
Windows Dev:
	Just run the batch file to auto config the server
Mac Dev:
	Open the batchfile to see the list of commands to run
	1) activate ENV
	2) cd into InstaShare
	3)python manage.py makemigrations restAPI
	4)python manage.py migrate
	5)python manage.py runserver