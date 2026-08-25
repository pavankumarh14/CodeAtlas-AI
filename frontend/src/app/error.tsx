'use client';

type ErrorProps = {
  error: Error & { digest?: string };
  retry: () => void;
};

const cardStyle: React.CSSProperties = {
  width: '100%',
  maxWidth: 512,
  marginLeft: 'auto',
  marginRight: 'auto',
  padding: 32,
  borderRadius: 16,
  background: '#0f172a',
  border: '1px solid #1e293b',
  textAlign: 'center',
  boxSizing: 'border-box',
};

const iconWrapStyle: React.CSSProperties = {
  width: 56,
  height: 56,
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
  fontSize: 18,
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
  paddingTop: 10,
  paddingBottom: 10,
  paddingLeft: 20,
  paddingRight: 20,
  borderRadius: 12,
  background: '#4f46e5',
  color: '#ffffff',
  fontSize: 14,
  fontWeight: 600,
  border: 'none',
  cursor: 'pointer',
  boxShadow: '0 4px 14px 0 rgba(49, 46, 129, 0.4)',
};

export default function Error({ error, retry }: ErrorProps) {
  if (typeof window !== 'undefined') {
    try {
      console.error(error);
    } catch {
      // no-op
    }
  }

  return (
    <div style={cardStyle}>
      <div>
        <div style={iconWrapStyle}>
          <svg
            xmlns="http://www.w3.org/2000/svg"
            width={28}
            height={28}
            viewBox="0 0 24 24"
            fill="none"
            stroke="#f43f5e"
            strokeWidth={2}
            strokeLinecap="round"
            strokeLinejoin="round"
            aria-hidden
          >
            <circle cx="12" cy="12" r="10" />
            <line x1="12" y1="8" x2="12" y2="12" />
            <line x1="12" y1="16" x2="12.01" y2="16" />
          </svg>
        </div>
        <h2 style={titleStyle}>Something went wrong</h2>
        <p style={descStyle}>
          Failed to load this section. You can try again.
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
  );
}
