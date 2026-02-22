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
  confirmOfferSequence: string;
  confirmEngineResult: string;
  confirmValidated: boolean;
  onReconcileKindChange: (kind: EscrowKind) => void;
  onReconcileStatusChange: (status: SigningStatus) => void;
  onReconcileTxHashChange: (value: string) => void;
  onConfirmKindChange: (kind: EscrowKind) => void;
  onConfirmTxHashChange: (value: string) => void;
  onConfirmOfferSequenceChange: (value: string) => void;
  onConfirmEngineResultChange: (value: string) => void;
  onConfirmValidatedChange: (value: boolean) => void;
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
  confirmOfferSequence,
  confirmEngineResult,
  confirmValidated,
  onReconcileKindChange,
  onReconcileStatusChange,
  onReconcileTxHashChange,
  onConfirmKindChange,
  onConfirmTxHashChange,
  onConfirmOfferSequenceChange,
  onConfirmEngineResultChange,
  onConfirmValidatedChange,
  onPrepare,
  onReconcile,
  onConfirm,
}: EscrowFlowPanelProps): JSX.Element {
  return (
    <section className="panel">
      <h2>Promoter Escrow Flow</h2>
      <div className="actions-row">
        <button type="button" onClick={onPrepare} disabled={busy} data-testid="escrow-prepare-submit">
          Prepare Escrows
        </button>
      </div>
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

      <div className="grid four-col compact-grid">
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
        <label>
          Offer Sequence
          <input
            value={confirmOfferSequence}
            onChange={(event) => onConfirmOfferSequenceChange(event.target.value)}
            inputMode="numeric"
          />
        </label>
        <label>
          Engine Result
          <input value={confirmEngineResult} onChange={(event) => onConfirmEngineResultChange(event.target.value)} />
        </label>
        <label className="check-label">
          <input type="checkbox" checked={confirmValidated} onChange={(event) => onConfirmValidatedChange(event.target.checked)} />
          Validated
        </label>
      </div>
      <div className="actions-row">
        <button type="button" onClick={onConfirm} disabled={busy} data-testid="escrow-confirm-submit">
          Confirm Escrow
        </button>
      </div>
    </section>
  );
}

