from flask import Flask, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)


@app.route('/')
def hello():
    return "Server is running!"


@app.route('/test', methods=['GET', 'POST'])
def test():
    return jsonify({"status": "success", "message": "API is working"})


if __name__ == '__main__':
    print("Starting test server on http://localhost:5000")
    app.run(host='0.0.0.0', port=5000, debug=True)
