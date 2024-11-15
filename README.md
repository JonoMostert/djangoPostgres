# Transaction Categorisation

## What does the application do?

In a world where credit cards are becoming more and more popular, the implications on financial tracking and budgeting have become more complex.
Our budgeting calculations now need to track across multiple platforms and account for the various difference between them. In order to achieve this synchronous integration we need to be able to categorize all of our transactions to understand what our biggest contributors are to our expenses. Unfortunately, not all platforms will allow us to categorise our expenses and this needs to be done manually (especially in the case of American Express (Amex)). 

| Trannsaction ID | Monzo Category | Amex Category |
|----------------:|---------------:|--------------:|
| 1               | Transport      | Null          |
| 2               | Groceries      | Null          |
| 3               | Entertainment  | Null          |

This problem can be handled in two ways: 
1. Manually categorise each Amex transaction before collating the data together
2. Automaticlaly catagorise the Amex transactions before collating the data

This application leverages Machine Learning to automatically categorise the Amex transactions, before collating the transactions together and providing the user with a summary of their expenses.

# Django Web Framework

## The insides of the app

The app was developed using the Django Web Framework. Specifcally, Django Forms, Models, Views and a postgresSQL database (postgresProject).

Looking into the the 'postresProject' directory will provide a good understanding of how everything fits together.

`models.py` - the definition of the database models.<br>
`urls.py` - the definition of the URL endpoints used by the app's views.<br>
`forms.py` - define the form used to collect user input (in this case, csv files of the useres transactions).<br>
`templates/` - contains the html templates rendered by the views.<br>
`views.py` - the methods (views) within are used to connect the user with the app's backend functionality.<br>
`categoryCreation.py` - contains the predict_category class which calls the Machine Learning model and predicts the Amex categories, and the assign_categories class which assigns the predicted categories to the Amex table in the database .<br>
'summaryTableCreate.py' - creates a third table in the database that represents the collation of all the transactions.<br>
`tests.py` - contains tests used to verify the call calculation made by the CallController class.<br>

## The models
Three models are used by the app:

* Table1 - contains the Monzo transaction dates, description, category and amount
* Table2 - contains the Amex transaction dates, description, category and amount
* CombinedTable - contains the combined data of Table1 and Table2

All of the models are created and appended by the app. The results of the .csv files are recorded in these tables.

## Docker
The app image (djangoapp) encapsulates all the necessary configurations as defined in the Dockerfile.

Here is a run through of how it works:

Specific libraries are required to allow the Django app to interface with the postgresSQL database, and these are defined in the first "RUN" function.
```shell script
RUN apt-get update && apt-get install -y \
    libpq-dev \
    gcc \
    && rm -rf /var/lib/apt/lists/*
```
The working directory in docker is set up as follows:
```shell script
WORKDIR /app
```
This will create a working directory called "app" in Docker.

The environment requirements are all listed in the requirements.txt file and used when creating the base image.
```shell script
COPY requirements.txt .
```

This, however, does not include the database configuration. Since we will be using postresSQL, we will need a docker-compose.yml file that can be executed to run both the djangoapp and database.
* NOTE: setting up of these images and starting the docker container will be shown in detail later on.

Since this project has not been developed for production environment, we will be using "volumes" in the docker-compose.yml file. This allows the Docker container to use the local app folder during start up and will take any changes made to the scripts into account without rebuilding the base image. For production, this would need to be removed as we would want to freeze the base image.

As mentioned before, the second image is the postgresSQL image that was taken directly from DockerHub. Since we are not using the built in sqlite3 database, we need to make changes in our settings.py folder. Specifically:
```shell script
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'postgres',
        'USER': 'postgres',
        'PASSWORD': 'mypassword',
        'HOST': 'my-postgres',
        'PORT': '5432',
    }
}
'''
This tells Django how to connect to the postgres database.
Finally, the specific image is linked to the container by specifying it in the docker-compose.yml file.

# Machine Learning Model


