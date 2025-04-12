import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import './App.css';

// Components
import Header from './components/Header';
import Home from './components/Home';
import PropertyList from './components/PropertyList';
import PropertyForm from './components/PropertyForm';
import ChatInterface from './components/ChatInterface';

function App() {
  return (
    <Router>
      <div className="app">
        <Header />
        <main className="main-content">
          <Routes>
            <Route path="/" element={<Home />} />
            <Route path="/properties" element={<PropertyList />} />
            <Route path="/add-property" element={<PropertyForm />} />
            <Route path="/chat" element={<ChatInterface />} />
          </Routes>
        </main>
        <footer className="footer">
          <p>&copy; {new Date().getFullYear()} Leasa - AI Real Estate Agent</p>
        </footer>
      </div>
    </Router>
  );
}

export default App;
