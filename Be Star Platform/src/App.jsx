import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Navbar from './components/Navbar';
import Footer from './components/Footer';
import ChatWidget from './components/ChatWidget';
import Home from './pages/Home';
import About from './pages/About';
import Tickets from './pages/Tickets';
import Speakers from './pages/Speakers';
import Sessions from './pages/Sessions';
import Sponsors from './pages/Sponsors';
import AIFeatures from './pages/AIFeatures';

function App() {
  return (
    <Router>
      <Navbar />
      <Routes>
        <Route path="/" element={<Home />} />
        <Route path="/about" element={<About />} />
        <Route path="/tickets" element={<Tickets />} />
        <Route path="/speakers" element={<Speakers />} />
        <Route path="/sessions" element={<Sessions />} />
        <Route path="/sponsors" element={<Sponsors />} />
        <Route path="/ai-features" element={<AIFeatures />} />
      </Routes>
      <Footer />
      <ChatWidget />
    </Router>
  );
}

export default App;
