const BASE_URL = import.meta.env.VITE_API_URL ?? 'http://localhost:8000';

async function request(path, options = {}) {
  const res = await fetch(`${BASE_URL}${path}`, {
    headers: { 'Content-Type': 'application/json', ...options.headers },
    ...options,
  });

  if (res.status === 204) return null;

  const data = await res.json().catch(() => null);

  if (!res.ok) {
    const message = data?.detail ?? `Request failed: ${res.status}`;
    throw new Error(message);
  }

  return data;
}

export async function createRoom(name) {
  return request('/rooms/', {
    method: 'POST',
    body: JSON.stringify({ name: name || null }),
  });
}

export async function getRoom(roomCode) {
  return request(`/rooms/${roomCode}`);
}

export async function closeRoom(roomCode, creatorToken) {
  return request(`/rooms/${roomCode}`, {
    method: 'DELETE',
    headers: { 'x-creator-token': creatorToken },
  });
}

export async function joinRoom(roomCode, playerName) {
  return request(`/rooms/${roomCode}/players`, {
    method: 'POST',
    body: JSON.stringify({ name: playerName }),
  });
}

export async function listPlayers(roomCode) {
  return request(`/rooms/${roomCode}/players`);
}

export async function runTeams(roomCode, creatorToken) {
  return request(`/rooms/${roomCode}/run`, {
    method: 'POST',
    headers: { 'x-creator-token': creatorToken },
  });
}

export async function getLatestResult(roomCode) {
  return request(`/rooms/${roomCode}/results/latest`);
}
