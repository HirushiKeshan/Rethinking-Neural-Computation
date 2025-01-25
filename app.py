from flask import Flask, request, jsonify, render_template
import google.generativeai as genai
import sqlite3
import spacy
from PIL import Image
from pytesseract import pytesseract
import os

app = Flask(__name__)

# Set up Tesseract
path_to_tesseract = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
pytesseract.tesseract_cmd = path_to_tesseract

# Load spaCy model for NLP
nlp = spacy.load("en_core_web_sm")

# Configure Google Generative AI
API_KEY = ""  # Replace with your API key
genai.configure(api_key=API_KEY)

model = genai.GenerativeModel('gemini-pro')
chat = model.start_chat(history=[])

instruction = "In this chat, respond as if you're explaining things to a 50-year-old man. Provide detailed and clear answers, leaving space between paragraphs for better readability."

# Database setup
def init_db():
    conn = sqlite3.connect('queries.db')
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS history (
                      id INTEGER PRIMARY KEY AUTOINCREMENT,
                      query TEXT NOT NULL,
                      response TEXT NOT NULL)''')
    conn.commit()
    conn.close()

def save_query_to_db(query, response):
    conn = sqlite3.connect('queries.db')
    cursor = conn.cursor()
    cursor.execute("INSERT INTO history (query, response) VALUES (?, ?)", (query, response))
    conn.commit()
    conn.close()

def send_message(question):
    if question.strip() == '':
        return "Please ask something."

    # Use spaCy for NLP processing
    doc = nlp(question)

    # Process the input with spaCy (e.g., extract entities, keywords)
    processed_question = ' '.join([token.lemma_ for token in doc])
    
    # Send the processed question to the chat model
    response = chat.send_message(instruction + processed_question)

    # Save to the database
    save_query_to_db(question, response.text)

    # Format the response for better readability
    formatted_response = response.text.replace('\n', ' ').strip()  # Replace line breaks and strip spaces
    return formatted_response

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/chat', methods=['POST'])
def chat_response():
    user_message = request.json['message']  # Read JSON input
    bot_response = send_message(user_message)

    return jsonify({'response': bot_response})  # Return a JSON response

@app.route('/history', methods=['GET'])
def get_history():
    conn = sqlite3.connect('queries.db')
    cursor = conn.cursor()
    cursor.execute("SELECT query, response FROM history")
    rows = cursor.fetchall()
    conn.close()
    
    # Format history for the frontend
    formatted_history = [{"query": query, "response": response.replace('\n', ' ').strip()} for query, response in rows]
    return jsonify(formatted_history)

@app.route('/extract-text', methods=['POST'])
def extract_text():
    if 'image' not in request.files:
        return "No image uploaded", 400
    file = request.files['image']
    if file:
        img = Image.open(file.stream)
        text = pytesseract.image_to_string(img)
        return jsonify({"extracted_text": text.strip()}), 200
    return "Failed to process the image", 500

if __name__ == '__main__':
    init_db()
    app.run(debug=True)
