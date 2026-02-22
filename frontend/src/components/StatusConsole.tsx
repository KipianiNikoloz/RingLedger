interface StatusConsoleProps {
  entries: string[];
}

export function StatusConsole({ entries }: StatusConsoleProps): JSX.Element {
  return (
    <section className="status-console" aria-live="polite">
      <h3>Action Log</h3>
      <ul>
        {entries.map((entry, index) => (
          <li key={`${entry}-${index}`}>{entry}</li>
        ))}
      </ul>
    </section>
  );
}
