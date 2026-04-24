import { BrowserRouter, Routes, Route } from 'react-router-dom';
import Home from './pages/Home';
import Room from './pages/Room';
import NotFound from './pages/NotFound';
import { PongBackground } from './components/PongBackground/PongBackground';

export default function App() {
  return (
    <BrowserRouter>
      <PongBackground />
      <Routes>
        <Route path="/" element={<Home />} />
        <Route path="/:roomCode" element={<Room />} />
        <Route path="*" element={<NotFound />} />
      </Routes>
    </BrowserRouter>
  );
}
