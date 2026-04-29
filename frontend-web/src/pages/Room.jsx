import { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useRoom, getCreatorToken, getPlayerName, savePlayerName } from '../hooks/useRoom';
import { joinRoom } from '../services/api';
import { PlayerChecklist } from '../components/PlayerChecklist/PlayerChecklist';
import { TeamResult } from '../components/TeamResult/TeamResult';
import { ShareButton } from '../components/ShareButton/ShareButton';
import styles from './Room.module.css';

function JoinOverlay({ roomCode, onJoined }) {
  const [name, setName] = useState('');
  const [isJoining, setIsJoining] = useState(false);
  const [error, setError] = useState(null);

  async function handleSubmit(e) {
    e.preventDefault();
    const trimmed = name.trim();
    if (!trimmed) return;
    setIsJoining(true);
    setError(null);
    try {
      await joinRoom(roomCode, trimmed);
      savePlayerName(roomCode, trimmed);
      onJoined();
    } catch (err) {
      setError(err.message);
      setIsJoining(false);
    }
  }

  return (
    <div className={styles.overlay}>
      <div className={styles.overlayCard}>
        <h2 className={styles.overlayTitle}>Join Room</h2>
        <p className={styles.overlayDesc}>
          Room <strong>{roomCode}</strong> — enter your name to join.
        </p>
        {error && <p className={styles.overlayError}>{error}</p>}
        <form onSubmit={handleSubmit} className={styles.overlayForm}>
          <input
            className={styles.overlayInput}
            type="text"
            placeholder="Your name"
            value={name}
            onChange={(e) => setName(e.target.value)}
            maxLength={50}
            autoFocus
            required
          />
          <button
            className={styles.overlayButton}
            type="submit"
            disabled={isJoining || !name.trim()}
          >
            {isJoining ? 'Joining...' : 'Join Room'}
          </button>
        </form>
      </div>
    </div>
  );
}

export default function Room() {
  const { roomCode } = useParams();
  const navigate = useNavigate();

  const isCreator = Boolean(getCreatorToken(roomCode));
  const alreadyJoined = Boolean(getPlayerName(roomCode));
  const [hasJoined, setHasJoined] = useState(isCreator || alreadyJoined);

  const {
    players,
    result,
    isRunning,
    error,
    roomClosed,
    canRun,
    handleRun,
    handleClose,
  } = useRoom(roomCode);

  useEffect(() => {
    if (roomClosed && isCreator) {
      navigate('/', { state: { toast: 'Room closed.' } });
    }
  }, [roomClosed, isCreator, navigate]);

  return (
    <div className={styles.page}>
      {!hasJoined && (
        <JoinOverlay roomCode={roomCode} onJoined={() => setHasJoined(true)} />
      )}

      <nav className={styles.navbar}>
        <div className={styles.navContainer}>
          <button className={styles.backLink} onClick={() => navigate('/')}>
            ← Back
          </button>
        </div>
      </nav>

      <header className={styles.header}>
        <h1 className={styles.roomTitle}>Room ID: {roomCode}</h1>
        <p className="srOnly">Pickleball room</p>
      </header>

      {error && <div className={styles.error}>{error}</div>}

      <main className={result ? styles.layout : styles.layoutSingle}>
        <section className={styles.section}>
          <div className={styles.sectionHeader}>
            <h2 className={styles.sectionTitle}>Players ({players.length})</h2>
            <ShareButton roomCode={roomCode} />
          </div>
          <PlayerChecklist players={players} />

          {isCreator && (
            <div className={styles.creatorActions}>
              <button
                className={styles.buttonRun}
                onClick={handleRun}
                disabled={!canRun || isRunning}
                title={!canRun ? 'Need at least 3 players' : ''}
              >
                {isRunning ? 'Generating...' : '🎲 Generate Teams'}
              </button>
              {!canRun && (
                <p className={styles.hint}>Need at least 3 players to generate teams.</p>
              )}
              <button className={styles.buttonClose} onClick={handleClose}>
                Close Room
              </button>
            </div>
          )}
        </section>

        {result && (
          <section className={styles.section}>
            <div className={styles.sectionHeader}>
              <h2 className={styles.sectionTitle}>Teams</h2>
            </div>
            <TeamResult result={result} />
          </section>
        )}
      </main>
    </div>
  );
}
