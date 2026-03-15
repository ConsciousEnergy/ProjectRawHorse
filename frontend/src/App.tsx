import { useEffect, useState } from 'react';
import { BrowserRouter as Router, Routes, Route, Link, useLocation } from 'react-router-dom';
import { Home, Database, BarChart3, FileDown, Upload, Info } from 'lucide-react';

import Dashboard from './pages/Dashboard';
import Browse from './pages/Browse';
import Analysis from './pages/Analysis';
import AnalysisOverview from './pages/AnalysisOverview';
import NetworkGraphPage from './pages/NetworkGraphPage';
import PyramidPage from './pages/PyramidPage';
import SankeyDiagramPage from './pages/SankeyDiagramPage';
import FoiaTargetsPage from './pages/FoiaTargetsPage';
import TimelinePage from './pages/TimelinePage';
import SimulationTimelinePage from './pages/SimulationTimelinePage';
import Export from './pages/Export';
import Contribute from './pages/Contribute';
import About from './pages/About';
import LegalDisclaimer from './components/LegalDisclaimer';
import ThemeToggle from './components/ThemeToggle';
import { ErrorBoundary } from './components/ErrorBoundary';
import SearchBar from './components/SearchBar';
import RefreshButton from './components/RefreshButton';
import { DataProvider } from './contexts/DataContext';

import './styles/theme.css';
import './App.css';

function Navigation() {
  const location = useLocation();
  
  const navItems = [
    { path: '/', icon: Home, label: 'Dashboard', exact: true },
    { path: '/browse', icon: Database, label: 'Browse', exact: true },
    { path: '/analysis', icon: BarChart3, label: 'Analysis', exact: false },
    { path: '/export', icon: FileDown, label: 'Export', exact: true },
    { path: '/contribute', icon: Upload, label: 'Contribute', exact: true },
    { path: '/about', icon: Info, label: 'About', exact: true },
  ];
  
  return (
    <nav className="sidebar">
      <div className="sidebar-header">
        <img src="/PRHLogo.png" alt="Project RawHorse Logo" className="sidebar-logo" />
        <h1>Project RawHorse</h1>
      </div>
      
      <div className="sidebar-search">
        <SearchBar />
      </div>
      
      <ul className="nav-items">
        {navItems.map((item) => {
          const Icon = item.icon;
          // For analysis, match any sub-route; for others, exact match only
          const isActive = item.exact 
            ? location.pathname === item.path 
            : location.pathname.startsWith(item.path);
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
  const isSimulationEnabled = localStorage.getItem('enable_simulation_tab') !== 'false';

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
    <DataProvider>
      <Router>
        <div className="app">
          <a href="#main-content" className="skip-link">
            Skip to main content
          </a>
          {!disclaimerAccepted && (
            <LegalDisclaimer onAccept={handleDisclaimerAccept} />
          )}
          
          <ThemeToggle />
          <Navigation />
          <RefreshButton position="floating" />
          
          <main id="main-content" className="main-content" role="main">
            <Routes>
              <Route path="/" element={<ErrorBoundary><Dashboard /></ErrorBoundary>} />
              <Route path="/browse" element={<ErrorBoundary><Browse /></ErrorBoundary>} />
              <Route path="/analysis" element={<ErrorBoundary><AnalysisOverview /></ErrorBoundary>} />
              <Route path="/analysis/network" element={<ErrorBoundary><NetworkGraphPage /></ErrorBoundary>} />
              <Route path="/analysis/sankey" element={<ErrorBoundary><SankeyDiagramPage /></ErrorBoundary>} />
              <Route path="/analysis/pyramid" element={<ErrorBoundary><PyramidPage /></ErrorBoundary>} />
              <Route path="/analysis/foia" element={<ErrorBoundary><FoiaTargetsPage /></ErrorBoundary>} />
              <Route path="/analysis/timeline" element={<ErrorBoundary><TimelinePage /></ErrorBoundary>} />
              {isSimulationEnabled && (
                <Route path="/analysis/simulation" element={<ErrorBoundary><SimulationTimelinePage /></ErrorBoundary>} />
              )}
              <Route path="/analysis/legacy" element={<ErrorBoundary><Analysis /></ErrorBoundary>} />
              <Route path="/export" element={<ErrorBoundary><Export /></ErrorBoundary>} />
              <Route path="/contribute" element={<ErrorBoundary><Contribute /></ErrorBoundary>} />
              <Route path="/about" element={<ErrorBoundary><About /></ErrorBoundary>} />
            </Routes>
          </main>
        </div>
      </Router>
    </DataProvider>
  );
}

export default App;
