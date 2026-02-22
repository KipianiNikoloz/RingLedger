import { AuthPanel } from "../components/AuthPanel";
import { BoutWorkspacePanel } from "../components/BoutWorkspacePanel";
import { EscrowFlowPanel } from "../components/EscrowFlowPanel";
import { OutputPanel } from "../components/OutputPanel";
import { PayoutFlowPanel } from "../components/PayoutFlowPanel";
import { ResultEntryPanel } from "../components/ResultEntryPanel";
import { StatusConsole } from "../components/StatusConsole";
import { useRingLedgerConsole } from "../hooks/useRingLedgerConsole";

export function AppShell(): JSX.Element {
  const model = useRingLedgerConsole();

  return (
    <main className="shell">
      <header className="masthead">
        <p className="eyebrow">RingLedger M4 Frontend Contract Coverage</p>
        <h1>Promoter Signing And Payout Console</h1>
        <p className="subtext">
          Frontend remains untrusted. Every lifecycle invariant is enforced by backend APIs. This console only drives
          authenticated API flows.
        </p>
      </header>

      <AuthPanel
        busy={model.busy}
        currentRoleSummary={model.currentRoleSummary}
        registerEmail={model.registerEmail}
        registerPassword={model.registerPassword}
        registerRole={model.registerRole}
        loginEmail={model.loginEmail}
        loginPassword={model.loginPassword}
        onRegisterEmailChange={model.setRegisterEmail}
        onRegisterPasswordChange={model.setRegisterPassword}
        onRegisterRoleChange={model.setRegisterRole}
        onLoginEmailChange={model.setLoginEmail}
        onLoginPasswordChange={model.setLoginPassword}
        onRegister={(event) => {
          void model.handleRegister(event);
        }}
        onLogin={(event) => {
          void model.handleLogin(event);
        }}
      />

      <BoutWorkspacePanel boutId={model.boutId} onBoutIdChange={model.setBoutId} />

      <EscrowFlowPanel
        busy={model.busy}
        reconcileKind={model.escrowReconcileKind}
        reconcileStatus={model.escrowReconcileStatus}
        reconcileTxHash={model.escrowReconcileTxHash}
        confirmKind={model.escrowConfirmKind}
        confirmTxHash={model.escrowConfirmTxHash}
        confirmOfferSequence={model.escrowConfirmOfferSequence}
        confirmEngineResult={model.escrowConfirmEngineResult}
        confirmValidated={model.escrowConfirmValidated}
        onReconcileKindChange={model.setEscrowReconcileKind}
        onReconcileStatusChange={model.setEscrowReconcileStatus}
        onReconcileTxHashChange={model.setEscrowReconcileTxHash}
        onConfirmKindChange={model.setEscrowConfirmKind}
        onConfirmTxHashChange={model.setEscrowConfirmTxHash}
        onConfirmOfferSequenceChange={model.setEscrowConfirmOfferSequence}
        onConfirmEngineResultChange={model.setEscrowConfirmEngineResult}
        onConfirmValidatedChange={model.setEscrowConfirmValidated}
        onPrepare={() => {
          void model.handleEscrowPrepare();
        }}
        onReconcile={() => {
          void model.handleEscrowReconcile();
        }}
        onConfirm={() => {
          void model.handleEscrowConfirm();
        }}
      />

      <ResultEntryPanel
        busy={model.busy}
        winner={model.winner}
        onWinnerChange={model.setWinner}
        onSubmit={() => {
          void model.handleResultEntry();
        }}
      />

      <PayoutFlowPanel
        busy={model.busy}
        reconcileKind={model.payoutReconcileKind}
        reconcileStatus={model.payoutReconcileStatus}
        reconcileTxHash={model.payoutReconcileTxHash}
        confirmKind={model.payoutConfirmKind}
        confirmTxHash={model.payoutConfirmTxHash}
        confirmEngineResult={model.payoutConfirmEngineResult}
        confirmValidated={model.payoutConfirmValidated}
        closeTimeRipple={model.payoutCloseTimeRipple}
        onReconcileKindChange={model.setPayoutReconcileKind}
        onReconcileStatusChange={model.setPayoutReconcileStatus}
        onReconcileTxHashChange={model.setPayoutReconcileTxHash}
        onConfirmKindChange={model.setPayoutConfirmKind}
        onConfirmTxHashChange={model.setPayoutConfirmTxHash}
        onConfirmEngineResultChange={model.setPayoutConfirmEngineResult}
        onConfirmValidatedChange={model.setPayoutConfirmValidated}
        onCloseTimeRippleChange={model.setPayoutCloseTimeRipple}
        onPrepare={() => {
          void model.handlePayoutPrepare();
        }}
        onReconcile={() => {
          void model.handlePayoutReconcile();
        }}
        onConfirm={() => {
          void model.handlePayoutConfirm();
        }}
      />

      {model.lastError ? <p className="error-banner">{model.lastError}</p> : null}

      <OutputPanel
        registerResult={model.registerResult}
        escrowPrepareResult={model.escrowPrepareResult}
        escrowReconcileResult={model.escrowReconcileResult}
        escrowConfirmResult={model.escrowConfirmResult}
        resultEntry={model.resultEntry}
        payoutPrepareResult={model.payoutPrepareResult}
        payoutReconcileResult={model.payoutReconcileResult}
        payoutConfirmResult={model.payoutConfirmResult}
      />

      <StatusConsole entries={model.actionLog} />
    </main>
  );
}

