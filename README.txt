Requirements:
	Python
	VirtualENV, with an ENV in workspace
Windows Dev:
	Just run the batch file to auto config the server
Mac Dev:
	Open the batchfile to see the list of commands to run(requires virtualENV)
	1) activate ENV
	2) cd into InstaShare
	3) pip install -r requirements.txt
	3)python manage.py makemigrations restAPI
	4)python manage.py migrate
	5)python manage.py runserver


AWS requirements and account set up:
1. Navigate to AWS’s IAM and create a user with Amazon S3 Access and Amazon Rekognition Access. Download both ACCESS_KEY_ID 	and ACCESS_SECRET_KEY. Change both keys to your key on your credentials.cvs. 
2. Navigate to AWS’s S3 and create a bucket for this project. Change the name of the bucket on CollectionTools.py to your 	bucket name
3. Set up the AWS’s Elastic Beanstalk and EC2 using this AWS documentation: 					
	https://docs.aws.amazon.com/elasticbeanstalk/latest/dg/create-deploy-python-django.html
	
	Add this to a .ebextensions/customize_httpd.config file:
	———
	files:
	  "/etc/httpd/conf.d/wsgi_custom.conf":
	    mode: "000644"
	    owner: root
	    group: root
	    content: |
	      WSGIPassAuthorization On
	———
