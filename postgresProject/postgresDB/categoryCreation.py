# postgresDB/categoryCreation.py

# from .models import Table2

# # Define category mapping
# CATEGORY_MAPPING = {
#     "Sainsbury's": 'Groceries',
#     'Tesco': 'Groceries',
#     'Deliveroo': 'Eating out',
#     'Bar': 'Eating out',
#     'Netflix': 'Entertainment',
#     'Amazon': 'Shopping',
#     'TFL': 'Transport',
#     'Human Forest': 'Transport',
#     'Lime': 'Transport',
#     # Add more mappings as needed
# }

# def assign_categories():
#     # Retrieve all rows in Table2 without a Category
#     table2_rows = Table2.objects.filter(Category='')

#     for row in table2_rows:
#         # Check each keyword in CATEGORY_MAPPING to see if it matches the Description
#         for keyword, category in CATEGORY_MAPPING.items():
#             if keyword.lower() in row.Description.lower():
#                 row.Category = category
#                 row.save()
#                 break
# postgresDB/categoryCreation.py

import pandas as pd
import pickle
import torch
from .models import Table2
from .rnn_model import TransactionRNN

# Parameters for model
INPUT_SIZE = 100  # Update this based on your vocabulary size used during training
HIDDEN_SIZE = 128
OUTPUT_SIZE = 9  # Update this based on the number of categories used during training

# Function to load the trained model
def load_model():
    model = TransactionRNN(INPUT_SIZE, HIDDEN_SIZE, OUTPUT_SIZE)
    model.load_state_dict(torch.load('postgresDB/transaction_rnn.pth'))
    model.eval()  # Set the model to evaluation mode
    return model

# Function to predict categories
def predict_category(model, descriptions):
    # Tokenization and padding as per training
    char_to_idx = {char: idx + 1 for idx, char in enumerate(set(''.join(descriptions)))}
    max_length = max([len(desc) for desc in descriptions])
    tokenized_descriptions = [[char_to_idx.get(char, 0) for char in desc] for desc in descriptions]

    # Pad sequences
    tokenized_descriptions = [desc + [0] * (max_length - len(desc)) for desc in tokenized_descriptions]

    # Convert to tensor
    inputs = torch.tensor(tokenized_descriptions, dtype=torch.long)

    # Get predictions
    with torch.no_grad():
        outputs = model(inputs)
        _, predicted = torch.max(outputs, 1)

    return predicted

# Load the label encoder
def load_label_encoder():
    with open('postgresDB/label_encoder.pkl', 'rb') as f:
        label_encoder = pickle.load(f)
    return label_encoder

def assign_categories():
    # Retrieve all rows in Table2 without a Category
    table2_rows = Table2.objects.filter(Category='')

    # Prepare data for predictions
    descriptions = [row.Description for row in table2_rows]
    
    if not descriptions:
        print("No descriptions found for prediction.")
        return

    # Load model and label encoder
    model = load_model()
    label_encoder = load_label_encoder()

    # Predict categories for all descriptions
    predicted_indices = predict_category(model, descriptions)
    predicted_categories = label_encoder.inverse_transform(predicted_indices.numpy())

    # Update Table2 with predicted categories
    for row, category in zip(table2_rows, predicted_categories):
        row.Category = category
        row.save()
    
    