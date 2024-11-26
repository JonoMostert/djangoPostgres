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
`tests.py` - .<br>

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
```
This tells Django how to connect to the postgres database.
Finally, the specific image is linked to the container by specifying it in the docker-compose.yml file.

# Machine Learning Model
The machine learning model is a Recurrent Neural Network (RNN) incorperated from the Pytorch module. This model was selected above a feedforward model, as RNNs are better suited to sequential data, specifically that of context-dependant data. RNNs untilise a hidden layer, which is used to maintain memory of previous inputs. This allows the model to understand the context provided by the sequence of words in the transaction descriptions - as apposed to a feedforward model that looses inherent ordering or relationships between words.

## The insides of the ML
There are 5 important files in the folder structure that are worth noting.

`rnn_model.py` - the definition of the RNN model. This is used during training to provide a predicted outcome based on the provided input.<br>
`train_model.py` - the training script that tockenizes the descriptions and itterates through training Epochs, calling the RNN model at each itteration.<br>
`transaction_rnn.pth` - the executable of the trained RNN model (with all the weights and biases stored).<br>
`label_encoder.pkl` - contains the label encoder object. The NN will output integer values representing the categories, this encoder is used to decode these values back into the category names.<br>
`test_model.py` - the script that is used to validate the model's accuracy.<br>

## Weights and biases
The RNN contains 3 important wights in the `transaction_rnn.pth` model.
1. Input-to-Hidden Weights:
These weights determine how the input features are transformed into the hidden state. i.e the matrix to convert the input data to the usable hidden layer.
2. Hidden-to-Hidden Weights:
These weights determine how the hidden state at the previous time step affects the current hidden state.
3. Hidden-to-Output Weights:
These weights determine how the hidden state is transformed into the output (e.g. category predictions).

## Areas of improvement
At present, the accuracy of the model is quite low. There are several reasons for this:
1. The data set size is not nearly big enough. At present I have around 1500 data points to train the model on from when I first open my bank account. In order to get better results, I would need at least 10k data points.
2. The data I have at the moment is packed with noise. The vendor descriptions contain locations, special characters and numbers - all of which make the training process more complex. In order to better the training on this data, there are a few possible steps to take:
    * Pre-process and clean the training data (the issue: training the model on cleaned data will inccure inaccuracy when using the model on real-life noisy data)
    * pre-process training data and real-life data (the issue: unaccounted for vendor descriptions might contain noisy data that slips through the pre-processing filters)
    * train the model on a much larger set of noisy data
3. The input sequence of data to the model needs to be optimised. Here is an overview of the current tockenisation method:
    * The model uses character-level tockenization (each character in the transaction description is maped to a unique index)
    * The tokenized sequences are padded to a uniform length (the maximum lenght of the descriptions)
    * These sequences are then batched in sizes of 64
   Possible improvements:
    * Switch to wrod-level tokenization (character-level tokenization might lose the semantic meaning of words)
    * Use pre-trained embeddings instead of learning embeddings from scratch (currently the case). This can be done with GloVe or FastText.
    * Use dynamic padding instead of the maximum length of the descriptions from the data set (this will reduce memory and increase performance).
    * Add positional encoding. Currently, the RNN does not encode the position of the tokens and can therefore limit the ability to understand the importance of the sequence order.


# Setting up the app for yourself

Clone the repo, then
```shell script
cd djangoPostgres/postgresProject
```
Set up a virtual environment
```shell script
python -m venv .venv
```
```shell script
.venv/Scripts/Activate.ps1
```
Install django
```shell script
pip install django
```
Install Docker Desktop.<br>
Build the app image
```shell script
docker build -t djangoapp .
```
Get the postgresSQL image
```shell script
docker pull postgres
```
Make the database migrations and run the app, it should be available by default at `http://127.0.0.1:8000/`
```shell script
python manage.py migrate
```
```shell script
docker-compose up
```

