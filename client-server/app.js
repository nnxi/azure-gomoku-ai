const express = require('express');
const axios = require('axios');
const app = express();

app.use(express.json());

const AI_SERVER_URL = process.env.AI_SERVER_URL || 'http://localhost:5000'; 

app.post('/api/play', async (req, res) => {
    try {
        const { boardState } = req.body; // 현재 오목판 배열

        const response = await axios.post(`${AI_SERVER_URL}/calculate-move`, {
            board: boardState
        });

        const aiMove = response.data;

        res.json({ success: true, aiMove });

    } catch (error) {
        console.error(error);
        res.status(500).json({ error: 'AI server error' });
    }
});

const PORT = process.env.PORT || 3000;

app.listen(PORT, () => console.log(`web server running on port ${PORT}`));