import { useState } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { createRoom, joinRoom } from '../services/api';
import { saveCreatorToken, savePlayerName } from '../hooks/useRoom';
import { Toast } from '../components/Toast/Toast';
import styles from './Home.module.css';

export default function Home() {
  const navigate = useNavigate();
  const location = useLocation();
  const [toast, setToast] = useState(location.state?.toast ?? null);

  const [view, setView] = useState('create'); // 'create' | 'join'
  const [roomName, setRoomName] = useState('');
  const [creatorName, setCreatorName] = useState('');
  const [roomCode, setRoomCode] = useState('');
  const [playerName, setPlayerName] = useState('');
  const [isCreating, setIsCreating] = useState(false);
  const [isJoining, setIsJoining] = useState(false);
  const [error, setError] = useState(null);

  function switchView(next) {
    setError(null);
    setView(next);
  }

  async function handleCreateRoom(e) {
    e.preventDefault();
    setIsCreating(true);
    setError(null);
    try {
      const room = await createRoom(roomName);
      saveCreatorToken(room.room_code, room.creator_token);
      const name = creatorName.trim();
      if (name) {
        await joinRoom(room.room_code, name);
        savePlayerName(room.room_code, name);
      }
      navigate(`/${room.room_code}`);
    } catch (err) {
      setError(err.message);
      setIsCreating(false);
    }
  }

  async function handleJoinRoom(e) {
    e.preventDefault();
    setIsJoining(true);
    setError(null);
    try {
      const code = roomCode.trim();
      await joinRoom(code, playerName.trim());
      savePlayerName(code, playerName.trim());
      navigate(`/${code}`);
    } catch (err) {
      setError(err.message);
      setIsJoining(false);
    }
  }

  return (
    <>
    <div className={styles.page}>
      {toast && <Toast message={toast} onDone={() => setToast(null)} />}
      <header className={styles.header}>
        <h1 className={styles.logo}>Pickle Pick a Pair</h1>
        <p className={styles.tagline}>Random pickleball teams.</p>
      </header>

      {error && <div className={styles.error}>{error}</div>}

      <main className={styles.cards}>
        {view === 'create' ? (
          <div className={styles.card}>
            <h2 className="srOnly">Open a New Room</h2>
            <p className="srOnly">Start a room and share the link with your group.</p>
            <form onSubmit={handleCreateRoom} className={styles.form}>
              <input
                className={styles.input}
                type="text"
                placeholder="Room name (optional)"
                value={roomName}
                onChange={(e) => setRoomName(e.target.value)}
                maxLength={100}
              />
              <input
                className={styles.input}
                type="text"
                placeholder="Your name (optional)"
                value={creatorName}
                onChange={(e) => setCreatorName(e.target.value)}
                maxLength={50}
              />
              <p className={styles.inputHint}>If you are a player, enter your name.</p>
              <button className={styles.buttonPrimary} type="submit" disabled={isCreating}>
                {isCreating ? 'Creating...' : 'Open New Room'}
              </button>
            </form>
            <button className={styles.switchLink} onClick={() => switchView('join')}>
              Join a Room
            </button>
          </div>
        ) : (
          <div className={styles.card}>
            <h2 className="srOnly">Join a Room</h2>
            <p className="srOnly">Enter a Room ID and your name to join.</p>
            <form onSubmit={handleJoinRoom} className={styles.form}>
              <input
                className={styles.input}
                type="text"
                placeholder="Room ID"
                value={roomCode}
                onChange={(e) => setRoomCode(e.target.value)}
                required
                maxLength={8}
                autoCapitalize="none"
              />
              <input
                className={styles.input}
                type="text"
                placeholder="Your name"
                value={playerName}
                onChange={(e) => setPlayerName(e.target.value)}
                required
                maxLength={50}
              />
              <button
                className={styles.buttonPrimary}
                type="submit"
                disabled={isJoining || !roomCode.trim() || !playerName.trim()}
              >
                {isJoining ? 'Joining...' : 'Join Room'}
              </button>
            </form>
            <button className={styles.switchLink} onClick={() => switchView('create')}>
              Open a New Room
            </button>
          </div>
        )}
      </main>
    </div>
    </>
  );
}
