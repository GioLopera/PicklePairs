import { useState } from 'react';
import styles from './ShareButton.module.css';

export function ShareButton({ roomCode }) {
  const [copied, setCopied] = useState(false);

  const roomUrl = `${window.location.origin}/${roomCode}`;

  async function handleShare() {
    try {
      if (navigator.share) {
        await navigator.share({ title: 'Join my Pickleball Party room', url: roomUrl });
      } else {
        await navigator.clipboard.writeText(roomUrl);
        setCopied(true);
        setTimeout(() => setCopied(false), 2000);
      }
    } catch {
      // User cancelled share or clipboard failed — fail silently
    }
  }

  return (
    <button className={styles.button} onClick={handleShare}>
      {copied ? '✓ Copied!' : '🔗 Share Room'}
    </button>
  );
}
