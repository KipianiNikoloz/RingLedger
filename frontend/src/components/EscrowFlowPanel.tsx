import type { EscrowKind } from "../api/types";
import type { SigningStatus } from "../constants";
import { ESCROW_KINDS, SIGNING_STATUSES } from "../constants";

interface EscrowFlowPanelProps {
  busy: boolean;
  reconcileKind: EscrowKind;
  reconcileStatus: SigningStatus;
  reconcileTxHash: string;
  confirmKind: EscrowKind;
  confirmTxHash: string;
  onReconcileKindChange: (kind: EscrowKind) => void;
  onReconcileStatusChange: (status: SigningStatus) => void;
  onReconcileTxHashChange: (value: string) => void;
  onConfirmKindChange: (kind: EscrowKind) => void;
  onConfirmTxHashChange: (value: string) => void;
  onPrepare: () => void;
  onReconcile: () => void;
  onConfirm: () => void;
}

export function EscrowFlowPanel({
  busy,
  reconcileKind,
  reconcileStatus,
  reconcileTxHash,
  confirmKind,
  confirmTxHash,
  onReconcileKindChange,
  onReconcileStatusChange,
  onReconcileTxHashChange,
  onConfirmKindChange,
  onConfirmTxHashChange,
  onPrepare,
  onReconcile,
  onConfirm,
}: EscrowFlowPanelProps) {
  return (
    <section className="panel workflow-panel">
      <div className="panel-header">
        <h2>Promoter Escrow Flow</h2>
        <p className="panel-note">Submit only the transaction hash; the backend retrieves and verifies XRPL Testnet evidence.</p>
      </div>

      <div className="flow-stage">
        <h3>1. Prepare</h3>
        <div className="actions-row">
          <button type="button" onClick={onPrepare} disabled={busy} data-testid="escrow-prepare-submit">
            Prepare Escrows
          </button>
        </div>
      </div>

      <div className="flow-stage">
        <h3>2. Reconcile Signing</h3>
        <div className="grid three-col compact-grid">
          <label>
            Escrow Kind
            <select value={reconcileKind} onChange={(event) => onReconcileKindChange(event.target.value as EscrowKind)}>
              {ESCROW_KINDS.map((kind) => (
                <option value={kind} key={kind}>
                  {kind}
                </option>
              ))}
            </select>
          </label>
          <label>
            Signing Status
            <select value={reconcileStatus} onChange={(event) => onReconcileStatusChange(event.target.value as SigningStatus)}>
              {SIGNING_STATUSES.map((statusName) => (
                <option value={statusName} key={statusName}>
                  {statusName}
                </option>
              ))}
            </select>
          </label>
          <label>
            Observed Tx Hash
            <input value={reconcileTxHash} onChange={(event) => onReconcileTxHashChange(event.target.value)} />
          </label>
        </div>
        <div className="actions-row">
          <button type="button" onClick={onReconcile} disabled={busy} data-testid="escrow-reconcile-submit">
            Reconcile Escrow Signing
          </button>
        </div>
      </div>

      <div className="flow-stage">
        <h3>3. Confirm Ledger Result</h3>
        <div className="grid two-col compact-grid">
          <label>
            Confirm Kind
            <select value={confirmKind} onChange={(event) => onConfirmKindChange(event.target.value as EscrowKind)}>
              {ESCROW_KINDS.map((kind) => (
                <option value={kind} key={kind}>
                  {kind}
                </option>
              ))}
            </select>
          </label>
          <label>
            Tx Hash
            <input value={confirmTxHash} onChange={(event) => onConfirmTxHashChange(event.target.value)} />
          </label>
        </div>
        <div className="actions-row">
          <button type="button" onClick={onConfirm} disabled={busy} data-testid="escrow-confirm-submit">
            Confirm Escrow
          </button>
        </div>
      </div>
    </section>
  );
}

