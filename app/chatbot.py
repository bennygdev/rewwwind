from flask import Blueprint, request, jsonify
import google.generativeai as genai
from dotenv import load_dotenv
import os

load_dotenv()

chatbot = Blueprint('chatbot', __name__)

genai.configure(api_key=os.getenv('GEMINI_API_KEY'))
model = genai.GenerativeModel("gemini-1.5-flash")

chat = model.start_chat(
  history=[
    {"role": "user", "parts": "Hello"},
    {"role": "model", "parts": "Great to meet you. What would you like to know?"},
  ]
)

@chatbot.route('/api/chat', methods=['POST'])
def chat():
  try:
    data = request.json
    user_message = data.get('message')
        
    if not user_message:
      return jsonify({'error': 'No message provided'}), 400

    chat = model.start_chat()
    response = chat.send_message(user_message)
        
    return jsonify({
      'response': response.text
    })
  except Exception as e:
    return jsonify({'error': str(e)}), 500