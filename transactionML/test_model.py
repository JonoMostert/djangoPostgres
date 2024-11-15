# test_model.py
import torch
from models.rnn_model import TransactionRNN
import pandas as pd
import pickle

# Parameters
INPUT_SIZE = 5000  # Must match the input size used in the training script
HIDDEN_SIZE = 128   # Must match the hidden size used in the training script
OUTPUT_SIZE = 9     # Must match the output size used in the training script
MAX_LENGTH = 100    # Should match the max length used during training

# Load the trained model
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
model = TransactionRNN(INPUT_SIZE, HIDDEN_SIZE, OUTPUT_SIZE).to(device)
# model.load_state_dict(torch.load('transaction_categorization/models/transaction_rnn.pth'))
model.load_state_dict(torch.load('transaction_categorization/models/transaction_rnn2.pth'))
model.eval()

# Load the label encoder
with open('transaction_categorization/models/label_encoder.pkl', 'rb') as f:
    label_encoder = pickle.load(f)

# Function to preprocess input data
def preprocess_data(descriptions):
    vocab = set(''.join(descriptions))
    char_to_idx = {char: idx + 1 for idx, char in enumerate(vocab)}  # Start indexing from 1
    tokenized_descriptions = [
        [char_to_idx.get(char, 0) for char in desc] for desc in descriptions  # Default to 0 if char not in vocab
    ]
    # Pad sequences
    tokenized_descriptions = [desc + [0] * (MAX_LENGTH - len(desc)) for desc in tokenized_descriptions]
    return torch.tensor(tokenized_descriptions, dtype=torch.long)

# Load new transaction data for testing
test_data = pd.read_csv('transaction_categorization/data/cleaned_training_data.csv')  # Ensure the path is correct
test_descriptions = test_data['Description'].values
test_cat = test_data['Category'].values

# Preprocess the test descriptions
test_tensor = preprocess_data(test_descriptions).to(device)

# Make predictions
with torch.no_grad():
    outputs = model(test_tensor)
    _, predicted = torch.max(outputs, 1)

# Decode the predicted categories
predicted_categories = label_encoder.inverse_transform(predicted.cpu().numpy())

# Output results
correct = 0
total = 0
for desc, category,exp_cat in zip(test_descriptions, predicted_categories,test_cat):
    print(f'Description: {desc} | Predicted Category: {category}')
    if category == exp_cat:
        correct = correct+1
        total = total+1
    else:
        total = total+1
    
print(f'Correct: {correct}. Total: {total}. Accuracy: {(correct/total)*100}%')
