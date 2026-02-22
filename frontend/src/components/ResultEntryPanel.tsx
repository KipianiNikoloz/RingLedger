interface ResultEntryPanelProps {
  busy: boolean;
  winner: "A" | "B";
  onWinnerChange: (winner: "A" | "B") => void;
  onSubmit: () => void;
}

export function ResultEntryPanel({ busy, winner, onWinnerChange, onSubmit }: ResultEntryPanelProps): JSX.Element {
  return (
    <section className="panel">
      <h2>Admin Result Entry</h2>
      <div className="grid two-col compact-grid">
        <label>
          Winner
          <select value={winner} onChange={(event) => onWinnerChange(event.target.value as "A" | "B")}>
            <option value="A">A</option>
            <option value="B">B</option>
          </select>
        </label>
        <div className="actions-row inline-action">
          <button type="button" onClick={onSubmit} disabled={busy} data-testid="result-submit">
            Enter Result
          </button>
        </div>
      </div>
    </section>
  );
}

