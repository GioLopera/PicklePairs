import styles from './PlayerChecklist.module.css';

export function PlayerChecklist({ players }) {
  if (players.length === 0) {
    return <p className={styles.empty}>Waiting for players to join...</p>;
  }

  return (
    <ul className={styles.list}>
      {players.map((player) => (
        <li key={player.id} className={styles.item}>
          <span className={styles.check}>✓</span>
          <span className={styles.name}>{player.name}</span>
        </li>
      ))}
    </ul>
  );
}
