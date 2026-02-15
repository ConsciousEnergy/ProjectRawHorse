import { Component, ReactNode } from 'react';
import { Link } from 'react-router-dom';
import { AlertTriangle } from 'lucide-react';
import './ErrorBoundary.css';

interface Props {
  children: ReactNode;
  fallback?: ReactNode;
}

interface State {
  hasError: boolean;
  error: Error | null;
  showDetails: boolean;
}

export class ErrorBoundary extends Component<Props, State> {
  constructor(props: Props) {
    super(props);
    this.state = {
      hasError: false,
      error: null,
      showDetails: false,
    };
  }

  static getDerivedStateFromError(error: Error): Partial<State> {
    return { hasError: true, error };
  }

  componentDidCatch(error: Error, errorInfo: React.ErrorInfo) {
    console.error('ErrorBoundary caught:', error, errorInfo);
  }

  handleRetry = () => {
    this.setState({ hasError: false, error: null });
  };

  render() {
    if (this.state.hasError && this.state.error) {
      if (this.props.fallback) {
        return this.props.fallback;
      }
      return (
        <div className="error-boundary" role="alert">
          <div className="error-boundary-content">
            <AlertTriangle size={48} className="error-boundary-icon" />
            <h2>Something went wrong</h2>
            <p>
              An unexpected error occurred. You can try again or return to the dashboard.
            </p>
            <div className="error-boundary-actions">
              <button onClick={this.handleRetry} className="btn btn-primary">
                Try Again
              </button>
              <Link to="/" className="btn btn-secondary">
                Go Home
              </Link>
            </div>
            <details
              className="error-boundary-details"
              open={this.state.showDetails}
              onToggle={(e) => this.setState({ showDetails: (e.target as HTMLDetailsElement).open })}
            >
              <summary>Error details</summary>
              <pre className="error-boundary-stack">{this.state.error.message}</pre>
            </details>
          </div>
        </div>
      );
    }
    return this.props.children;
  }
}

export default ErrorBoundary;
