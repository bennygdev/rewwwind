from flask import Blueprint, request, jsonify
import google.generativeai as genai
from dotenv import load_dotenv
import os

load_dotenv()

chatbot = Blueprint('chatbot', __name__)

genai.configure(api_key=os.getenv('GEMINI_API_KEY'))
model = genai.GenerativeModel("gemini-1.5-flash")

# load master prompts at startup
def load_master_prompts():
  current_dir = os.path.dirname(os.path.abspath(__file__))
  prompts_path = os.path.join(current_dir, 'static\\' , 'masterprompt.txt')
  print(prompts_path)
    
  try:
    with open(prompts_path, 'r') as file:
      print('Prompt file found.')
      return file.read()
  except FileNotFoundError:
    print("Master prompt file not found.")
    return ""

MASTER_PROMPTS = load_master_prompts()

def create_chat_context():
  # create new chat with master prompts
  chat = model.start_chat(
    history=[
      {
        "role": "user",
        "parts": [MASTER_PROMPTS]
      },
      {
        "role": "model",
        "parts": ["Understood. I will act as a helpful customer service chatbot following these guidelines."]
      }
    ]
  )
  return chat

@chatbot.route('/api/chat', methods=['POST'])
def chat():
  try:
    data = request.json
    user_message = data.get('message')
        
    if not user_message:
      return jsonify({'error': 'No message provided'}), 400

    chat = create_chat_context()
    response = chat.send_message(user_message)
        
    return jsonify({
      'response': response.text
    })
  except Exception as e:
    print(f"Error in chat endpoint: {str(e)}")  # for debugging
    return jsonify({'error': str(e)}), 500