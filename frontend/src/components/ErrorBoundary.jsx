import React from 'react';

export class ErrorBoundary extends React.Component {
  constructor(props) {
    super(props);
    this.state = { hasError: false, error: null, errorInfo: null };
  }

  static getDerivedStateFromError(error) {
    return { hasError: true, error };
  }

  componentDidCatch(error, errorInfo) {
    this.setState({ errorInfo });
    // Keep a diagnostic log for developer review
    console.error('ErrorBoundary caught an unhandled error:', error, errorInfo);
  }

  handleReload = () => {
    window.location.reload();
  };

  handleReset = () => {
    this.setState({ hasError: false, error: null, errorInfo: null });
    window.location.href = '/';
  };

  render() {
    if (this.state.hasError) {
      return (
        <div className="min-h-[60vh] flex items-center justify-center px-4 py-12">
          <div className="max-w-md w-full bg-academic-card border border-academic-border rounded-lg p-6 shadow-sm text-center">
            <div className="inline-flex items-center justify-center w-12 h-12 rounded-full bg-academic-burgundylight text-academic-burgundy mb-4">
              <svg
                xmlns="http://www.w3.org/2000/svg"
                className="w-6 h-6"
                fill="none"
                viewBox="0 0 24 24"
                stroke="currentColor"
                strokeWidth={2}
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"
                />
              </svg>
            </div>
            <h2 className="text-lg font-bold text-academic-primary mb-2">
              Application Notice
            </h2>
            <p className="text-xs text-academic-muted mb-6 leading-relaxed">
              An unexpected error occurred while rendering this view. Your session data remains safe.
            </p>
            {this.state.error?.message && (
              <div className="mb-6 p-2 bg-academic-secondary/60 rounded text-[11px] text-academic-muted font-mono text-left overflow-x-auto border border-academic-border/60">
                {this.state.error.message}
              </div>
            )}
            <div className="flex justify-center gap-3">
              <button
                type="button"
                onClick={this.handleReload}
                className="px-4 py-2 text-xs font-medium rounded border border-academic-border bg-academic-secondary hover:bg-academic-border text-academic-primary transition-colors"
              >
                Reload Page
              </button>
              <button
                type="button"
                onClick={this.handleReset}
                className="px-4 py-2 text-xs font-semibold rounded bg-academic-burgundy hover:bg-academic-burgundy/90 text-white transition-colors"
              >
                Back to Home
              </button>
            </div>
          </div>
        </div>
      );
    }

    return this.props.children;
  }
}
