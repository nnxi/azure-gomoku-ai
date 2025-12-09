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
    
    # [추가된 로직] 사용자의 수(흑돌)가 3-3인지 검사 (심판 개입)
    if user_move:
        ux = user_move['row']
        uy = user_move['col']
        
        # 흑돌(1) 입장에서 3-3인지 체크
        # 주의: check_33 함수는 시뮬레이션 후 자리를 0으로 비워버리는 특징이 있음.
        # 그래서 체크하고 나서 다시 1로 채워줘야 함.
        if game_logic.check_33(board, ux, uy, 1):
            return jsonify({
                "error": "ILLEGAL_MOVE", 
                "message": "🚫 3-3 금지수입니다! 다른 곳에 두세요."
            })
        
        # check_33이 시뮬레이션 하느라 지워버린 내 돌을 다시 복구! (중요)
        board[ux][uy] = 1
    
    # AI는 백돌(2)이라고 가정
    ai_color = 2 

    # 1. AI가 둘 수 있는 '모든 합법적인 자리' 찾기
    # (이미 둔 곳 제외, 흑돌이면 3-3 금지 자리 제외 등)
    valid_moves = []
    for r in range(15):
        for c in range(15):
            # AI(백돌) 입장에서 둘 수 있는지 체크
            if game_logic.is_valid_move(board, r, c, color=ai_color):
                valid_moves.append((r, c))
    
    # 2. 더 이상 둘 곳이 없다면? (무승부)
    if not valid_moves:
        return jsonify({"error": "No moves left (Draw)"})

    # 3. [지금은 랜덤] 나중엔 여기서 AI 모델이 최적의 수를 선택함
    # valid_moves 리스트 중에서 하나를 랜덤으로 뽑음
    x, y = random.choice(valid_moves)
    
    # 4. 승리 판정 (가상의 바둑판에 돌을 두고 체크해봄)
    board[x][y] = ai_color
    is_win = game_logic.check_win(board, x, y, ai_color)

    # 5. 결과 전송 (좌표 + 승리 여부)
    return jsonify({
        "x": x, 
        "y": y,
        "isWin": is_win 
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)