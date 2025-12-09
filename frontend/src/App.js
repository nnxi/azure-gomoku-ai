import React, { useState } from 'react';
import axios from 'axios';
import './App.css';

function App() {
  // 15x15 바둑판 만들기 (0: 빈칸, 1: 흑돌/나, 2: 백돌/AI)
  const [board, setBoard] = useState(Array(15).fill(null).map(() => Array(15).fill(0)));
  const [status, setStatus] = useState("당신의 차례입니다 (흑돌 ⚫)");

  const handleClick = async (row, col) => {
    // 이미 돌이 있거나 AI가 생각 중이면 클릭 금지
    if (board[row][col] !== 0 || status.includes("AI가 생각 중")) return;

    // 1. 내 돌(흑돌) 두기
    const newBoard = board.map(r => [...r]);
    newBoard[row][col] = 1; 
    setBoard(newBoard);

    if (checkWin(newBoard, row, col, 1)) {
        setStatus("🎉 당신의 승리입니다! (흑돌 승) 🎉");
        return; // 여기서 함수 종료
    }

    setStatus("AI가 생각 중... 🤖");

    try {
      // 2. 서버에 "나 여기에 뒀어!" 하고 보내기
      // 주의: Node서버 주소(3000번)를 정확히 적어야 합니다.
      const response = await axios.post('http://localhost:3000/api/play', {
        boardState: newBoard,
        userMove: { row: row, col: col }
      });

      if (response.data.error === "ILLEGAL_MOVE") {
          alert(response.data.message); 
          
          // 돌 물리기
          const rollbackBoard = board.map(r => [...r]); 
          rollbackBoard[row][col] = 0; // 방금 둔 곳을 0으로 되돌림
          setBoard(rollbackBoard); 
          
          setStatus("당신의 차례입니다 (흑돌 ⚫)");
          return; 
      }

      // 3. AI가 둔 수(백돌) 받아와서 업데이트
      const { x, y, isWin } = response.data; 
      
      console.log("AI 응답:", x, y);

      if (x !== undefined && y !== undefined) {
          newBoard[x][y] = 2; // 2는 백돌
          setBoard([...newBoard]); 

          if (isWin) {
              setStatus("😭 AI의 승리입니다... (백돌 승)");
              return;
          }
      }
      
      setStatus("당신의 차례입니다 (흑돌 ⚫)");

    } catch (error) {
      console.error("에러 발생:", error);
      setStatus("통신 에러! 터미널을 확인하세요.");
    }
  };

  // 오목 승리 판정 함수 (자바스크립트 버전)
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