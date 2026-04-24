import { useEffect, useState } from 'react';
import styles from './Toast.module.css';

export function Toast({ message, duration = 3000, onDone }) {
  const [visible, setVisible] = useState(true);

  useEffect(() => {
    const hide = setTimeout(() => setVisible(false), duration);
    const done = setTimeout(() => onDone?.(), duration + 300);
    return () => { clearTimeout(hide); clearTimeout(done); };
  }, [duration, onDone]);

  if (!message) return null;

  return (
    <div className={`${styles.snackbar} ${visible ? styles.show : styles.hide}`}>
      {message}
    </div>
  );
}
