import type { ReactNode } from "react";

import { AuthPanel } from "../components/AuthPanel";
import { BoutWorkspacePanel } from "../components/BoutWorkspacePanel";
import { EscrowFlowPanel } from "../components/EscrowFlowPanel";
import { OutputPanel } from "../components/OutputPanel";
import { PayoutFlowPanel } from "../components/PayoutFlowPanel";
import { ResultEntryPanel } from "../components/ResultEntryPanel";
import { StatusConsole } from "../components/StatusConsole";
import { type RingLedgerConsoleModel, useRingLedgerConsole } from "../hooks/useRingLedgerConsole";
import { HomePage as FocusedHomePage } from "./HomePage";
import { usePathname } from "./usePathname";

type StageState = "complete" | "in-progress" | "pending" | "failed";

interface NavLinkProps {
  currentPath: string;
  href: string;
  label: string;
  onNavigate: (href: string) => void;
  variant?: "default" | "strong";
}

interface StageSummary {
  id: "auth" | "escrows" | "result" | "payouts";
  index: string;
  label: string;
  state: StageState;
  summary: string;
}

interface EvidenceItem {
  label: string;
  value: string;
  tone?: "operator" | "signing" | "backend" | "ledger" | "failure";
}

function NavLink({ currentPath, href, label, onNavigate, variant = "default" }: NavLinkProps) {
  const isActive = currentPath === href;

  return (
    <a
      className={`nav-link nav-link-${variant}`}
      data-active={isActive}
      href={href}
      onClick={(event) => {
        event.preventDefault();
        onNavigate(href);
      }}
    >
      {label}
    </a>
  );
}

interface HomePageProps {
  currentPath: string;
  onNavigate: (href: string) => void;
}

function HomePage({ currentPath, onNavigate }: HomePageProps) {
  return (
    <main className="site-shell home-shell">
      <section className="entry-console" aria-labelledby="home-heading">
        <div className="entry-copy">
          <p className="eyebrow">RingLedger</p>
          <h1 id="home-heading">Backend-authoritative escrow settlement console.</h1>
          <p className="hero-body">
            RingLedger gives operators one dark control surface for XRPL escrow preparation, Xaman signing reconciliation,
            result entry, payout closeout, and backend evidence review.
          </p>
          <div className="hero-actions">
            <NavLink
              currentPath={currentPath}
              href="/app"
              label="Enter operator workspace"
              onNavigate={onNavigate}
              variant="strong"
            />
            <a className="text-link" href="#trust-boundaries">
              Review trust boundaries
            </a>
          </div>
        </div>

        <div className="entry-status-board" aria-label="RingLedger trust boundary summary">
          <div className="entry-status-header">
            <span>Settlement Control</span>
            <strong>XRPL Testnet</strong>
          </div>
          <div className="entry-status-grid">
            <article data-tone="operator">
              <span>Operator action</span>
              <strong>Prepare and submit</strong>
            </article>
            <article data-tone="signing">
              <span>Xaman signing</span>
              <strong>Payload status</strong>
            </article>
            <article data-tone="backend">
              <span>Backend authority</span>
              <strong>Lifecycle gates</strong>
            </article>
            <article data-tone="ledger">
              <span>XRPL evidence</span>
              <strong>Validated results</strong>
            </article>
          </div>
        </div>
      </section>

      <section id="trust-boundaries" className="home-trust-band" aria-labelledby="trust-heading">
        <div>
          <p className="eyebrow">Operating model</p>
          <h2 id="trust-heading">The browser drives approved actions. The backend and ledger remain the source of truth.</h2>
        </div>
        <div className="trust-grid">
          <article>
            <h3>Authenticate</h3>
            <p>Promoter and admin role tokens stay visible as session posture.</p>
          </article>
          <article>
            <h3>Escrows</h3>
            <p>Escrow creation moves through prepare, signing reconciliation, and confirmation.</p>
          </article>
          <article>
            <h3>Result</h3>
            <p>Winner entry is isolated before payout direction can be closed.</p>
          </article>
          <article>
            <h3>Payouts</h3>
            <p>Finish and cancel actions expose signing and ledger evidence for review.</p>
          </article>
        </div>
      </section>
    </main>
  );
}

