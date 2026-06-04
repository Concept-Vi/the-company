import { useState, useEffect } from 'react';

function formatTime() {
  const now = new Date();
  const hours = String(now.getHours()).padStart(2, '0');
  const minutes = String(now.getMinutes()).padStart(2, '0');
  const seconds = String(now.getSeconds()).padStart(2, '0');
  return `${hours}:${minutes}:${seconds}`;
}

export default function live_clock_widget() {
  const [time, setTime] = useState(formatTime());

  useEffect(() => {
    const intervalId = setInterval(() => {
      setTime(formatTime());
    }, 1000);
    return () => clearInterval(intervalId);
  }, []);

  const style = {
    position: 'fixed',
    top: '10px',
    right: '10px',
    background: 'var(--s0)',
    color: 'var(--tx)',
    padding: '8px 16px',
    borderRadius: 'var(--r-lg)',
    fontFamily: 'monospace',
    fontSize: '16px',
    zIndex: 9999,
    boxShadow: 'var(--shadow)',
  };

  return <div style={style}>{time}</div>;
}
