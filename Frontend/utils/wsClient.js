export function connectWS(onMessage) {
  const ws = new WebSocket("ws://localhost:8000/ws");
  
  ws.onmessage = (event) => {
    const data = JSON.parse(event.data);
    onMessage(data);
  };

  ws.onclose = () => console.log("WebSocket closed");
  ws.onerror = (err) => console.error(err);

  return ws;
}