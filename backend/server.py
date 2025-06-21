from flask import Flask, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

@app.route('/api/health', methods=['GET'])
def health():
    return jsonify({'status': 'OK', 'message': 'Backend is running'})

@app.route('/api/hello', methods=['GET'])
def hello():
    return jsonify({'message': 'Hello from MARA Backend!'})

if __name__ == '__main__':
    print("🚀 MARA Backend Starting...")
    print("📡 Server running on http://localhost:5001")
    app.run(host='0.0.0.0', port=5001, debug=True) 