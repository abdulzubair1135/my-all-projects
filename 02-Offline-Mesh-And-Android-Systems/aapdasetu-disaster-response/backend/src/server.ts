import http from 'http';
import dotenv from 'dotenv';
import { Server as SocketIOServer } from 'socket.io';
import app from './app.js';
import { connectDB } from './config/db.js';
import { initSocket } from './sockets/socket.js';

dotenv.config();

const PORT = process.env.PORT || 5000;

const server = http.createServer(app);

const io = new SocketIOServer(server, {
  cors: {
    origin: '*',
    methods: ['GET', 'POST', 'PATCH', 'DELETE']
  }
});

initSocket(io);

const startServer = async () => {
  await connectDB();

  server.listen(PORT, () => {
    console.log(`====================================================`);
    console.log(`🚀 AapdaSetu Backend Server running on port ${PORT}`);
    console.log(`📡 WebSocket / Socket.IO listening on port ${PORT}`);
    console.log(`🛡️  "When the Network Fails, AapdaSetu Doesn't."`);
    console.log(`====================================================`);
  });
};

startServer().catch((err) => {
  console.error('Failed to start server:', err);
});
