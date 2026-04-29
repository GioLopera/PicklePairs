import { useNavigate } from 'react-router-dom';
import styles from './Home.module.css';

export default function NotFound() {
  const navigate = useNavigate();
  return (
    <div className={styles.page}>
      <header className={styles.header}>
        <h1 className={styles.logo}>🏓 PicklePairs</h1>
        <p className={styles.tagline}>Page not found.</p>
      </header>
      <button className={styles.buttonPrimary} onClick={() => navigate('/')}>
        Go Home
      </button>
    </div>
  );
}