function OperatorWorkspacePage() {
  const model = useRingLedgerConsole();
  const stages = buildStageSummaries(model);
  const activeStage = stages.find((stage) => stage.state === "failed" || stage.state === "in-progress") ?? stages[0];
  const activeRoles = getActiveRoles(model);
  const latestAction = model.actionLog[0] ?? "No actions recorded";
  const latestResponse = getLatestResponse(model);
  const signingEvidence = getSigningEvidence(model);
  const ledgerEvidence = getLedgerEvidence(model);
  const failureEvidence = getFailureEvidence(model);

  return (
    <main className="operator-shell" aria-labelledby="workspace-heading">
      <section className="workspace-header">
        <div>
          <p className="eyebrow">Operator Workspace</p>
          <h1 id="workspace-heading">Settlement control room</h1>
          <p className="hero-body">Backend and XRPL evidence are the source of truth for every lifecycle transition.</p>
        </div>
        <div className="workspace-status">
          <label>
            Network
            <select aria-label="Network">
              <option>XRPL Testnet</option>
            </select>
          </label>
          <span className="status-chip status-chip-ledger">Backend online</span>
          <button className="icon-button" type="button" aria-label="Notifications">
            N
          </button>
          <button className="icon-button" type="button" aria-label="Help">
            ?
          </button>
          <span className="avatar-mark" aria-label="Operator profile">
            OP
          </span>
        </div>
      </section>

      <section className="lifecycle-stepper" aria-label="RingLedger lifecycle stages">
        {stages.map((stage) => (
          <article className="lifecycle-step" data-state={stage.state} key={stage.id}>
            <span className="step-marker">{stage.index}</span>
            <div>
              <span className="step-label">{stage.label}</span>
              <strong>{formatStageState(stage.state)}</strong>
              <p>{stage.summary}</p>
            </div>
          </article>
        ))}
      </section>

      <div className="workbench-grid">
        <div className="operations-grid">
          <aside className="context-rail" aria-label="Session and bout context">
            <section className="panel rail-panel">
              <div className="panel-header">
                <p className="eyebrow">Session</p>
                <h2>Operator context</h2>
                <p className="panel-note">Active role, bout, stage, and latest confirmed action.</p>
              </div>
              <dl className="definition-grid">
                <div>
                  <dt>Active roles</dt>
                  <dd>{activeRoles.length > 0 ? activeRoles.join(", ") : "none"}</dd>
                </div>
                <div>
                  <dt>Auth posture</dt>
                  <dd>{activeRoles.length > 0 ? "token state loaded" : "login required"}</dd>
                </div>
                <div>
                  <dt>Bout ID</dt>
                  <dd>{model.boutId.trim() || "not selected"}</dd>
                </div>
                <div>
                  <dt>Current stage</dt>
                  <dd>{activeStage.label}</dd>
                </div>
                <div>
                  <dt>Latest action</dt>
                  <dd>{summarizeAction(latestAction)}</dd>
                </div>
              </dl>
            </section>

            <section className="panel rail-panel">
              <div className="panel-header">
                <p className="eyebrow">Task list</p>
                <h2>Run order</h2>
              </div>
              <ol className="operator-task-list">
                {stages.map((stage) => (
                  <li data-state={stage.state} key={stage.id}>
                    <span>{stage.index}</span>
                    <div>
                      <strong>{stage.label}</strong>
                      <p>{stage.summary}</p>
                    </div>
                  </li>
                ))}
              </ol>
            </section>
          </aside>

          <section className="workspace-column" aria-label="Active lifecycle controls">
            {model.lastError ? <p className="error-banner">{model.lastError}</p> : null}

            <section className="flow-shell" aria-labelledby="stage-auth">
              <StageHeader index="01" title="Authenticate" description="Load promoter and admin role tokens for this session." id="stage-auth" />
              <AuthPanel
                busy={model.busy}
                currentRoleSummary={model.currentRoleSummary}
                registerEmail={model.registerEmail}
                registerPassword={model.registerPassword}
                provisionEmail={model.provisionEmail}
                provisionPassword={model.provisionPassword}
                provisionRole={model.provisionRole}
                loginEmail={model.loginEmail}
                loginPassword={model.loginPassword}
                onRegisterEmailChange={model.setRegisterEmail}
                onRegisterPasswordChange={model.setRegisterPassword}
                onProvisionEmailChange={model.setProvisionEmail}
                onProvisionPasswordChange={model.setProvisionPassword}
                onProvisionRoleChange={model.setProvisionRole}
                onLoginEmailChange={model.setLoginEmail}
                onLoginPasswordChange={model.setLoginPassword}
                onRegister={(event) => {
                  void model.handleRegister(event);
                }}
                onProvision={(event) => {
                  void model.handleProvision(event);
                }}
                onLogin={(event) => {
                  void model.handleLogin(event);
                }}
              />
            </section>

            <section className="flow-shell" aria-labelledby="stage-escrows">
              <StageHeader
                index="02"
                title="Escrows"
                description="Prepare, reconcile, and confirm escrow creation for the active bout."
                id="stage-escrows"
              />
              <BoutWorkspacePanel
                busy={model.busy}
                boutId={model.boutId}
                fighterDisplayName={model.fighterDisplayName}
                fighterXrplAddress={model.fighterXrplAddress}
                createFighterAUserId={model.createFighterAUserId}
                createFighterBUserId={model.createFighterBUserId}
                createEventDatetimeUtc={model.createEventDatetimeUtc}
                createPromoterOwnerAddress={model.createPromoterOwnerAddress}
                createShowADrops={model.createShowADrops}
                createShowBDrops={model.createShowBDrops}
                createBonusADrops={model.createBonusADrops}
                createBonusBDrops={model.createBonusBDrops}
                listCount={model.boutListResult?.bouts.length ?? null}
                onBoutIdChange={model.setBoutId}
                onFighterDisplayNameChange={model.setFighterDisplayName}
                onFighterXrplAddressChange={model.setFighterXrplAddress}
                onCreateFighterAUserIdChange={model.setCreateFighterAUserId}
                onCreateFighterBUserIdChange={model.setCreateFighterBUserId}
                onCreateEventDatetimeUtcChange={model.setCreateEventDatetimeUtc}
                onCreatePromoterOwnerAddressChange={model.setCreatePromoterOwnerAddress}
                onCreateShowADropsChange={model.setCreateShowADrops}
                onCreateShowBDropsChange={model.setCreateShowBDrops}
                onCreateBonusADropsChange={model.setCreateBonusADrops}
                onCreateBonusBDropsChange={model.setCreateBonusBDrops}
                onFighterProfileUpsert={(event) => {
                  void model.handleFighterProfileUpsert(event);
                }}
                onBoutCreate={(event) => {
                  void model.handleBoutCreate(event);
                }}
                onBoutList={() => {
                  void model.handleBoutList();
                }}
                onBoutLoad={() => {
                  void model.handleBoutLoad();
                }}
              />
              <EscrowFlowPanel
                busy={model.busy}
                reconcileKind={model.escrowReconcileKind}
                reconcileStatus={model.escrowReconcileStatus}
                reconcileTxHash={model.escrowReconcileTxHash}
                confirmKind={model.escrowConfirmKind}
                confirmTxHash={model.escrowConfirmTxHash}
                onReconcileKindChange={model.setEscrowReconcileKind}
                onReconcileStatusChange={model.setEscrowReconcileStatus}
                onReconcileTxHashChange={model.setEscrowReconcileTxHash}
                onConfirmKindChange={model.setEscrowConfirmKind}
                onConfirmTxHashChange={model.setEscrowConfirmTxHash}
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
            </section>

            <section className="flow-shell" aria-labelledby="stage-result">
              <StageHeader index="03" title="Result" description="Enter the winner once escrow creation evidence is ready." id="stage-result" />
              <ResultEntryPanel
                busy={model.busy}
                winner={model.winner}
                onWinnerChange={model.setWinner}
                onSubmit={() => {
                  void model.handleResultEntry();
                }}
              />
            </section>

            <section className="flow-shell" aria-labelledby="stage-payouts">
              <StageHeader
                index="04"
                title="Payouts"
                description="Prepare payout actions, reconcile signing, and confirm ledger closeout."
                id="stage-payouts"
              />
              <PayoutFlowPanel
                busy={model.busy}
                reconcileKind={model.payoutReconcileKind}
                reconcileStatus={model.payoutReconcileStatus}
                reconcileTxHash={model.payoutReconcileTxHash}
                confirmKind={model.payoutConfirmKind}
                confirmTxHash={model.payoutConfirmTxHash}
                onReconcileKindChange={model.setPayoutReconcileKind}
                onReconcileStatusChange={model.setPayoutReconcileStatus}
                onReconcileTxHashChange={model.setPayoutReconcileTxHash}
                onConfirmKindChange={model.setPayoutConfirmKind}
                onConfirmTxHashChange={model.setPayoutConfirmTxHash}
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
            </section>
          </section>
        </div>

        <aside className="evidence-rail" aria-label="Evidence and output">
          <EvidencePanel title="Latest backend response" description="Most recent payload accepted by the frontend model.">
            <EvidenceList
              items={[
                { label: "Response", value: latestResponse.label, tone: "backend" },
                { label: "Bout", value: latestResponse.boutId, tone: "operator" },
                { label: "Status", value: latestResponse.status, tone: latestResponse.statusTone },
              ]}
            />
          </EvidencePanel>

          <EvidencePanel title="Xaman signing state" description="Payload and signing status surfaced from prepare or reconcile responses.">
            <EvidenceList items={signingEvidence} />
          </EvidencePanel>

          <EvidencePanel title="XRPL ledger evidence" description="Validated ledger details from confirm responses.">
            <EvidenceList items={ledgerEvidence} />
          </EvidencePanel>

          <EvidencePanel title="Failure classification" description="Last deterministic error or signing failure code.">
            <EvidenceList items={failureEvidence} />
          </EvidencePanel>

          <StatusConsole entries={model.actionLog} />

          <section className="panel output-panel-wrap">
            <div className="panel-header">
              <p className="eyebrow">Raw output</p>
              <h2>Backend payloads</h2>
              <p className="panel-note">Full JSON remains available for audit and troubleshooting.</p>
            </div>
            <OutputPanel
              registerResult={model.registerResult}
              fighterProfileResult={model.fighterProfileResult}
              boutCreateResult={model.boutCreateResult}
              boutListResult={model.boutListResult}
              boutDetailResult={model.boutDetailResult}
              escrowPrepareResult={model.escrowPrepareResult}
              escrowReconcileResult={model.escrowReconcileResult}
              escrowConfirmResult={model.escrowConfirmResult}
              resultEntry={model.resultEntry}
              payoutPrepareResult={model.payoutPrepareResult}
              payoutReconcileResult={model.payoutReconcileResult}
              payoutConfirmResult={model.payoutConfirmResult}
            />
          </section>
        </aside>
      </div>

      <TrustBoundaryLegend />
    </main>
  );
}

