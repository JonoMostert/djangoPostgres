# train_model.py
import pandas as pd
import numpy as np
import torch
import torch.nn as nn
import torch.optim as optim
from torch.optim.lr_scheduler import ReduceLROnPlateau
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from sklearn.utils import resample
from sklearn.utils.class_weight import compute_class_weight
from models.rnn_model import TransactionRNN
import pickle
import os

# Parameters
INPUT_SIZE = 5000  # Adjust based on your data preprocessing
HIDDEN_SIZE = 128
OUTPUT_SIZE = 9  # Adjust based on the number of unique categories in your dataset
EPOCHS = 1000
BATCH_SIZE = 64
LEARNING_RATE = 0.0001

# Function to oversample minority classes
def oversample_minority_classes(descriptions, categories):
    df = pd.DataFrame({'Description': descriptions, 'Category': categories})

    # Count the number of occurrences of each category
    category_counts = df['Category'].value_counts()
    max_count = category_counts.max()

    # Create an empty list to hold the upsampled data
    upsampled_data = []

    for category, count in category_counts.items():
        category_data = df[df['Category'] == category]
        
        # If the count is less than the max, we need to upsample
        if count < max_count:
            # Calculate the number of samples needed
            samples_needed = max_count - count
            
            # Randomly sample with replacement from the existing category data
            upsampled_samples = category_data.sample(samples_needed, replace=True)
            upsampled_data.append(upsampled_samples)

        # Append the original data for this category
        upsampled_data.append(category_data)

    # Concatenate the upsampled data into a new DataFrame
    df_upsampled = pd.concat(upsampled_data, ignore_index=True)

    # Return the upsampled descriptions and categories
    return df_upsampled['Description'].values, df_upsampled['Category'].values


# Load Data
data = pd.read_csv('transaction_categorization/data/cleaned_training_data.csv')
descriptions = data['Description'].values
categories = data['Category'].values

# Over-sample minority classes
descriptions, categories = oversample_minority_classes(descriptions, categories)

# Preprocess Data
label_encoder = LabelEncoder()
encoded_labels = label_encoder.fit_transform(categories)

# Calculate class weights
class_weights = compute_class_weight('balanced', classes=np.unique(encoded_labels), y=encoded_labels)
class_weights = torch.tensor(class_weights, dtype=torch.float)

# Tokenize Descriptions (simple character-level tokenization for illustration)
vocab = set(''.join(descriptions))
char_to_idx = {char: idx + 1 for idx, char in enumerate(vocab)}  # Start indexing from 1
max_length = max(len(desc) for desc in descriptions)

# Tokenize and pad sequences
def pad_sequence(seq, max_len):
    return seq + [0] * (max_len - len(seq))

tokenized_descriptions = [
    pad_sequence([char_to_idx[char] for char in desc], max_length) for desc in descriptions
]

# Split Data
X_train, X_val, y_train, y_val = train_test_split(tokenized_descriptions, encoded_labels, test_size=0.2, random_state=42)
# X_train = tokenized_descriptions
# y_train = encoded_labels

# Convert to PyTorch tensors
X_train_tensor = torch.tensor(X_train, dtype=torch.long)
X_val_tensor = torch.tensor(X_val, dtype=torch.long)
y_train_tensor = torch.tensor(y_train, dtype=torch.long)
y_val_tensor = torch.tensor(y_val, dtype=torch.long)

# Model Setup
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
print(device)
model = TransactionRNN(INPUT_SIZE, HIDDEN_SIZE, OUTPUT_SIZE).to(device)
criterion = nn.CrossEntropyLoss(weight=class_weights)
optimizer = optim.Adam(model.parameters(), lr=LEARNING_RATE)
# scheduler = ReduceLROnPlateau(optimizer, 'min', patience=3, verbose=True)

# # Load Checkpoint if available
# checkpoint_path = 'transaction_categorization/models/transaction_rnn_checkpoint1.pth'
# start_epoch = 0
# if os.path.exists(checkpoint_path):
#     checkpoint = torch.load(checkpoint_path)
#     model.load_state_dict(checkpoint['model_state_dict'])
#     optimizer.load_state_dict(checkpoint['optimizer_state_dict'])
#     start_epoch = checkpoint['epoch'] + 1  # Start from the next epoch
#     print(f"Checkpoint loaded. Resuming training from epoch {start_epoch}.")
# else:
#     print("No checkpoint found. Starting training from scratch.")
# checkpoint_path = 'transaction_categorization/models/transaction_rnn_checkpoint2.pth'

# Training Loop
for epoch in range(EPOCHS):
    model.train()
    epoch_loss = 0
    for i in range(0, len(X_train_tensor), BATCH_SIZE):
        batch_X = X_train_tensor[i:i + BATCH_SIZE].to(device)
        batch_y = y_train_tensor[i:i + BATCH_SIZE].to(device)

        optimizer.zero_grad()
        output = model(batch_X)
        loss = criterion(output, batch_y)
        loss.backward()
        optimizer.step()        
        epoch_loss += loss.item()
        # scheduler.step(epoch_loss)

    print(f'Epoch [{epoch + 1}/{EPOCHS}], Loss: {epoch_loss / len(X_train_tensor):.4f}')
    if (epoch_loss/ len(X_train_tensor)) < 0.0105:
        exit

    # Save checkpoint after each epoch
#     checkpoint = {
#         'model_state_dict': model.state_dict(),
#         'optimizer_state_dict': optimizer.state_dict(),
#         'epoch': epoch,
#         'loss': epoch_loss
#     }
    
# torch.save(checkpoint, checkpoint_path)    

# Save Model and Label Encoder
torch.save(model.state_dict(), 'transaction_categorization/models/transaction_rnn2.pth')
with open('transaction_categorization/models/label_encoder.pkl', 'wb') as f:
    pickle.dump(label_encoder, f)
print("Training complete. Model and label encoder saved.")
