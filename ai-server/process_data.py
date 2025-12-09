import numpy as np
import os
import glob

def process_gomocup_files(data_folder):
    print(f"📂 '{data_folder}' 폴더와 그 하위 폴더들을 탐색합니다...")
    
    # [수정된 부분] "**"와 recursive=True를 써서 하위 폴더까지 다 뒤집니다.
    search_pattern = os.path.join(data_folder, "**", "*")
    files = glob.glob(search_pattern, recursive=True)
    
    print(f"   - 발견된 전체 파일 개수: {len(files)}개 (폴더 포함)")
    
    X_data = [] 
    Y_data = []
    
    success_count = 0
    
    for filepath in files:
        # 폴더이거나, 우리가 찾는 데이터 파일이 아니면 패스
        if os.path.isdir(filepath):
            continue
        
        # 확장자가 .psq, .rec, .txt 인 것만 처리
        if not (filepath.endswith('.psq') or filepath.endswith('.rec') or filepath.endswith('.txt')):
            continue

        try:
            with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                lines = f.readlines()
        except:
            continue
            
        # 1. 헤더 체크
        if len(lines) < 1 or "Piskvorky" not in lines[0]:
            continue
            
        # 2. 바둑판 초기화
        board = np.zeros((15, 15), dtype=np.int8)
        current_color = 1 
        
        temp_X = []
        temp_Y = []
        is_valid_game = True
        
        # 3. 좌표 추출
        for line in lines[1:]:
            parts = line.strip().split(',')
            if len(parts) < 2: break 
            
            try:
                x = int(parts[0])
                y = int(parts[1])
                
                if x < 0 or y < 0: break
                
                # Gomocup 좌표 보정
                row = y - 1
                col = x - 1
                
                if not (0 <= row < 15 and 0 <= col < 15): break
                if board[row][col] != 0:
                    is_valid_game = False
                    break

                temp_X.append(board.copy())
                action = row * 15 + col
                temp_Y.append(action)
                
                board[row][col] = current_color
                current_color = 3 - current_color 
                
            except ValueError:
                break 

        if is_valid_game and len(temp_X) > 5:
            X_data.extend(temp_X)
            Y_data.extend(temp_Y)
            success_count += 1
            
        if success_count % 1000 == 0 and success_count > 0:
            print(f"   ... {success_count}개 게임 처리 완료 ({len(X_data)}개 수집됨)")

    print("🔄 데이터를 Numpy 배열로 변환 중...")
    X = np.array(X_data, dtype=np.int8)
    Y = np.array(Y_data, dtype=np.int16)
    
    print(f"✅ 변환 완료!")
    print(f"   - 총 읽은 게임 수: {success_count}판")
    print(f"   - 총 학습 데이터(수) 개수: {len(X)}")
    print(f"   - X 형태: {X.shape}") 
    print(f"   - Y 형태: {Y.shape}") 
    
    return X, Y

if __name__ == '__main__':
    data_path = 'data' 
    
    if os.path.exists(data_path):
        X, Y = process_gomocup_files(data_path)
        
        if len(X) > 0:
            np.save('data/dataset_x.npy', X)
            np.save('data/dataset_y.npy', Y)
            print("💾 저장 완료!")
        else:
            print("⚠️ 데이터가 없습니다.")
    else:
        print("❌ data 폴더가 없습니다.")