interface StageHeaderProps {
  id: string;
  index: string;
  title: string;
  description: string;
}

function StageHeader({ id, index, title, description }: StageHeaderProps) {
  return (
    <div className="stage-header">
      <span className="stage-index">{index}</span>
      <div>
        <h2 id={id}>{title}</h2>
        <p>{description}</p>
      </div>
    </div>
  );
}

interface EvidencePanelProps {
  title: string;
  description: string;
  children: ReactNode;
}

function EvidencePanel({ title, description, children }: EvidencePanelProps) {
  return (
    <section className="panel evidence-panel">
      <div className="panel-header">
        <h2>{title}</h2>
        <p className="panel-note">{description}</p>
      </div>
      {children}
    </section>
  );
}

function EvidenceList({ items }: { items: EvidenceItem[] }) {
  return (
    <dl className="evidence-list">
      {items.map((item) => (
        <div data-tone={item.tone ?? "backend"} key={item.label}>
          <dt>{item.label}</dt>
          <dd>{item.value}</dd>
        </div>
      ))}
    </dl>
  );
}

function TrustBoundaryLegend() {
  return (
    <section className="trust-boundary-legend" aria-label="Trust-boundary color legend">
      <article data-tone="operator">
        <span />
        <div>
          <strong>Operator Actions</strong>
          <p>Cyan marks human-driven commands and the current workflow stage.</p>
        </div>
      </article>
      <article data-tone="signing">
        <span />
        <div>
          <strong>Signing State</strong>
          <p>Blue marks Xaman payloads, signing status, and observed transaction hashes.</p>
        </div>
      </article>
      <article data-tone="backend">
        <span />
        <div>
          <strong>Backend Processing</strong>
          <p>Amber marks pending server-side lifecycle processing.</p>
        </div>
      </article>
      <article data-tone="ledger">
        <span />
        <div>
          <strong>Ledger Evidence</strong>
          <p>Green marks validated backend or XRPL confirmation evidence.</p>
        </div>
      </article>
    </section>
  );
}

