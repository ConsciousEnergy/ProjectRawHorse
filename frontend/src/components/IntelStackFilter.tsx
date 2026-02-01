import React from 'react';
import './IntelStackFilter.css';

// Intelligence Stack Levels based on UAPGerb's pyramid structure
export const STACK_LEVELS = [
  { level: 1, name: 'Control Group', color: '#FF1744', description: 'MITRE/JASON, NSC, Executive Branch' },
  { level: 2, name: 'Administrators', color: '#FF6B35', description: 'NRO, NGA, CIA DS&T, DIA, NSA, OUSD, SAF-AQ' },
  { level: 3, name: 'FFRDCs', color: '#FF9800', description: 'MITRE, Battelle, Sandia, LANL, LLNL, Oak Ridge' },
  { level: 4, name: 'Prime Contractors', color: '#5B4FFF', description: 'Lockheed Martin, Northrop Grumman, Raytheon' },
  { level: 5, name: 'Facilities', color: '#4CAF50', description: 'Area 51, S4, Edwards AFB, Tonopah, Dugway' },
  { level: 6, name: 'Programs', color: '#E91E63', description: 'Immaculate Constellation, Kona Blue, etc.' },
];

interface IntelStackFilterProps {
  activeLevels: number[];
  onChange: (levels: number[]) => void;
  showAll?: boolean;
  compact?: boolean;
}

function IntelStackFilter({ activeLevels, onChange, showAll = true, compact = false }: IntelStackFilterProps) {
  const handleLevelToggle = (level: number) => {
    if (activeLevels.includes(level)) {
      // Remove level
      onChange(activeLevels.filter(l => l !== level));
    } else {
      // Add level
      onChange([...activeLevels, level].sort());
    }
  };

  const handleSelectAll = () => {
    if (activeLevels.length === STACK_LEVELS.length) {
      onChange([]); // Deselect all
    } else {
      onChange(STACK_LEVELS.map(l => l.level)); // Select all
    }
  };

  const allSelected = activeLevels.length === STACK_LEVELS.length;
  const noneSelected = activeLevels.length === 0;

  return (
    <div className={`intel-stack-filter ${compact ? 'compact' : ''}`}>
      <div className="intel-stack-header">
        <h4>Intelligence Stack</h4>
        {showAll && (
          <button 
            className={`select-all-btn ${allSelected ? 'all-selected' : ''}`}
            onClick={handleSelectAll}
            title={allSelected ? 'Deselect All' : 'Select All'}
          >
            {allSelected ? 'Clear' : 'All'}
          </button>
        )}
      </div>
      
      <div className="intel-stack-pyramid">
        {STACK_LEVELS.map((stack) => {
          const isActive = activeLevels.includes(stack.level) || noneSelected;
          return (
            <button
              key={stack.level}
              className={`stack-level ${isActive ? 'active' : 'inactive'}`}
              onClick={() => handleLevelToggle(stack.level)}
              style={{ 
                '--stack-color': stack.color,
                '--stack-width': `${100 - (stack.level - 1) * 10}%`
              } as React.CSSProperties}
              title={stack.description}
              aria-pressed={isActive}
            >
              <span className="stack-indicator" style={{ backgroundColor: stack.color }} />
              <span className="stack-name">{stack.name}</span>
              {!compact && <span className="stack-level-num">L{stack.level}</span>}
            </button>
          );
        })}
      </div>
      
      {!compact && (
        <div className="intel-stack-info">
          <small>
            {noneSelected 
              ? 'Showing all levels' 
              : `Showing ${activeLevels.length} of ${STACK_LEVELS.length} levels`}
          </small>
        </div>
      )}
    </div>
  );
}

export default IntelStackFilter;
