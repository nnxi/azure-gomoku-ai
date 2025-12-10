from flask import Flask, request, jsonify
from flask_cors import CORS  # [중요] 이게 있어야 리액트랑 통신됨
import random
import game_logic  # 방금 만든 게임 로직 파일 불러오기

app = Flask(__name__)
CORS(app)  # 모든 접속 허용

@app.route('/calculate-move', methods=['POST'])
def calculate_move():
    data = request.get_json()
    board = data.get('board')
    user_move = data.get('userMove') # 프론트에서 보낸 좌표 받기
    
    # 흑돌이 3-3인지 검사
    if user_move:
        ux = user_move['row']
        uy = user_move['col']
        
        # 3-3인지 체크
        if game_logic.check_33(board, ux, uy, 1):
            return jsonify({
                "error": "ILLEGAL_MOVE", 
                "message": "🚫 3-3 금지수입니다! 다른 곳에 두세요."
            })
        
        # 돌 복구
        board[ux][uy] = 1

    ai_color = 2 

    valid_moves = []
    for r in range(15):
        for c in range(15):
            if game_logic.is_valid_move(board, r, c, color=ai_color):
                valid_moves.append((r, c))
    
    # 빈 칸 없으면 무승부
    if not valid_moves:
        return jsonify({"error": "No moves left (Draw)"})

    x, y = random.choice(valid_moves)
    
    # 승리 판정
    board[x][y] = ai_color
    is_win = game_logic.check_win(board, x, y, ai_color)

    return jsonify({
        "x": x, 
        "y": y,
        "isWin": is_win 
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)