function NotFoundPage({ onNavigate, currentPath }: HomePageProps) {
  return (
    <main className="site-shell not-found-shell">
      <section className="final-cta">
        <div>
          <p className="eyebrow">404</p>
          <h1>Route outside the settlement workspace.</h1>
        </div>
        <div className="final-cta-actions">
          <NavLink currentPath={currentPath} href="/" label="Back to entry" onNavigate={onNavigate} variant="strong" />
          <NavLink currentPath={currentPath} href="/app" label="Open operator workspace" onNavigate={onNavigate} />
        </div>
      </section>
    </main>
  );
}

export function AppShell() {
  const { pathname, navigate } = usePathname();
  const route = pathname === "/" || pathname === "/app" ? pathname : "/404";

  return (
    <div className="app-frame">
      <header className="topbar">
        <NavLink currentPath={pathname} href="/" label="RingLedger" onNavigate={navigate} variant="strong" />
        <div className="topbar-center" aria-label="Workspace identity">
          <span>Operator Workspace</span>
          <strong>XRPL escrow lifecycle</strong>
        </div>
        <nav className="topbar-nav" aria-label="Primary">
          <NavLink currentPath={pathname} href="/" label="Home" onNavigate={navigate} />
          <NavLink currentPath={pathname} href="/app" label="Workspace" onNavigate={navigate} />
        </nav>
      </header>

      {route === "/" ? <FocusedHomePage currentPath={pathname} onNavigate={navigate} /> : null}
      {route === "/app" ? <OperatorWorkspacePage /> : null}
      {route === "/404" ? <NotFoundPage currentPath={pathname} onNavigate={navigate} /> : null}
    </div>
  );
}

