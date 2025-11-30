import { useState, useEffect, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import { Search, X, Loader } from 'lucide-react';
import { searchGlobal } from '../services/api';
import type { SearchResult } from '../types';
import './SearchBar.css';

export default function SearchBar() {
  const navigate = useNavigate();
  const [query, setQuery] = useState('');
  const [results, setResults] = useState<SearchResult[]>([]);
  const [loading, setLoading] = useState(false);
  const [isOpen, setIsOpen] = useState(false);
  const [selectedIndex, setSelectedIndex] = useState(-1);
  const searchRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLInputElement>(null);

  // Debounced search
  useEffect(() => {
    if (query.length >= 2) {
      setLoading(true);
      const timer = setTimeout(async () => {
        try {
          const data = await searchGlobal(query);
          setResults(data.results || []);
          setIsOpen(true);
          setSelectedIndex(-1);
        } catch (error) {
          console.error('Search error:', error);
          setResults([]);
        } finally {
          setLoading(false);
        }
      }, 300);
      return () => clearTimeout(timer);
    } else {
      setResults([]);
      setIsOpen(false);
      setLoading(false);
    }
  }, [query]);

  // Click outside to close
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (searchRef.current && !searchRef.current.contains(event.target as Node)) {
        setIsOpen(false);
      }
    };
    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  // Keyboard navigation
  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (!isOpen || results.length === 0) return;

    switch (e.key) {
      case 'ArrowDown':
        e.preventDefault();
        setSelectedIndex((prev) => (prev < results.length - 1 ? prev + 1 : prev));
        break;
      case 'ArrowUp':
        e.preventDefault();
        setSelectedIndex((prev) => (prev > 0 ? prev - 1 : -1));
        break;
      case 'Enter':
        e.preventDefault();
        if (selectedIndex >= 0) {
          handleResultClick(results[selectedIndex]);
        }
        break;
      case 'Escape':
        e.preventDefault();
        setIsOpen(false);
        break;
    }
  };

  // Global keyboard shortcut: / to focus search
  useEffect(() => {
    const handleGlobalKeyDown = (e: KeyboardEvent) => {
      if (e.key === '/' && !['INPUT', 'TEXTAREA'].includes((e.target as HTMLElement).tagName)) {
        e.preventDefault();
        inputRef.current?.focus();
      }
    };
    document.addEventListener('keydown', handleGlobalKeyDown);
    return () => document.removeEventListener('keydown', handleGlobalKeyDown);
  }, []);

  const handleResultClick = (result: SearchResult) => {
    // Map result type to Browse tab
    const typeToTab: Record<string, string> = {
      'entity': 'entities',
      'award': 'awards',
      'money_flow': 'money-flows',
      'foia_target': 'foia'
    };
    
    const tab = typeToTab[result.type] || 'entities';
    
    // Navigate to Browse page with search pre-filled
    // Extract the main search term from the title
    const searchTerm = result.title.split(':')[0].split('→')[0].trim();
    
    navigate(`/browse?tab=${tab}&search=${encodeURIComponent(searchTerm)}&highlight=${result.id}`);
    
    setIsOpen(false);
    setQuery('');
  };

  const getResultIcon = (type: string) => {
    switch (type) {
      case 'entity':
        return '📊';
      case 'award':
        return '🏆';
      case 'money_flow':
        return '💰';
      case 'foia_target':
        return '📄';
      default:
        return '📌';
    }
  };

  const getResultTypeName = (type: string) => {
    switch (type) {
      case 'entity':
        return 'Entity';
      case 'award':
        return 'Award';
      case 'money_flow':
        return 'Money Flow';
      case 'foia_target':
        return 'FOIA Target';
      default:
        return type;
    }
  };

  return (
    <div className="search-bar-wrapper" ref={searchRef}>
      <div className="search-input-container">
        <Search className="search-icon" size={18} />
        <input
          ref={inputRef}
          type="text"
          placeholder="Search entities, awards, flows... (press / to focus)"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          onKeyDown={handleKeyDown}
          onFocus={() => query.length >= 2 && setIsOpen(true)}
          className="search-input"
        />
        {loading && <Loader className="search-loading" size={18} />}
        {query && !loading && (
          <button
            onClick={() => {
              setQuery('');
              setIsOpen(false);
            }}
            className="search-clear"
            aria-label="Clear search"
          >
            <X size={16} />
          </button>
        )}
      </div>

      {isOpen && (
        <div className="search-results-dropdown">
          {results.length > 0 ? (
            <>
              <div className="search-results-list">
                {results.map((result, index) => (
                  <div
                    key={`${result.type}-${result.id}`}
                    className={`search-result-item ${index === selectedIndex ? 'selected' : ''}`}
                    onClick={() => handleResultClick(result)}
                    onMouseEnter={() => setSelectedIndex(index)}
                  >
                    <div className="search-result-icon">{getResultIcon(result.type)}</div>
                    <div className="search-result-content">
                      <div className="search-result-header">
                        <span className="search-result-title">{result.title}</span>
                        <span className="search-result-type-badge">
                          {getResultTypeName(result.type)}
                        </span>
                      </div>
                      <div className="search-result-description">{result.description}</div>
                    </div>
                  </div>
                ))}
              </div>
              <div className="search-results-footer">
                <span>{results.length} result{results.length !== 1 ? 's' : ''}</span>
                <span className="search-hint">↑↓ navigate • Enter select • Esc close</span>
              </div>
            </>
          ) : (
            <div className="search-no-results">
              <p>No results found for "{query}"</p>
              <small>Try a different search term</small>
            </div>
          )}
        </div>
      )}
    </div>
  );
}

