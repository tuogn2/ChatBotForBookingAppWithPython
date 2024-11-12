from flask import Flask, request, jsonify
from gpt_assistant import GPTAssistant
import json
from flask_cors import CORS  # Thêm dòng này

app = Flask(__name__)
CORS(app)
gpt_assistant = GPTAssistant()
@app.route("/chat", methods=["POST"])
def chat_with_ai():
    try:
        data = request.get_json()
        user_message = data.get("message", "")
        user_id = data.get('user_id')
        response = gpt_assistant.process_message(user_message, user_id)
       
        return jsonify({"response": response})
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
@app.route("/api/v1/rooms", methods=["GET"])
def get_rooms():
    try:
        room_names = gpt_assistant.get_rooms()
        return jsonify(room_names)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(port=8080, debug=True)