function buildStageSummaries(model: RingLedgerConsoleModel): StageSummary[] {
  const roles = getActiveRoles(model);
  const failedStage = getLatestFailureStage(model);
  const authComplete = roles.length > 0;
  const escrowStarted = Boolean(
    model.boutId ||
      model.boutCreateResult ||
      model.boutDetailResult ||
      model.escrowPrepareResult ||
      model.escrowReconcileResult ||
      model.escrowConfirmResult,
  );
  const escrowComplete = Boolean(model.escrowConfirmResult);
  const resultComplete = Boolean(model.resultEntry);
  const payoutStarted = Boolean(model.payoutPrepareResult || model.payoutReconcileResult || model.payoutConfirmResult);
  const payoutComplete = Boolean(model.payoutConfirmResult);

  return [
    {
      id: "auth",
      index: "01",
      label: "Authenticate",
      state: failedStage === "auth" ? "failed" : authComplete ? "complete" : "in-progress",
      summary: authComplete ? `${roles.join(", ")} token state active` : "Promoter/admin token required",
    },
    {
      id: "escrows",
      index: "02",
      label: "Escrows",
      state: failedStage === "escrows" ? "failed" : escrowComplete ? "complete" : escrowStarted ? "in-progress" : "pending",
      summary: escrowComplete ? `${model.escrowConfirmResult?.escrow_kind} confirmed` : "Create/select, prepare, confirm",
    },
    {
      id: "result",
      index: "03",
      label: "Result",
      state: failedStage === "result" ? "failed" : resultComplete ? "complete" : escrowComplete ? "in-progress" : "pending",
      summary: resultComplete ? `Winner ${model.resultEntry?.winner} recorded` : "Admin winner entry",
    },
    {
      id: "payouts",
      index: "04",
      label: "Payouts",
      state: failedStage === "payouts" ? "failed" : payoutComplete ? "complete" : payoutStarted ? "in-progress" : "pending",
      summary: payoutComplete ? `${model.payoutConfirmResult?.escrow_kind} ${model.payoutConfirmResult?.escrow_status}` : "Prepare closeout actions",
    },
  ];
}

