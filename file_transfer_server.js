const express = require('express');
const http = require('http');
const WebSocket = require('ws');
const fs = require('fs');
const path = require('path');
const bodyParser = require('body-parser');

const app = express();
const server = http.createServer(app);
const wss = new WebSocket.Server({ server });

const DATA_DIR = path.join(__dirname, 'datafile');
const MESSAGE_HISTORY_FILE = path.join(__dirname, 'message_history.json');

if (!fs.existsSync(DATA_DIR)) fs.mkdirSync(DATA_DIR);

let clients = {};
let messages = loadJsonFile(MESSAGE_HISTORY_FILE, []);

app.use(bodyParser.json());
app.use(express.static(path.join(__dirname, 'templates')));

// Middleware to log all incoming requests
app.use((req, res, next) => {
    const timestamp = new Date().toISOString();
    const [date, time] = timestamp.split('T'); // Split date and time
    const ip = req.socket.remoteAddress;
    console.log(`Date: ${date} | Time: ${time.split('.')[0]} | IP: ${ip}`);
    next();
});

function loadJsonFile(filePath, defaultValue) {
    if (fs.existsSync(filePath)) {
        const content = fs.readFileSync(filePath, 'utf-8').trim();
        return content ? JSON.parse(content) : defaultValue;
    }
    return defaultValue;
}

function saveJsonFile(filePath, data) {
    fs.writeFileSync(filePath, JSON.stringify(data, null, 4));
}

app.get('/', (req, res) => {
    res.sendFile(path.join(__dirname, 'templates', 'index.html'));
});

app.get('/devices', (req, res) => {
    res.json(Object.keys(clients));
});

app.post('/send_request', (req, res) => {
    const { sender_id, target_id } = req.body;
    if (clients[target_id]) {
        clients[target_id].send(JSON.stringify({ type: 'REQUEST', sender_id }));
        res.json({ status: 'Request sent' });
    } else {
        res.status(404).json({ status: 'Target not found' });
    }
});

app.post('/send_file', (req, res) => {
    const { sender_id, file_name, file_data } = req.body;
    if (sender_id && file_name && file_data) {
        const timestamp = new Date().toISOString();
        const newMessage = { sender_id, file_name, file_data, timestamp };
        messages.push(newMessage);
        saveJsonFile(MESSAGE_HISTORY_FILE, messages);
        res.status(204).send(); // Return no content
    } else {
        res.status(400).json({ status: 'Invalid data' });
    }
});

app.get('/messages', (req, res) => {
    messages = loadJsonFile(MESSAGE_HISTORY_FILE, []);
    res.json(messages.slice(-50));
});

app.post('/send_message', (req, res) => {
    const { sender_id, message } = req.body;
    if (sender_id && message) {
        const timestamp = new Date().toISOString();
        const newMessage = { sender_id, message, timestamp };
        messages.push(newMessage);
        saveJsonFile(MESSAGE_HISTORY_FILE, messages);
        res.json({ status: 'Message sent' });
    } else {
        res.status(400).json({ status: 'Invalid data' });
    }
});

app.post('/send_image', (req, res) => {
    const { sender_id, image_data, image_name } = req.body;
    if (sender_id && image_data && image_name) {
        const timestamp = new Date().toISOString();
        const imagePath = path.join(DATA_DIR, `${timestamp}_${image_name}`);
        
        // Decode Base64 and save the image
        const imageBuffer = Buffer.from(image_data, 'base64');
        fs.writeFileSync(imagePath, imageBuffer);

        const newMessage = { sender_id, image_name, timestamp, image_path: imagePath };
        messages.push(newMessage);
        saveJsonFile(MESSAGE_HISTORY_FILE, messages);

        res.json({ status: 'Image saved successfully', image_path: imagePath });
    } else {
        res.status(400).json({ status: 'Invalid data' });
    }
});

wss.on('connection', (ws, req) => {
    const ip = req.socket.remoteAddress;
    clients[ip] = ws;

    ws.send(JSON.stringify({ type: 'ID', clientId: ip }));

    ws.on('message', (message) => {
        // Handle incoming WebSocket messages if needed
    });

    ws.on('close', () => {
        delete clients[ip];
    });
});

server.listen(8001, 'localhost', () => {
    console.log('Server started on http://localhost:8001');
});
