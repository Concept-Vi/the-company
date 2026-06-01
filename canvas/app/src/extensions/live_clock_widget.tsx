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
    background: 'rgba(0, 0, 0, 0.75)',
    color: 'white',
    padding: '8px 16px',
    borderRadius: '8px',
    fontFamily: 'monospace',
    fontSize: '16px',
    zIndex: 9999,
    boxShadow: '0 2px 8px rgba(0,0,0,0.3)',
  };

  return <div style={style}>{time}</div>;
}
