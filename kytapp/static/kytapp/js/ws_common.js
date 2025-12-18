// 共通 WebSocket 生存確認
function startPing(socket) {
  setInterval(() => {
    if (socket && socket.readyState === WebSocket.OPEN) {
      socket.send(JSON.stringify({ type: "ping" }));
    }
  }, 30000); // 30秒
}

// 安全送信
function safeSend(socket, data) {
  if (socket && socket.readyState === WebSocket.OPEN) {
    socket.send(JSON.stringify(data));
  } else {
    console.warn("⚠ WebSocket not open:", data);
  }
}
