Simple Time Clock Application

    Summary:
        - This application is my Simple Time Clock Application.
        - The technologies used to build this application are primarily:
            - Django
            - JavaScript
            - Html
            - CSS
            - PostgreSQL
            - Alembic
            - Sqlalchemy
        
        - There are two django apps in this project, "login" and "time_clock".
        the login app handles the processes of logging into the application,
        while the time_clock app handles everything involving shift data.


    Running this project locally:
        1. To run this application locally, you will need to have the following prerequisites:
            - python3

            - pipenv

            - an empty local PostgreSQL database, with the EXTENSION "uuid-ossp". Get this
              EXTENSION by running the following command in your query editor for PostgreSQL:
                CREATE EXTENSION "uuid-ossp";
        
        2. Once you have all the above (assuming you already downloaded and unzipped the simple_time_clock folder),
          you will need to create a virtual environment:
            - cd into the simple_time_clock directory

            - run the command: 
                pipenv shell
              to create a virtual environment

            - run the command:
                pipenv sync --dev
              to install the dependencies for the project

            - you should now be in the virtual environment
        
        3. Once the virtual environment is created, you will need to link your local db by changing
          the following in lines in line 79-88 of core.settings.py with your DB's info:
            DATABASES = {
                'default': {
                    'ENGINE': 'django.db.backends.postgresql',
                    'NAME': ENTER YOUR DBs NAME,
                    'USER': "ENTER THE USER NAME,
                    'PASSWORD': ENTER THE PASSWORD FOR THE USER,
                    'HOST': "127.0.0.1",
                    'PORT': "5432"
                }
            }

        4. Create a .env file in the same path as the PipFile and PipFile.lock files and paste
          the following in the .env file. (SQLALCHEMY_URL and DB_URL reflect your databases info):
            DEBUG = False
            SECRET_KEY = 'django-insecure-nl9hf-&sibl)xh5$oq!as)n@l97%8pz%rz!e*75zygx$hxyu09'
            SQLALCHEMY_URL = 'postgresql://user:password@localhost/db_name'
            DB_URL = 'postgresql://user:password@localhost/db_name'

        5. Once the .env file is created, do the following in the virtual environment 
          (if you are not in the virtual environment, run: pipenv shell)
          to create the tables needed locally:
            - cd into the folder where the manage.py file is and run the following command:
                python manage.py migrate
              to create the django tables

            - run the command:
                alembic upgrade head
              to create the tables related to the a login and time_clock apps

        7. You should now be able to run:
              python manage.py runserver
           to run the app locally
            
