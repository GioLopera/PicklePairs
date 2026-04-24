import { useState, useEffect, useCallback } from 'react';
import { listPlayers, getLatestResult, runTeams, closeRoom } from '../services/api';
import { useRoomSocket } from './useRoomSocket';

const CREATOR_TOKEN_KEY = (roomCode) => `picklepairs_creator_${roomCode}`;
const PLAYER_NAME_KEY = (roomCode) => `picklepairs_player_${roomCode}`;

export function saveCreatorToken(roomCode, token) {
  localStorage.setItem(CREATOR_TOKEN_KEY(roomCode), token);
}

export function getCreatorToken(roomCode) {
  return localStorage.getItem(CREATOR_TOKEN_KEY(roomCode));
}

export function savePlayerName(roomCode, name) {
  localStorage.setItem(PLAYER_NAME_KEY(roomCode), name);
}

export function getPlayerName(roomCode) {
  return localStorage.getItem(PLAYER_NAME_KEY(roomCode));
}

/**
 * Manages all state for a room: players, team results, errors, and loading.
 */
export function useRoom(roomCode) {
  const [players, setPlayers] = useState([]);
  const [result, setResult] = useState(null);
  const [isRunning, setIsRunning] = useState(false);
  const [error, setError] = useState(null);
  const [roomClosed, setRoomClosed] = useState(false);

  const creatorToken = roomCode ? getCreatorToken(roomCode) : null;
  const isCreator = Boolean(creatorToken);

  // Initial data load
  useEffect(() => {
    if (!roomCode) return;

    listPlayers(roomCode)
      .then(setPlayers)
      .catch(() => setError('Could not load players.'));

    getLatestResult(roomCode)
      .then(setResult)
      .catch(() => {/* no result yet is fine */});
  }, [roomCode]);

  // Real-time updates
  useRoomSocket(roomCode, {
    onPlayerJoined: (player) => {
      setPlayers((prev) => {
        // Avoid duplicates in case HTTP and WS race
        if (prev.some((p) => p.id === player.id)) return prev;
        return [...prev, player];
      });
    },
    onTeamsGenerated: (newResult) => {
      setResult(newResult);
    },
    onRoomClosed: () => {
      setRoomClosed(true);
    },
  });

  const handleRun = useCallback(async () => {
    if (!creatorToken) return;
    setIsRunning(true);
    setError(null);
    try {
      const newResult = await runTeams(roomCode, creatorToken);
      setResult(newResult);
    } catch (e) {
      setError(e.message);
    } finally {
      setIsRunning(false);
    }
  }, [roomCode, creatorToken]);

  const handleClose = useCallback(async () => {
    if (!creatorToken) return;
    try {
      await closeRoom(roomCode, creatorToken);
      setRoomClosed(true);
    } catch (e) {
      setError(e.message);
    }
  }, [roomCode, creatorToken]);

  return {
    players,
    result,
    isRunning,
    error,
    roomClosed,
    isCreator,
    canRun: players.length >= 3,
    handleRun,
    handleClose,
  };
}