function getActiveRoles(model: RingLedgerConsoleModel): string[] {
  return model.currentRoleSummary === "none" ? [] : model.currentRoleSummary.split(", ");
}

function getLatestFailureStage(model: RingLedgerConsoleModel): StageSummary["id"] | null {
  if (!model.lastError) {
    return null;
  }
  const latest = model.actionLog[0]?.toLowerCase() ?? "";
  if (latest.includes("payout")) {
    return "payouts";
  }
  if (latest.includes("result")) {
    return "result";
  }
  if (latest.includes("escrow")) {
    return "escrows";
  }
  return "auth";
}

function formatStageState(state: StageState): string {
  if (state === "in-progress") {
    return "in progress";
  }
  return state;
}

function summarizeAction(action: string): string {
  const [, message] = action.split("|").map((part) => part.trim());
  return message || action;
}

function getLatestResponse(model: RingLedgerConsoleModel): {
  label: string;
  boutId: string;
  status: string;
  statusTone: EvidenceItem["tone"];
} {
  if (model.payoutConfirmResult) {
    return {
      label: "Payout Confirm",
      boutId: model.payoutConfirmResult.bout_id,
      status: model.payoutConfirmResult.bout_status,
      statusTone: "ledger",
    };
  }
  if (model.payoutReconcileResult) {
    return {
      label: "Payout Reconcile",
      boutId: model.payoutReconcileResult.bout_id,
      status: model.payoutReconcileResult.signing_status,
      statusTone: model.payoutReconcileResult.failure_code ? "failure" : "signing",
    };
  }
  if (model.payoutPrepareResult) {
    return {
      label: "Payout Prepare",
      boutId: model.payoutPrepareResult.bout_id,
      status: model.payoutPrepareResult.bout_status,
      statusTone: "backend",
    };
  }
  if (model.resultEntry) {
    return {
      label: "Result Entry",
      boutId: model.resultEntry.bout_id,
      status: model.resultEntry.bout_status,
      statusTone: "backend",
    };
  }
  if (model.escrowConfirmResult) {
    return {
      label: "Escrow Confirm",
      boutId: model.escrowConfirmResult.bout_id,
      status: model.escrowConfirmResult.bout_status,
      statusTone: "ledger",
    };
  }
  if (model.escrowReconcileResult) {
    return {
      label: "Escrow Reconcile",
      boutId: model.escrowReconcileResult.bout_id,
      status: model.escrowReconcileResult.signing_status,
      statusTone: model.escrowReconcileResult.failure_code ? "failure" : "signing",
    };
  }
  if (model.escrowPrepareResult) {
    return {
      label: "Escrow Prepare",
      boutId: model.escrowPrepareResult.bout_id,
      status: `${model.escrowPrepareResult.escrows.length} payloads`,
      statusTone: "backend",
    };
  }
  if (model.boutDetailResult) {
    return {
      label: "Bout Detail",
      boutId: model.boutDetailResult.bout_id,
      status: model.boutDetailResult.bout_status,
      statusTone: "backend",
    };
  }
  if (model.boutCreateResult) {
    return {
      label: "Bout Create",
      boutId: model.boutCreateResult.bout_id,
      status: model.boutCreateResult.bout_status,
      statusTone: "backend",
    };
  }
  if (model.fighterProfileResult) {
    return {
      label: "Fighter Profile",
      boutId: model.boutId.trim() || "not selected",
      status: "profile saved",
      statusTone: "operator",
    };
  }
  if (model.registerResult) {
    return {
      label: "Register Response",
      boutId: model.boutId.trim() || "not selected",
      status: "role created",
      statusTone: "operator",
    };
  }
  return {
    label: "No response yet",
    boutId: model.boutId.trim() || "not selected",
    status: "waiting for action",
    statusTone: "backend",
  };
}

