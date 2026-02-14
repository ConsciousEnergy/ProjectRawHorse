import { useState, useEffect, useRef, useCallback, useMemo } from 'react';
import { useNavigate } from 'react-router-dom';
import { Search, X, Loader } from 'lucide-react';
import { searchGlobal } from '../services/api';
import type { SearchResult } from '../types';
import './SearchBar.css';

const RECENT_CLICKED_KEY = 'searchBarClickedResults';
const RECENT_QUERIES_KEY = 'searchBarRecentQueries';
const MAX_CLICKED = 8;
const MAX_QUERIES = 10;
const DEBOUNCE_MS = 200;

export interface RecentClickedItem {
  id: string | number;
  type: string;
  title: string;
}

function loadRecentClicked(): RecentClickedItem[] {
  try {
    const raw = localStorage.getItem(RECENT_CLICKED_KEY);
    if (!raw) return [];
    const parsed = JSON.parse(raw);
    return Array.isArray(parsed) ? parsed : [];
  } catch {
    return [];
  }
}

function saveRecentClicked(items: RecentClickedItem[]) {
  try {
    localStorage.setItem(RECENT_CLICKED_KEY, JSON.stringify(items.slice(0, MAX_CLICKED)));
  } catch {
    // ignore
  }
}

function loadRecentQueries(): string[] {
  try {
    const raw = localStorage.getItem(RECENT_QUERIES_KEY);
    if (!raw) return [];
    const parsed = JSON.parse(raw);
    return Array.isArray(parsed) ? parsed : [];
  } catch {
    return [];
  }
}

function saveRecentQueries(queries: string[]) {
  try {
    localStorage.setItem(RECENT_QUERIES_KEY, JSON.stringify(queries.slice(0, MAX_QUERIES)));
  } catch {
    // ignore
  }
}

