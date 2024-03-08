import pandas as pd
import json
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report
from transformers import BertTokenizer, TFBertForSequenceClassification
from tensorflow.keras.callbacks import EarlyStopping

# Charger les données prétraitées
dataset = '/Users/gemmafelton/Desktop/Interface_web/corpus/detection_dh.csv'
df = pd.read_csv(dataset)

# Ajouter une colonne pour la classification binaire
df['label'] = df.apply(lambda row: 1 if row['hate_speech_count'] > 0 or row['offensive_language_count'] > 0 else 0, axis=1)

# Diviser les données en ensembles d'entraînement et de test
train_data, test_data, train_labels, test_labels = train_test_split(
    df['tweet'], df['label'], test_size=0.2, random_state=42
)

# Charger le tokenizer
tokenizer = BertTokenizer.from_pretrained('bert-base-uncased')

# Tokeniser les textes
train_encodings = tokenizer(list(train_data.astype(str)),
                             truncation=True,
                             padding=True,
                             max_length=128,
                             return_tensors='tf')
test_encodings = tokenizer(list(test_data.astype(str)),
                            truncation=True,
                            padding=True,
                            max_length=128,
                            return_tensors='tf')

# Créer le modèle BERT pour la classification de séquence
model = TFBertForSequenceClassification.from_pretrained('bert-base-uncased', num_labels=2)

# Compilation du modèle
model.compile(optimizer='adam',
              loss='sparse_categorical_crossentropy',
              metrics=['accuracy'])

# Entraînement du modèle
early_stopping = EarlyStopping(monitor='val_loss', patience=3, restore_best_weights=True)

model.fit(train_encodings, train_labels,
          epochs=3,
          batch_size=10,
          validation_split=0.2,
          callbacks=[early_stopping])

# Évaluation du modèle sur l'ensemble de test
predictions = model.predict(test_encodings)
predicted_classes = predictions.logits.argmax(axis=1)

# Affichage du rapport de classification avec scikit-learn
classification_rep = classification_report(test_labels, predicted_classes)
print('\nClassification Report:\n', classification_rep)

# Enregistrer les résultats dans un fichier json
results_data = {
    "actual_labels": test_labels.tolist(),
    "predicted_labels": predicted_classes.tolist(),
    "classification_report": classification_rep,
}

with open('/Users/gemmafelton/Desktop/Interface_web/scripts/models/bert_classification_results.json', 'w') as json_file:
    json.dump(results_data, json_file)