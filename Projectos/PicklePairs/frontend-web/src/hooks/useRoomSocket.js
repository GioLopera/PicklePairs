import { useEffect, useRef } from 'react';

const WS_URL = import.meta.env.VITE_WS_URL ?? 'ws://localhost:8000';

/**
 * Connects to the room WebSocket and fires callbacks on incoming events.
 * Automatically reconnects if the connection drops unexpectedly.
 */
export function useRoomSocket(roomCode, { onPlayerJoined, onTeamsGenerated, onRoomClosed } = {}) {
  const callbacksRef = useRef({ onPlayerJoined, onTeamsGenerated, onRoomClosed });

  // Keep callbacks ref current without re-running the effect
  useEffect(() => {
    callbacksRef.current = { onPlayerJoined, onTeamsGenerated, onRoomClosed };
  });

  useEffect(() => {
    if (!roomCode) return;

    let ws;
    let shouldReconnect = true;

    function connect() {
      ws = new WebSocket(`${WS_URL}/ws/${roomCode}`);

      ws.onmessage = (event) => {
        let data;
        try {
          data = JSON.parse(event.data);
        } catch {
          return;
        }

        const { onPlayerJoined, onTeamsGenerated, onRoomClosed } = callbacksRef.current;
        if (data.type === 'player_joined') onPlayerJoined?.(data.player);
        if (data.type === 'teams_generated') onTeamsGenerated?.(data.result);
        if (data.type === 'room_closed') onRoomClosed?.();
      };

      ws.onclose = () => {
        if (shouldReconnect) {
          // Reconnect after 2 seconds if closed unexpectedly
          setTimeout(connect, 2000);
        }
      };
    }

    connect();

    return () => {
      shouldReconnect = false;
      ws?.close();
    };
  }, [roomCode]);
}
