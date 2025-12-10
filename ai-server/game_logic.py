BOARD_SIZE = 15

# 수를 둘 수 있는 자리인지 체크
def is_valid_move(board, row, col, color=None):

    if not (0 <= row < BOARD_SIZE and 0 <= col < BOARD_SIZE):
        return False
    if board[row][col] != 0:
        return False
        
    # 33 체크
    if color == 1:
        if check_33(board, row, col, color):
            return False # 33이라서 못 둠

    return True

def check_33(board, row, col, color):
    # 돌 두고 판단
    board[row][col] = color
    
    three_count = 0
    directions = [(0, 1), (1, 0), (1, 1), (1, -1)]
    
    for dr, dc in directions:
        if is_open_three(board, row, col, color, dr, dc):
            three_count += 1
            
    # 원상복구
    board[row][col] = 0
    
    if three_count >= 2:
        return True
    return False

# 열린 3인지 체크
def is_open_three(board, r, c, color, dr, dc):
    line = []
    
    # -4칸 ~ +4칸까지 총 9칸을 가져옴
    for i in range(-4, 5):
        nr, nc = r + (dr * i), c + (dc * i)
        if 0 <= nr < BOARD_SIZE and 0 <= nc < BOARD_SIZE:
            line.append(board[nr][nc])
        else:
            line.append(-1) # 벽
            
    # 추출한 라인으로 패턴 매치
    s_line = ""
    for val in line:
        if val == color:
            s_line += "1"
        elif val == 0:
            s_line += "0"
        else:
            s_line += "X"
            
    # 열린 3 패턴 목록
    patterns = ["01110", "011010", "010110"]
    
    for p in patterns:
        if p in s_line:
            return True
            
    return False

def check_win(board, row, col, color):
    directions = [(0, 1), (1, 0), (1, 1), (1, -1)]
    for dr, dc in directions:
        count = 1
        r, c = row + dr, col + dc
        while 0 <= r < BOARD_SIZE and 0 <= c < BOARD_SIZE and board[r][c] == color:
            count += 1
            r += dr
            c += dc
        r, c = row - dr, col - dc
        while 0 <= r < BOARD_SIZE and 0 <= c < BOARD_SIZE and board[r][c] == color:
            count += 1
            r -= dr
            c -= dc
        if count >= 5:
            return True
    return False

def check_draw(board):
    for row in board:
        if 0 in row:
            return False
    return True