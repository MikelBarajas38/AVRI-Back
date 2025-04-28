// project-root/server.js
const express = require('express');
const cors = require('cors');
const path = require('path');
const chats    = require('./data/chats.json');
const messages = require('./data/messages.json');
const users    = require('./data/users.json');

const app = express();
const PORT = process.env.PORT || 8080;

app.use(cors());
app.use(express.json());

// 1) Listar todos los chats
app.get('/api/chats', (req, res) => {
  res.json({ chats });
});

// 2) Listar mensajes de un chat concreto (p.ej. /api/messages?idChat=1)
app.get('/api/messages', (req, res) => {
  const idChat = parseInt(req.query.idChat, 10);
  const filtered = messages.filter(m => m.idChat === idChat);
  res.json({ messages: filtered });
});

// 3) Listar usuarios
app.get('/api/users', (req, res) => {
  res.json({ users });
});

// 4) Enviar un mensaje al asistente
app.post('/api/chat', (req, res) => {
  const { idChat, text } = req.body;
  if (typeof idChat !== 'number' || !text) {
    return res.status(400).json({ error: 'Parámetros inválidos' });
  }
  // Simulamos respuesta “system”
  const reply = {
    id: Date.now(),
    idChat,
    type: 'system',
    text: `Recibí tu mensaje: "${text}"`
  };
  res.json(reply);
});

// 5) (OPCIONAL) servir Angular en producción
app.use(express.static(path.join(__dirname, 'dist/avri')));
app.get('*', (req, res) => {
  res.sendFile(path.join(__dirname, 'dist/avri/index.html'));
});

app.listen(PORT, () => {
  console.log(`API corriendo en http://localhost:${PORT}`);
});
