'use client';

type GlobalErrorProps = {
  error: Error & { digest?: string };
  retry: () => void;
};

const htmlStyle: React.CSSProperties = {
  height: '100%',
  margin: 0,
  padding: 0,
  background: '#020617',
  color: '#f1f5f9',
  fontFamily:
    'ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif',
  WebkitFontSmoothing: 'antialiased',
};

const bodyStyle: React.CSSProperties = {
  height: '100%',
  margin: 0,
  padding: 0,
  display: 'flex',
  alignItems: 'center',
  justifyContent: 'center',
  overflow: 'hidden',
};

const cardStyle: React.CSSProperties = {
  width: '100%',
  maxWidth: 448,
  padding: 32,
  borderRadius: 16,
  background: '#0f172a',
  border: '1px solid #1e293b',
  textAlign: 'center',
  boxSizing: 'border-box',
};

const iconWrapStyle: React.CSSProperties = {
  width: 64,
  height: 64,
  marginLeft: 'auto',
  marginRight: 'auto',
  marginBottom: 16,
  borderRadius: '50%',
  background: 'rgba(244, 63, 94, 0.10)',
  display: 'flex',
  alignItems: 'center',
  justifyContent: 'center',
};

const titleStyle: React.CSSProperties = {
  fontSize: 20,
  fontWeight: 700,
  color: '#ffffff',
  marginBottom: 8,
  marginTop: 0,
};

const descStyle: React.CSSProperties = {
  fontSize: 14,
  color: '#94a3b8',
  lineHeight: 1.5,
  margin: 0,
};

const digestStyle: React.CSSProperties = {
  marginTop: 12,
  fontSize: 11,
  fontFamily:
    'ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, "Liberation Mono", "Courier New", monospace',
  color: '#64748b',
  wordBreak: 'break-all',
};

const btnStyle: React.CSSProperties = {
  width: '100%',
  paddingTop: 12,
  paddingBottom: 12,
  paddingLeft: 16,
  paddingRight: 16,
  borderRadius: 12,
  background: '#4f46e5',
  color: '#ffffff',
  fontSize: 14,
  fontWeight: 600,
  border: 'none',
  cursor: 'pointer',
  boxShadow: '0 4px 14px 0 rgba(49, 46, 129, 0.4)',
};

export default function GlobalError({ error, retry }: GlobalErrorProps) {
  if (typeof window !== 'undefined') {
    try {
      console.error(error);
    } catch {
      // no-op
    }
  }

  return (
    <html lang="en" style={htmlStyle}>
      <head>
        <meta charSet="utf-8" />
        <meta name="viewport" content="width=device-width, initial-scale=1" />
        <title>Error — CodeAtlas AI</title>
      </head>
      <body style={bodyStyle}>
        <div style={cardStyle}>
          <div>
            <div style={iconWrapStyle}>
              <svg
                xmlns="http://www.w3.org/2000/svg"
                width={32}
                height={32}
                viewBox="0 0 24 24"
                fill="none"
                stroke="#f43f5e"
                strokeWidth={2}
                strokeLinecap="round"
                strokeLinejoin="round"
                aria-hidden
              >
                <path d="M10.29 3.86 1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z" />
                <line x1="12" y1="9" x2="12" y2="13" />
                <line x1="12" y1="17" x2="12.01" y2="17" />
              </svg>
            </div>
            <h2 style={titleStyle}>Something went wrong</h2>
            <p style={descStyle}>
              An unexpected error occurred while loading the application.
            </p>
            {error.digest ? (
              <p style={digestStyle}>Error ID: {error.digest}</p>
            ) : null}
          </div>
          <div style={{ marginTop: 24 }}>
            <button
              type="button"
              onClick={() => retry()}
              style={btnStyle}
              onMouseEnter={(e) => {
                (e.currentTarget as HTMLButtonElement).style.background = '#6366f1';
              }}
              onMouseLeave={(e) => {
                (e.currentTarget as HTMLButtonElement).style.background = '#4f46e5';
              }}
            >
              Try again
            </button>
          </div>
        </div>
      </body>
    </html>
  );
}
