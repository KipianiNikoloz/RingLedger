interface BoutWorkspacePanelProps {
  boutId: string;
  onBoutIdChange: (value: string) => void;
}

export function BoutWorkspacePanel({ boutId, onBoutIdChange }: BoutWorkspacePanelProps): JSX.Element {
  return (
    <section className="panel">
      <div className="panel-header">
        <h2>Bout Workspace</h2>
        <p className="panel-note">Select the active bout context used by escrow, result, and payout actions.</p>
      </div>
      <label className="wide-label">
        Bout ID
        <input
          type="text"
          name="bout_id"
          value={boutId}
          onChange={(event) => onBoutIdChange(event.target.value)}
          placeholder="e.g. 123e4567-e89b-12d3-a456-426614174000"
        />
      </label>
    </section>
  );
}
