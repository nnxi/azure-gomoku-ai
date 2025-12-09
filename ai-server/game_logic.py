BOARD_SIZE = 15

def is_valid_move(board, row, col, color=None):
    # 1. 범위 및 빈칸 체크
    if not (0 <= row < BOARD_SIZE and 0 <= col < BOARD_SIZE):
        return False
    if board[row][col] != 0:
        return False
        
    # 2. 3-3 금지 룰 체크
    # color가 1일 때만 check_33을 수행
    if color == 1:
        if check_33(board, row, col, color):
            return False # 33이라서 못 둠

    return True

def check_33(board, row, col, color):
    """
    (row, col)에 돌을 뒀을 때 3-3(Double Three)이 되는지 확인
    """
    # 임시로 돌을 놔봄
    board[row][col] = color
    
    three_count = 0
    directions = [(0, 1), (1, 0), (1, 1), (1, -1)]
    
    for dr, dc in directions:
        if is_open_three(board, row, col, color, dr, dc):
            three_count += 1
            
    # 원상복구-
    board[row][col] = 0
    
    # 열린 3이 2개 이상이면 금지수
    if three_count >= 2:
        return True
    return False

def is_open_three(board, r, c, color, dr, dc):
    """
    특정 방향(dr, dc)으로 '열린 3'이 형성되는지 정밀 검사
    패턴: 01110, 010110, 011010 등 양쪽이 뚫린 3
    """
    # 현재 돌을 포함한 라인(총 9칸 정도)을 추출해서 분석
    line = []
    
    # -4칸 ~ +4칸까지 총 9칸을 가져옴
    for i in range(-4, 5):
        nr, nc = r + (dr * i), c + (dc * i)
        if 0 <= nr < BOARD_SIZE and 0 <= nc < BOARD_SIZE:
            line.append(board[nr][nc])
        else:
            line.append(-1) # 벽(장외)
            
    # 추출한 라인에서 패턴 매칭 (가운데 인덱스는 4)
    # 내 돌은 color, 빈칸은 0, 상대/벽은 -1로 치환해서 문자열로 만듦
    # 예: 0 1 1 1 0  -> "01110"
    
    s_line = ""
    for val in line:
        if val == color:
            s_line += "1" # 내 돌
        elif val == 0:
            s_line += "0" # 빈칸
        else:
            s_line += "X" # 벽이나 상대 돌
            
    # 열린 3 패턴 목록 (가운데 1이 방금 둔 돌이라고 가정)
    # 1. 01110 (연속 3)
    # 2. 011010 (한 칸 뜀)
    # 3. 010110 (한 칸 뜀)
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