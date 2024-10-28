from flask import Flask, request, jsonify
from flask_cors import CORS
import tensorflow as tf
import numpy as np
from tensorflow.keras.preprocessing.sequence import pad_sequences
from pythainlp.tokenize import word_tokenize
from tensorflow.keras.preprocessing.text import tokenizer_from_json

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Load the TensorFlow Lite models
interpreter = tf.lite.Interpreter(model_path='model_mdl_v1.tflite')
interpreter.allocate_tensors()

# Load the tokenizer from JSON files
with open("tokenizer_mdl_v1.json", 'r', encoding='utf-8') as f:
    tokenizer_json = f.read()
tokenizer_nopo = tokenizer_from_json(tokenizer_json)


# Load class labels
def load_class_labels(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        return [line.strip() for line in file.readlines()]

class_labels_y1 = load_class_labels('class_labels_mail_v1.txt')
class_labels_y2 = load_class_labels('class_labels_name_v1.txt')


# Tokenize and preprocess the input text
def tokenize_text(text):
    return ' '.join(word_tokenize(text))

def preprocess_text(text, tokenizer, max_sequence_length=6):
    tokenized_text = tokenizer.texts_to_sequences([text])
    return pad_sequences(tokenized_text, maxlen=max_sequence_length, dtype='float32')  # Ensure float32 type

# Helper function to process prediction scores and sort by rank
def process_predictions(predictions, class_labels, is_numeric=False):
    scores = predictions[0]  # Take the first batch element (since we process one input at a time)

    scores_with_labels = []
    for label, score in zip(class_labels, scores):
        try:
            if is_numeric:
                # Convert labels to int if they represent numbers (like Expense Code or WHT Code)
                numeric_label = int(float(label))
                scores_with_labels.append({"label": numeric_label, "score": float(score * 100)})
            else:
                # Default case, keep labels as strings
                scores_with_labels.append({"label": label, "score": float(score * 100)})
        except ValueError:
            # Handle the case where conversion fails
            print(f"Skipping label '{label}' due to conversion error.")
            continue

    # Sort by score in descending order
    sorted_scores_with_labels = sorted(scores_with_labels, key=lambda x: x['score'], reverse=True)
    return sorted_scores_with_labels


@app.route('/predict_Email', methods=['POST'])
def predict_non_PO():
    row = request.get_json()  # Get the input data from the POST request
    company = row['Company']
    vendor = row['Vendor']
    PO = row['PO']
    Material = row['Material']
    MatGroup = row['MatGroup']
    Plant =  row['Plant']

    # Combine the columns as before
    test_input = f"{company} {vendor} {PO} {Material} {MatGroup} {Plant}"

    # Preprocess the input text
    test_padded = preprocess_text(test_input, tokenizer_nopo)

    # Set the input tensor
    input_details = interpreter.get_input_details()[0]
    input_index = input_details['index']
    input_dtype = input_details['dtype']

    # Ensure input tensor is of the correct type
    if input_dtype == np.float32:
        test_padded = test_padded.astype(np.float32)

    interpreter.set_tensor(input_index, test_padded)

    # Run inference
    interpreter.invoke()

    # Get the output tensors
    output_details = interpreter.get_output_details()
    prediction_y1 = interpreter.get_tensor(output_details[1]['index'])  
    prediction_y2 = interpreter.get_tensor(output_details[0]['index'])  


    # Process predictions and sort by score
    sorted_scores_y1 = process_predictions(prediction_y1, class_labels_y1)
    sorted_scores_y2 = process_predictions(prediction_y2, class_labels_y2)


    # Convert the top predictions 
    predicted_class_label_y1 = sorted_scores_y1[0]["label"] 
    predicted_class_label_y2 = sorted_scores_y2[0]["label"]              



    # Prepare the response with sorted prediction scores
    response = {
        'predicted_Email': predicted_class_label_y1,
        'predicted_Name': predicted_class_label_y2,
        'sorted_prediction_scores_Email': sorted_scores_y1,
        'sorted_prediction_scores_Name': sorted_scores_y2,
    }

    return jsonify(response)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
