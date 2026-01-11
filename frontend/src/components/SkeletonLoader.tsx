import './SkeletonLoader.css';

interface SkeletonLoaderProps {
  type?: 'card' | 'table' | 'stat' | 'text' | 'line';
  count?: number;
  width?: string;
  height?: string;
}

function SkeletonLoader({ type = 'line', count = 1, width, height }: SkeletonLoaderProps) {
  if (type === 'card') {
    return (
      <div className="skeleton-card">
        <div className="skeleton-line" style={{ width: '60%', height: '24px', marginBottom: '16px' }} />
        <div className="skeleton-line" style={{ width: '100%', height: '16px', marginBottom: '8px' }} />
        <div className="skeleton-line" style={{ width: '80%', height: '16px' }} />
      </div>
    );
  }

  if (type === 'table') {
    return (
      <div className="skeleton-table">
        <div className="skeleton-table-header">
          {[1, 2, 3, 4, 5].map((i) => (
            <div key={i} className="skeleton-line" style={{ width: '100%', height: '20px' }} />
          ))}
        </div>
        {[1, 2, 3, 4, 5, 6, 7, 8].map((row) => (
          <div key={row} className="skeleton-table-row">
            {[1, 2, 3, 4, 5].map((col) => (
              <div key={col} className="skeleton-line" style={{ width: '100%', height: '16px' }} />
            ))}
          </div>
        ))}
      </div>
    );
  }

  if (type === 'stat') {
    return (
      <div className="skeleton-stat">
        <div className="skeleton-line" style={{ width: '70%', height: '14px', marginBottom: '12px' }} />
        <div className="skeleton-line" style={{ width: '50%', height: '32px' }} />
      </div>
    );
  }

  return (
    <>
      {Array.from({ length: count }).map((_, i) => (
        <div
          key={i}
          className="skeleton-line"
          style={{
            width: width || '100%',
            height: height || '16px',
            marginBottom: i < count - 1 ? '8px' : '0',
          }}
        />
      ))}
    </>
  );
}

export default SkeletonLoader;
