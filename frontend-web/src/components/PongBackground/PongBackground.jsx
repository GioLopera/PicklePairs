import { useEffect, useRef } from 'react';

const PADDLE_WIDTH  = 10;
const PADDLE_HEIGHT = 60;
const PADDLE_OFFSET = 48;
const BALL_RADIUS   = 10;
const BALL_SIZE     = BALL_RADIUS * 2; // kept for physics references
const COLOR         = 'rgba(255, 255, 255, 0.18)';
const BALL_COLOR    = 'rgba(255, 255, 255, 0.18)';

export function PongBackground() {
  const canvasRef = useRef(null);

  useEffect(() => {
    const canvas = canvasRef.current;
    const ctx    = canvas.getContext('2d');
    let animId;

    const ball = { x: 0, y: 0, vx: 0, vy: 0 };
    const left  = { y: 0 };
    const right = { y: 0 };

    function speed() {
      // ~5 s to cross full width at 60 fps
      return canvas.width / (5 * 60 * 0.5);
    }

    function reset() {
      const { width, height } = canvas;
      ball.x  = width  / 2;
      ball.y  = height / 2;
      const angle = (Math.random() * Math.PI / 4) - Math.PI / 8;
      const s = speed();
      ball.vx = s * (Math.random() > 0.5 ? 1 : -1);
      ball.vy = s * Math.tan(angle);
      left.y  = height / 2 - PADDLE_HEIGHT / 2;
      right.y = height / 2 - PADDLE_HEIGHT / 2;
    }

    function resize() {
      canvas.width  = window.innerWidth;
      canvas.height = window.innerHeight;
      reset();
    }

    function update() {
      const { width, height } = canvas;

      // Move ball
      ball.x += ball.vx;
      ball.y += ball.vy;

      // Bounce top / bottom
      if (ball.y - BALL_SIZE / 2 < 0)      { ball.y = BALL_SIZE / 2;      ball.vy =  Math.abs(ball.vy); }
      if (ball.y + BALL_SIZE / 2 > height) { ball.y = height - BALL_SIZE / 2; ball.vy = -Math.abs(ball.vy); }

      // AI paddles — follow ball with slight lag so it looks natural
      const lag = speed() * 0.8;
      const lTarget = ball.y - PADDLE_HEIGHT / 2;
      const rTarget = ball.y - PADDLE_HEIGHT / 2;
      left.y  += Math.sign(lTarget - left.y)  * Math.min(Math.abs(lTarget - left.y),  lag);
      right.y += Math.sign(rTarget - right.y) * Math.min(Math.abs(rTarget - right.y), lag);

      // Clamp paddles
      left.y  = Math.max(0, Math.min(height - PADDLE_HEIGHT, left.y));
      right.y = Math.max(0, Math.min(height - PADDLE_HEIGHT, right.y));

      // Left paddle collision
      const lx = PADDLE_OFFSET + PADDLE_WIDTH;
      if (ball.x - BALL_SIZE / 2 < lx && ball.vx < 0 &&
          ball.y > left.y && ball.y < left.y + PADDLE_HEIGHT) {
        ball.x  = lx + BALL_SIZE / 2;
        ball.vx = Math.abs(ball.vx);
        // slight angle randomisation on hit
        ball.vy += (Math.random() - 0.5) * speed() * 0.4;
      }

      // Right paddle collision
      const rx = width - PADDLE_OFFSET - PADDLE_WIDTH;
      if (ball.x + BALL_SIZE / 2 > rx && ball.vx > 0 &&
          ball.y > right.y && ball.y < right.y + PADDLE_HEIGHT) {
        ball.x  = rx - BALL_SIZE / 2;
        ball.vx = -Math.abs(ball.vx);
        ball.vy += (Math.random() - 0.5) * speed() * 0.4;
      }

      // Ball out of bounds → reset rally
      if (ball.x < 0 || ball.x > width) reset();
    }

    function draw() {
      const { width, height } = canvas;

      // Background
      ctx.fillStyle = '#65AAC2';
      ctx.fillRect(0, 0, width, height);

      ctx.fillStyle  = COLOR;
      ctx.strokeStyle = COLOR;

      // Centre dotted line
      ctx.setLineDash([10, 14]);
      ctx.lineWidth = 4;
      ctx.beginPath();
      ctx.moveTo(width / 2, 0);
      ctx.lineTo(width / 2, height);
      ctx.stroke();
      ctx.setLineDash([]);

      // Top & bottom borders (retro look)
      ctx.fillRect(0, 0,          width, 6);
      ctx.fillRect(0, height - 6, width, 6);

      // Left paddle
      ctx.fillRect(PADDLE_OFFSET, left.y, PADDLE_WIDTH, PADDLE_HEIGHT);

      // Right paddle
      ctx.fillRect(width - PADDLE_OFFSET - PADDLE_WIDTH, right.y, PADDLE_WIDTH, PADDLE_HEIGHT);

      // Ball
      ctx.fillStyle = BALL_COLOR;
      ctx.beginPath();
      ctx.arc(ball.x, ball.y, BALL_RADIUS, 0, Math.PI * 2);
      ctx.fill();
    }

    function loop() {
      update();
      draw();
      animId = requestAnimationFrame(loop);
    }

    resize();
    window.addEventListener('resize', resize);
    loop();

    return () => {
      cancelAnimationFrame(animId);
      window.removeEventListener('resize', resize);
    };
  }, []);

  return (
    <canvas
      ref={canvasRef}
      aria-hidden="true"
      style={{ position: 'fixed', inset: 0, zIndex: 0, display: 'block' }}
    />
  );
}
