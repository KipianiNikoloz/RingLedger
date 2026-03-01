interface StatusConsoleProps {
  entries: string[];
}

export function StatusConsole({ entries }: StatusConsoleProps) {
  return (
    <section className="status-console panel" aria-live="polite">
      <div className="panel-header">
        <h2>Action Log</h2>
        <p className="panel-note">Latest 40 actions with deterministic status/error entries.</p>
      </div>
      {entries.length > 0 ? (
        <ul>
          {entries.map((entry, index) => (
            <li key={`${entry}-${index}`}>{entry}</li>
          ))}
        </ul>
      ) : (
        <p className="panel-note empty-log">No actions yet.</p>
      )}
    </section>
  );
}