export default function SearchBar() {
  const navigate = useNavigate();
  const [query, setQuery] = useState('');
  const [results, setResults] = useState<SearchResult[]>([]);
  const [loading, setLoading] = useState(false);
  const [isOpen, setIsOpen] = useState(false);
  const [selectedIndex, setSelectedIndex] = useState(-1);
  const [recentClicked, setRecentClicked] = useState<RecentClickedItem[]>([]);
  const [recentQueries, setRecentQueries] = useState<string[]>([]);
  const [suggestions, setSuggestions] = useState<string[]>([]);
  const searchRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLInputElement>(null);

  // Load recent from localStorage when dropdown opens
  useEffect(() => {
    if (isOpen) {
      setRecentClicked(loadRecentClicked());
      setRecentQueries(loadRecentQueries());
    }
  }, [isOpen]);

  // Debounced search
  useEffect(() => {
    if (query.length >= 2) {
      setLoading(true);
      const timer = setTimeout(async () => {
        try {
          const data = await searchGlobal(query);
          const list = data.results || [];
          setResults(list);
          setSuggestions(data.suggestions || []);
          setIsOpen(true);
          setSelectedIndex(-1);
          // Save successful query to recent searches
          const prev = loadRecentQueries();
          const updated = [query.trim(), ...prev.filter((s) => s !== query.trim())].slice(0, MAX_QUERIES);
          saveRecentQueries(updated);
          setRecentQueries(updated);
        } catch (error) {
          console.error('Search error:', error);
          setResults([]);
          setSuggestions([]);
        } finally {
          setLoading(false);
        }
      }, DEBOUNCE_MS);
      return () => clearTimeout(timer);
    } else {
      setResults([]);
      setSuggestions([]);
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

  const typeToTab: Record<string, string> = {
    entity: 'entities',
    award: 'awards',
    money_flow: 'money-flows',
    foia_target: 'foia',
  };

  const navigateToResult = useCallback(
    (item: { id: string | number; type: string; title: string }) => {
      const tab = typeToTab[item.type] || 'entities';
      const searchTerm = item.title.split(':')[0].split('→')[0].trim();
      navigate(`/browse?tab=${tab}&search=${encodeURIComponent(searchTerm)}&highlight=${item.id}`);
      setIsOpen(false);
      setQuery('');
    },
    [navigate]
  );

  // Filter recent queries by current query for display and keyboard
  const filteredRecentQueries = useMemo(
    () =>
      recentQueries.filter(
        (q) => !query.trim() || q.toLowerCase().includes(query.toLowerCase())
      ),
    [recentQueries, query]
  );
  const suggestionCount = recentClicked.length + filteredRecentQueries.length;
  const showSuggestionsOnly = isOpen && query.length < 2;

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (!isOpen) return;
    if (showSuggestionsOnly) {
      switch (e.key) {
        case 'ArrowDown':
          e.preventDefault();
          setSelectedIndex((prev) => (prev < suggestionCount - 1 ? prev + 1 : prev));
          break;
        case 'ArrowUp':
          e.preventDefault();
          setSelectedIndex((prev) => (prev > 0 ? prev - 1 : -1));
          break;
        case 'Enter':
          e.preventDefault();
          if (selectedIndex >= 0) {
            if (selectedIndex < recentClicked.length) {
              navigateToResult(recentClicked[selectedIndex]);
            } else {
              const q = filteredRecentQueries[selectedIndex - recentClicked.length];
              if (q) {
                setQuery(q);
                inputRef.current?.focus();
              }
            }
          }
          break;
        case 'Escape':
          e.preventDefault();
          setIsOpen(false);
          break;
      }
      return;
    }
    if (results.length === 0) {
      if (e.key === 'Escape') {
        e.preventDefault();
        setIsOpen(false);
      }
      return;
    }
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
        if (selectedIndex >= 0) handleResultClick(results[selectedIndex]);
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
    const item: RecentClickedItem = { id: result.id, type: result.type, title: result.title };
    const prev = loadRecentClicked();
    const deduped = [item, ...prev.filter((r) => !(r.id === item.id && r.type === item.type))];
    saveRecentClicked(deduped);
    setRecentClicked(deduped.slice(0, MAX_CLICKED));
    navigateToResult(item);
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
          onFocus={() => setIsOpen(true)}
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
          {showSuggestionsOnly ? (
            <>
              <div className="search-suggestions-block">
                <div className="search-suggestions-label">Suggestions</div>
                {recentClicked.length > 0 && (
                  <div className="search-suggestions-section">
                    <span className="search-suggestions-section-title">Recent results</span>
                    <div className="search-results-list">
                      {recentClicked.map((item, index) => (
                        <div
                          key={`recent-${item.type}-${item.id}`}
                          className={`search-result-item ${index === selectedIndex ? 'selected' : ''}`}
                          onClick={() => navigateToResult(item)}
                          onMouseEnter={() => setSelectedIndex(index)}
                        >
                          <div className="search-result-icon">{getResultIcon(item.type)}</div>
                          <div className="search-result-content">
                            <span className="search-result-title">{item.title}</span>
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                )}
                {recentQueries.length > 0 && (
                  <div className="search-suggestions-section">
                    <span className="search-suggestions-section-title">Recent searches</span>
                    <div className="search-results-list">
                      {filteredRecentQueries.map((q, index) => {
                          const idx = recentClicked.length + index;
                          return (
                            <div
                              key={`query-${q}`}
                              className={`search-result-item ${idx === selectedIndex ? 'selected' : ''}`}
                              onClick={() => {
                                setQuery(q);
                                setSelectedIndex(-1);
                                inputRef.current?.focus();
                              }}
                              onMouseEnter={() => setSelectedIndex(idx)}
                            >
                              <div className="search-result-icon">🔍</div>
                              <div className="search-result-content">
                                <span className="search-result-title">{q}</span>
                              </div>
                            </div>
                          );
                        })}
                    </div>
                  </div>
                )}
              </div>
              <div className="search-results-footer">
                <button
                  type="button"
                  className="search-clear-history"
                  onClick={() => {
                    saveRecentClicked([]);
                    saveRecentQueries([]);
                    setRecentClicked([]);
                    setRecentQueries([]);
                  }}
                >
                  Clear history
                </button>
                <span className="search-hint">↑↓ navigate • Enter select • Esc close</span>
              </div>
            </>
          ) : results.length > 0 ? (
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
          ) : query.length >= 2 ? (
            <div className="search-no-results">
              <p>No results found for "{query}"</p>
              {suggestions.length > 0 ? (
                <div className="search-did-you-mean">
                  <span>Did you mean:</span>
                  <div className="search-suggestion-pills">
                    {suggestions.map((s) => (
                      <button
                        key={s}
                        type="button"
                        className="search-suggestion-pill"
                        onClick={() => setQuery(s)}
                      >
                        {s}
                      </button>
                    ))}
                  </div>
                </div>
              ) : (
                <small>Try a different search term</small>
              )}
            </div>
          ) : null}
        </div>
      )}
    </div>
  );
}

