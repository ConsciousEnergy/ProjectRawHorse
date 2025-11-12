import { useEffect, useState } from 'react';
import { BrowserRouter as Router, Routes, Route, Link, useLocation } from 'react-router-dom';
import { Home, Database, BarChart3, FileDown, Upload, Info } from 'lucide-react';

import Dashboard from './pages/Dashboard';
import Browse from './pages/Browse';
import Analysis from './pages/Analysis';
import Export from './pages/Export';
import Contribute from './pages/Contribute';
import About from './pages/About';
import LegalDisclaimer from './components/LegalDisclaimer';
import ThemeToggle from './components/ThemeToggle';

import './styles/theme.css';
import './App.css';

function Navigation() {
  const location = useLocation();
  
  const navItems = [
    { path: '/', icon: Home, label: 'Dashboard' },
    { path: '/browse', icon: Database, label: 'Browse' },
    { path: '/analysis', icon: BarChart3, label: 'Analysis' },
    { path: '/export', icon: FileDown, label: 'Export' },
    { path: '/contribute', icon: Upload, label: 'Contribute' },
    { path: '/about', icon: Info, label: 'About' },
  ];
  
  return (
    <nav className="sidebar">
      <div className="sidebar-header">
        <h1>Project RawHorse</h1>
      </div>
      <ul className="nav-items">
        {navItems.map((item) => {
          const Icon = item.icon;
          const isActive = location.pathname === item.path;
          return (
            <li key={item.path}>
              <Link 
                to={item.path} 
                className={isActive ? 'active' : ''}
              >
                <Icon size={20} />
                <span>{item.label}</span>
              </Link>
            </li>
          );
        })}
      </ul>
    </nav>
  );
}

function App() {
  const [disclaimerAccepted, setDisclaimerAccepted] = useState(false);

  useEffect(() => {
    const accepted = localStorage.getItem('disclaimer_accepted');
    if (accepted === 'true') {
      setDisclaimerAccepted(true);
    }
  }, []);

  const handleDisclaimerAccept = () => {
    localStorage.setItem('disclaimer_accepted', 'true');
    setDisclaimerAccepted(true);
  };

  return (
    <Router>
      <div className="app">
        {!disclaimerAccepted && (
          <LegalDisclaimer onAccept={handleDisclaimerAccept} />
        )}
        
        <ThemeToggle />
        <Navigation />
        
        <main className="main-content">
          <Routes>
            <Route path="/" element={<Dashboard />} />
            <Route path="/browse" element={<Browse />} />
            <Route path="/analysis" element={<Analysis />} />
            <Route path="/export" element={<Export />} />
            <Route path="/contribute" element={<Contribute />} />
            <Route path="/about" element={<About />} />
          </Routes>
        </main>
      </div>
    </Router>
  );
}

export default App;
