import type {
  BoutResultResponse,
  EscrowConfirmResponse,
  EscrowPrepareResponse,
  PayoutConfirmResponse,
  PayoutPrepareResponse,
  SigningReconcileResponse,
} from "../api/types";
import { JsonBlock } from "./JsonBlock";

interface OutputPanelProps {
  registerResult: unknown;
  escrowPrepareResult: EscrowPrepareResponse | null;
  escrowReconcileResult: SigningReconcileResponse | null;
  escrowConfirmResult: EscrowConfirmResponse | null;
  resultEntry: BoutResultResponse | null;
  payoutPrepareResult: PayoutPrepareResponse | null;
  payoutReconcileResult: SigningReconcileResponse | null;
  payoutConfirmResult: PayoutConfirmResponse | null;
}

export function OutputPanel({
  registerResult,
  escrowPrepareResult,
  escrowReconcileResult,
  escrowConfirmResult,
  resultEntry,
  payoutPrepareResult,
  payoutReconcileResult,
  payoutConfirmResult,
}: OutputPanelProps) {
  const hasResults = Boolean(
    registerResult ||
      escrowPrepareResult ||
      escrowReconcileResult ||
      escrowConfirmResult ||
      resultEntry ||
      payoutPrepareResult ||
      payoutReconcileResult ||
      payoutConfirmResult,
  );

  return (
    <section className="output-grid">
      {hasResults ? (
        <>
          {registerResult ? <JsonBlock title="Register Response" data={registerResult} /> : null}
          {escrowPrepareResult ? <JsonBlock title="Escrow Prepare" data={escrowPrepareResult} /> : null}
          {escrowReconcileResult ? <JsonBlock title="Escrow Reconcile" data={escrowReconcileResult} /> : null}
          {escrowConfirmResult ? <JsonBlock title="Escrow Confirm" data={escrowConfirmResult} /> : null}
          {resultEntry ? <JsonBlock title="Result Entry" data={resultEntry} /> : null}
          {payoutPrepareResult ? <JsonBlock title="Payout Prepare" data={payoutPrepareResult} /> : null}
          {payoutReconcileResult ? <JsonBlock title="Payout Reconcile" data={payoutReconcileResult} /> : null}
          {payoutConfirmResult ? <JsonBlock title="Payout Confirm" data={payoutConfirmResult} /> : null}
        </>
      ) : (
        <p className="panel-note empty-output">Run an action to see backend payloads.</p>
      )}
    </section>
  );
}

