from flask import Flask, request, jsonify
from flask_cors import CORS
import random
import torch
import numpy as np
from src import game_logic
from src.model import GomokuNet  

app = Flask(__name__)
CORS(app)

# AI 모델 로드 (서버 켜질 때 한 번만 실행)
device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
model = GomokuNet()

try:
    # 저장된 가중치(best_model.pth) 불러오기
    model.load_state_dict(torch.load('data/best_model.pth', map_location=device))
    model.to(device)
    model.eval() # 평가 모드
except Exception as e:
    print(f"모델 로드 실패: {e}")
    model = None


# 데이터 전처리 함수 (보드 -> 3채널 텐서 변환)
def preprocess_board(board, ai_color):
    """
    입력: 15x15 2차원 리스트 (0, 1, 2)
    출력: (1, 3, 15, 15) 형태의 PyTorch Tensor
    채널 구성: [내 돌, 상대 돌, 빈 곳]
    """
    board_np = np.array(board)
    user_color = 1 if ai_color == 2 else 2

    # 채널 1: AI의 돌 위치 (1이면 1.0, 아니면 0.0)
    ch1 = (board_np == ai_color).astype(np.float32)
    
    # 채널 2: 유저의 돌 위치
    ch2 = (board_np == user_color).astype(np.float32)
    
    # 채널 3: 빈 공간 위치
    ch3 = (board_np == 0).astype(np.float32)

    # 3개를 합쳐서 (3, 15, 15)로 만듦
    input_data = np.stack([ch1, ch2, ch3])
    
    # 차원 추가 -> (1, 3, 15, 15)
    tensor_data = torch.tensor(input_data).unsqueeze(0)
    return tensor_data.to(device)

# 라우트 처리
@app.route('/calculate-move', methods=['POST'])
def calculate_move():
    data = request.get_json()
    board = data.get('board')     # 0:빈칸, 1:흑, 2:백
    user_move = data.get('userMove')

    # 1. 유저 착수 및 금지수 체크
    if user_move:
        ux = user_move['row']
        uy = user_move['col']
        if game_logic.check_33(board, ux, uy, 1):
            return jsonify({
                "error": "ILLEGAL_MOVE", 
                "message": "🚫 3-3 금지수입니다!"
            })
        board[ux][uy] = 1 # 유저 돌 반영

    ai_color = 2 

    # 2. 둘 수 있는 모든 자리(Valid Moves) 찾기
    valid_moves = []
    for r in range(15):
        for c in range(15):
            if game_logic.is_valid_move(board, r, c, color=ai_color):
                valid_moves.append((r, c))
    
    if not valid_moves:
        return jsonify({"error": "No moves left (Draw)"})

    # 3. AI 모델 예측 시작
    x, y = 0, 0

    if model:
        # (1) 전처리: 보드를 3채널 텐서로 변환
        input_tensor = preprocess_board(board, ai_color)

        # (2) 예측: 모델에 넣고 결과 받기
        with torch.no_grad():
            output = model(input_tensor) # 결과: (1, 225)
        
        # (3) 점수 가져오기 (1차원으로 펴기)
        scores = output.cpu().numpy().flatten()
        
        # (4) 이미 돌이 있는 자리는 절대 못 두게 점수를 -무한대로 만듦
        masked_scores = -np.inf * np.ones(225)
        
        for r, c in valid_moves:
            idx = r * 15 + c
            masked_scores[idx] = scores[idx] # 유효한 자리만 점수 복사

        # (5) 가장 점수 높은 자리(argmax) 선택
        best_idx = np.argmax(masked_scores)
        x = int(best_idx // 15)
        y = int(best_idx % 15)
        
        print(f"🤖 AI 모델 예측: ({x}, {y}) / 점수: {scores[best_idx]:.4f}")
        
    else:
        # 모델 로드 실패시 랜덤
        x, y = random.choice(valid_moves)

    # 4. 결과 반환
    board[x][y] = ai_color
    is_win = game_logic.check_win(board, x, y, ai_color)

    return jsonify({
        "x": x, 
        "y": y,
        "isWin": is_win 
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)