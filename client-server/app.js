const express = require('express');
const axios = require('axios');
const cors = require('cors');
const app = express();

app.use(cors());
app.use(express.json());

const AI_SERVER_URL = process.env.AI_SERVER_URL || 'http://localhost:5000'; 

app.post('/api/play', async (req, res) => {
    try {
        const { boardState, userMove } = req.body; 

        const response = await axios.post(`${AI_SERVER_URL}/calculate-move`, {
            board: boardState,
            userMove: userMove
        });

        // 파이썬의 응답 (정상 좌표 or 에러 메시지)
        const aiResponse = response.data;

        // 프론트로 그대로 전달
        res.json(aiResponse);

    } catch (error) {
        console.error(error);
        res.status(500).json({ error: 'AI server error' });
    }
});

const PORT = process.env.PORT || 3000;

app.listen(PORT, () => console.log(`web server running on port ${PORT}`));