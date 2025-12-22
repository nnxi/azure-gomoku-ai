import React, { useState } from 'react';
import axios from 'axios';
import './App.css';

const API_URL = 'https://gomoku-backend-jh.azurewebsites.net';

function App() {
  // 0: 빈칸, 1: 흑돌, 2: 백돌
  const [board, setBoard] = useState(Array(15).fill(null).map(() => Array(15).fill(0)));
  const [status, setStatus] = useState("당신의 차례입니다 (흑돌 ⚫)");
  const [isGameOver, setIsGameOver] = useState(false); // 게임 종료 여부 체크

  // 게임 초기화 함수
  const resetGame = () => {
    setBoard(Array(15).fill(null).map(() => Array(15).fill(0)));
    setStatus("당신의 차례입니다 (흑돌 ⚫)");
    setIsGameOver(false);
  };

  const handleClick = async (row, col) => {
    // 1. 이미 돌이 있거나
    // 2. AI가 생각 중이거나
    // 3. 게임이 끝났으면(isGameOver) --> 클릭 무시
    if (board[row][col] !== 0 || status.includes("AI가 생각 중") || isGameOver) return;

    // --- 유저(흑돌) 착수 ---
    const newBoard = board.map(r => [...r]);
    newBoard[row][col] = 1; 
    setBoard(newBoard);

    // 유저 승리 체크
    if (checkWin(newBoard, row, col, 1)) {
        setStatus("🎉 당신의 승리입니다! (흑돌 승) 🎉");
        setIsGameOver(true); // 게임 종료 상태로 변경
        return;
    }

    setStatus("AI가 생각 중... 🤖");

    try {
      const response = await axios.post(`${API_URL}/calculate-move`, {
        board: newBoard,       // 백엔드가 받는 변수명 'board'로 수정
        userMove: { row: row, col: col }
      });

      // 3-3 금지수 처리
      if (response.data.error === "ILLEGAL_MOVE") {
          alert(response.data.message); 
          
          // 돌 물리기
          const rollbackBoard = board.map(r => [...r]); 
          rollbackBoard[row][col] = 0; 
          setBoard(rollbackBoard); 
          
          setStatus("당신의 차례입니다 (흑돌 ⚫)");
          return; 
      }

      // --- AI(백돌) 착수 ---
      const { x, y, isWin } = response.data; 
      
      console.log("AI 응답:", x, y);

      if (x !== undefined && y !== undefined) {
          // AI가 둔 곳에 백돌(2) 표시
          // 주의: 리액트 상태 업데이트를 위해 새 배열 생성
          const aiBoard = newBoard.map(r => [...r]);
          aiBoard[x][y] = 2;
          setBoard(aiBoard); 

          if (isWin) {
              setStatus("😭 AI의 승리입니다... (백돌 승)");
              setIsGameOver(true); // 게임 종료 상태로 변경
              return;
          }
      }
      
      setStatus("당신의 차례입니다 (흑돌 ⚫)");

    } catch (error) {
      console.error("에러 발생:", error);
      setStatus("통신 에러! 백엔드 서버가 켜져 있나요?");
      
      // 에러 나면 돌 물려주기
      const rollbackBoard = board.map(r => [...r]); 
      rollbackBoard[row][col] = 0; 
      setBoard(rollbackBoard); 
    }
  };

  // 승리 체크 로직 (기존 유지)
  const checkWin = (board, row, col, color) => {
    const directions = [
      [0, 1],   // 가로
      [1, 0],   // 세로
      [1, 1],   // 대각선 \
      [1, -1]   // 대각선 /
    ];

    for (let [dr, dc] of directions) {
      let count = 1;

      // 정방향 탐색
      let r = row + dr;
      let c = col + dc;
      while (r >= 0 && r < 15 && c >= 0 && c < 15 && board[r][c] === color) {
        count++;
        r += dr;
        c += dc;
      }

      // 역방향 탐색
      r = row - dr;
      c = col - dc;
      while (r >= 0 && r < 15 && c >= 0 && c < 15 && board[r][c] === color) {
        count++;
        r -= dr;
        c -= dc;
      }

      if (count >= 5) return true;
    }
    return false;
  };

  return (
    <div className="game-container">
      <h1>Azure Gomoku AI</h1>
      <div className="status">{status}</div>
      
      {/* 게임이 끝났을 때만 버튼 표시 */}
      {isGameOver && (
          <button className="restart-btn" onClick={resetGame}>
            게임 다시하기 🔄
          </button>
      )}

      <div className="board">
        {board.map((row, rowIndex) => (
          <div key={rowIndex} className="board-row">
            {row.map((cell, colIndex) => (
              <div 
                key={colIndex} 
                className={`cell ${cell === 1 ? 'black' : cell === 2 ? 'white' : ''}`}
                onClick={() => handleClick(rowIndex, colIndex)}
              ></div>
            ))}
          </div>
        ))}
      </div>
    </div>
  );
}

export default App;