function getSigningEvidence(model: RingLedgerConsoleModel): EvidenceItem[] {
  const reconcile = model.payoutReconcileResult ?? model.escrowReconcileResult;
  const preparedPayout = model.payoutPrepareResult?.escrows[0];
  const preparedEscrow = model.escrowPrepareResult?.escrows[0];
  const prepared = preparedPayout ?? preparedEscrow;

  return [
    {
      label: "Payload ID",
      value: reconcile?.payload_id ?? prepared?.xaman_sign_request.payload_id ?? "pending",
      tone: "signing",
    },
    {
      label: "Signing status",
      value: reconcile?.signing_status ?? "not reconciled",
      tone: reconcile?.failure_code ? "failure" : "signing",
    },
    {
      label: "Observed tx",
      value: reconcile?.tx_hash ?? "not observed",
      tone: reconcile?.tx_hash ? "ledger" : "signing",
    },
    {
      label: "Mode",
      value: prepared?.xaman_sign_request.mode ?? "pending",
      tone: "backend",
    },
  ];
}

function getLedgerEvidence(model: RingLedgerConsoleModel): EvidenceItem[] {
  const confirm = model.payoutConfirmResult ?? model.escrowConfirmResult;

  return [
    {
      label: "Tx hash",
      value: confirm?.tx_hash ?? "pending",
      tone: confirm?.tx_hash ? "ledger" : "backend",
    },
    {
      label: "Escrow kind",
      value: confirm?.escrow_kind ?? model.payoutConfirmKind ?? model.escrowConfirmKind,
      tone: "operator",
    },
    {
      label: "Escrow status",
      value: confirm?.escrow_status ?? "not confirmed",
      tone: confirm ? "ledger" : "backend",
    },
    {
      label: "Evidence authority",
      value: "XRPL Testnet via backend",
      tone: "ledger",
    },
  ];
}

function getFailureEvidence(model: RingLedgerConsoleModel): EvidenceItem[] {
  const failureCode = model.payoutReconcileResult?.failure_code ?? model.escrowReconcileResult?.failure_code ?? null;

  return [
    {
      label: "Last error",
      value: model.lastError ?? "none",
      tone: model.lastError ? "failure" : "ledger",
    },
    {
      label: "Failure code",
      value: failureCode ?? "none",
      tone: failureCode ? "failure" : "ledger",
    },
    {
      label: "Latest log",
      value: summarizeAction(model.actionLog[0] ?? "No actions recorded"),
      tone: model.lastError ? "failure" : "backend",
    },
  ];
}
