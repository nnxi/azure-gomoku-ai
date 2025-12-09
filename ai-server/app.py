from flask import Flask, request, jsonify
import random
import time

app = Flask(__name__)

@app.route('/calculate-move', methods=['POST'])

def calculate_move():
    data = request.json
    board = data.get('board')

    x = random.randint(0, 14)
    y = random.randint(0, 14)

    return jsonify({"x": x, "y": y})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)