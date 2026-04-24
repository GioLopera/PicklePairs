import styles from './TeamResult.module.css';

export function TeamResult({ result }) {
  if (!result) return null;

  return (
    <div className={styles.container}>
      <h3 className={styles.heading}>
        Teams — Run #{result.run_number}
      </h3>

      <div className={styles.teams}>
        {result.teams.map((team) => (
          <div key={team.team_number} className={styles.team}>
            <span className={styles.teamLabel}>Team {team.team_number}</span>
            <div className={styles.players}>
              {team.players.map((name) => (
                <span key={name} className={styles.player}>{name}</span>
              ))}
            </div>
          </div>
        ))}
      </div>

      {result.waiting_player && (
        <div className={styles.waiting}>
          <span className={styles.waitingIcon}>⏳</span>
          <div>
            <span className={styles.waitingLabel}>Waiting this round</span>
            <span className={styles.waitingName}>{result.waiting_player.player}</span>
          </div>
        </div>
      )}
    </div>
  );
}
