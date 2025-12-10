import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader, Dataset
import numpy as np
import os
from model import GomokuNet # 방금 만든 두뇌 가져오기

# 환경 설정
BATCH_SIZE = 64     # 한 번에 64개씩
LEARNING_RATE = 0.001 # 학습 속도
EPOCHS = 10         # 학습 반복
DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")
print(f"학습 장치: {DEVICE}") # GPU 쓰는지 확인

# dataset 제작
class GomokuDataset(Dataset):
    def __init__(self, x_path, y_path):
        # npy 파일 불러옴
        self.X = np.load(x_path) 
        self.Y = np.load(y_path)
        
    def __len__(self):
        return len(self.X) # 전체 문제 개수
    
    def __getitem__(self, idx):
        # 문제와 정답 불러오기
        board = self.X[idx]
        target = self.Y[idx]
        
        # AI에게 보여줄 3가지 채널 만들기
        # 1. 흑돌 개수와 백돌 개수를 세서 차례 파악
        count1 = np.sum(board == 1)
        count2 = np.sum(board == 2)
        current_player = 1 if count1 == count2 else 2
        
        # (3, 15, 15) 크기의 빈 그릇 준비
        input_tensor = np.zeros((3, 15, 15), dtype=np.float32)
        
        # 채널 0: "내 돌이 어디 있지?" (공격/수비 판단용)
        input_tensor[0] = (board == current_player).astype(np.float32)
        # 채널 1: "상대 돌은 어디 있지?" (견제용)
        input_tensor[1] = (board == (3 - current_player)).astype(np.float32)
        # 채널 2: "빈 곳은 어디지?" (둘 수 있는 곳)
        input_tensor[2] = (board == 0).astype(np.float32)
        
        return torch.from_numpy(input_tensor), torch.tensor(target, dtype=torch.long)

# 학습 실행 코드
if __name__ == '__main__':
    # 데이터 파일 없으면 경고하고 끄기
    if not os.path.exists('../data/dataset_x.npy'):
        print("data 파일에 데이터가 없습니다.")
        exit()
        
    print("데이터 불러오는 중...")
    # 데이터를 잘게 쪼개서(Batch) 랜덤하게 섞어서(Shuffle) 줍니다.
    dataset = GomokuDataset('../data/dataset_x.npy', '../data/dataset_y.npy')
    loader = DataLoader(dataset, batch_size=BATCH_SIZE, shuffle=True)
    print(f"   - 총 문제 수: {len(dataset)}개")
    
    # 모델 소환
    model = GomokuNet().to(DEVICE)
    
    # 채점 기준표 (CrossEntropyLoss: 틀린 답을 고르면 벌점을 줌)
    criterion = nn.CrossEntropyLoss()
    
    # 점수 판단 (Adam Optimizer: 벌점을 보고 뇌를 수정해줌)
    optimizer = optim.Adam(model.parameters(), lr=LEARNING_RATE)
    
    print("훈련 시작")
    
    # 10번 반복 학습 (Epoch)
    for epoch in range(EPOCHS):
        total_loss = 0 # 이번 시험의 총 벌점
        correct = 0    # 맞춘 문제 수
        total = 0      # 푼 문제 수
        
        # 문제집 한 권 풀기 (Batch 단위로)
        for i, (inputs, labels) in enumerate(loader):
            # GPU로 데이터 보내기
            inputs, labels = inputs.to(DEVICE), labels.to(DEVICE)
            
            # 1. 풀기 (Forward)
            outputs = model(inputs)
            
            # 2. 채점 (Loss 계산)
            loss = criterion(outputs, labels)
            
            # 3. 복습하고 고침 (Backward & Optimization)
            optimizer.zero_grad() # 이전 기억 리셋
            loss.backward()       # 어디서 틀렸는지 역추적
            optimizer.step()      # 뇌 수정
            
            # 성적표 작성
            total_loss += loss.item()
            _, predicted = torch.max(outputs.data, 1) # AI가 고른 답
            total += labels.size(0)
            correct += (predicted == labels).sum().item() # 정답이랑 비교
            
            # 100번 풀 때마다 중간 보고
            if (i+1) % 100 == 0:
                print(f"   [Epoch {epoch+1}, {i+1}번째 묶음] 현재 오차: {loss.item():.4f}")
                
        # 한 권 다 풀었을 때 평균 점수
        avg_loss = total_loss / len(loader)
        accuracy = 100 * correct / total
        print(f"✨ {epoch+1}학년 수료! 평균 오차: {avg_loss:.4f}, 정답률: {accuracy:.2f}%")
        
        # 중간 저장
        torch.save(model.state_dict(), f"../data/model_epoch_{epoch+1}.pth")

    print("모든 학습 완료")
    # 최종 결과물 저장
    torch.save(model.state_dict(), "../data/best_model.pth")
    print("'best_model.pth' 저장 완료")