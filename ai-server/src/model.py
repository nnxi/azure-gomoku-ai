import torch
import torch.nn as nn

class GomokuNet(nn.Module):
    def __init__(self):
        super(GomokuNet, self).__init__()
        
        # [입력층]
        # 채널 3개: (1)내 돌 위치, (2)상대 돌 위치, (3)빈칸 위치
        # 이걸 64개의 특징(feature)으로 뻥튀기해서 분석합니다.
        self.conv1 = nn.Conv2d(in_channels=3, out_channels=64, kernel_size=3, padding=1)
        self.bn1 = nn.BatchNorm2d(64) # 데이터 값을 정규화
        self.relu = nn.ReLU() # 활성화 함수
        
        # [중간층]
        # 특징을 64개 -> 128개로 늘려서 더 디테일하게 봅니다.
        self.conv2 = nn.Conv2d(64, 128, kernel_size=3, padding=1)
        self.bn2 = nn.BatchNorm2d(128)
        
        # [중간층 2]
        # 128개 특징을 유지하면서 한 번 더 꼬아서 분석합니다.
        self.conv3 = nn.Conv2d(128, 128, kernel_size=3, padding=1)
        self.bn3 = nn.BatchNorm2d(128)
        
        # [요약층]
        # 결론을 내기 위해 특징을 128개 -> 64개로 줄입니다.
        self.conv4 = nn.Conv2d(128, 64, kernel_size=3, padding=1)
        self.bn4 = nn.BatchNorm2d(64)
        
        # [출력층]
        # 64개의 특징 지도를 15x15 바둑판 전체(225칸)에 대한 점수로 변환합니다.
        # 즉, 225개의 숫자(확률)가 나옵니다.
        self.fc = nn.Linear(64 * 15 * 15, 15 * 15) 

    # [실제 생각의 흐름]
    def forward(self, x):
        # x: 바둑판 상황 (Input)
        
        # 1~4단계: 눈으로 훑어보고 패턴 찾기
        x = self.relu(self.bn1(self.conv1(x)))
        x = self.relu(self.bn2(self.conv2(x)))
        x = self.relu(self.bn3(self.conv3(x)))
        x = self.relu(self.bn4(self.conv4(x)))
        
        # 5단계: 바둑판(2D)을 한 줄(1D)로 쭉 폄 (일렬로 세우기)
        x = x.view(x.size(0), -1) 
        
        # 6단계: 최종 점수 계산
        x = self.fc(x)
        return x