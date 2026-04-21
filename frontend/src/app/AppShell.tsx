import { AuthPanel } from "../components/AuthPanel";
import { BoutWorkspacePanel } from "../components/BoutWorkspacePanel";
import { EscrowFlowPanel } from "../components/EscrowFlowPanel";
import { OutputPanel } from "../components/OutputPanel";
import { PayoutFlowPanel } from "../components/PayoutFlowPanel";
import { ResultEntryPanel } from "../components/ResultEntryPanel";
import { StatusConsole } from "../components/StatusConsole";
import { useRingLedgerConsole } from "../hooks/useRingLedgerConsole";
import { usePathname } from "./usePathname";

interface NavLinkProps {
  currentPath: string;
  href: string;
  label: string;
  onNavigate: (href: string) => void;
  variant?: "default" | "strong";
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
      <section className="home-hero">
        <div className="hero-grid">
          <div className="hero-copy">
            <p className="eyebrow">RingLedger</p>
            <h1>XRPL escrow settlement for fight-night operations.</h1>
            <p className="hero-body">
              RingLedger coordinates purse escrows, promoter signing, result entry, and payout closeout without moving
              lifecycle authority out of the backend.
            </p>
            <div className="hero-actions">
              <NavLink currentPath={currentPath} href="/app" label="Enter operator workspace" onNavigate={onNavigate} variant="strong" />
              <a className="text-link" href="#lifecycle">
                Explore the lifecycle
              </a>
            </div>
          </div>

          <section className="hero-visual" aria-label="RingLedger workflow summary">
            <div className="visual-kicker">
              <span>Promoter signing</span>
              <span>Admin result control</span>
              <span>Ledger-validated closeout</span>
            </div>

            <div className="visual-orbit">
              <article>
                <p className="mini-label">Stage 01</p>
                <h2>Prepare escrows</h2>
                <p>Unsigned XRPL payloads plus Xaman sign requests are generated per bout.</p>
              </article>
              <article>
                <p className="mini-label">Stage 02</p>
                <h2>Reconcile and confirm</h2>
                <p>Signing outcomes are reconciled, then ledger evidence is validated before state transitions.</p>
              </article>
              <article>
                <p className="mini-label">Stage 03</p>
                <h2>Result and payout</h2>
                <p>Admin enters the winner, promoter signs payout actions, and the bout closes only on valid completion.</p>
              </article>
            </div>
          </section>
        </div>
      </section>

      <section className="story-section" aria-labelledby="trust-heading">
        <div className="section-heading">
          <p className="eyebrow">Why it exists</p>
          <h2 id="trust-heading">A product surface for a brittle financial workflow.</h2>
        </div>
        <div className="feature-ribbon">
          <article>
            <h3>Backend remains authoritative</h3>
            <p>Frontend actions only drive typed API contracts. Invariants, role checks, timing rules, and ledger truth stay server-side.</p>
          </article>
          <article>
            <h3>Xaman-first promoter signing</h3>
            <p>Promoters sign without handing private keys to the platform. RingLedger tracks status and confirmation evidence around that boundary.</p>
          </article>
          <article>
            <h3>Bout-state clarity</h3>
            <p>Escrow creation, result entry, payout progress, and closeout align to an explicit lifecycle instead of ad hoc manual bookkeeping.</p>
          </article>
        </div>
      </section>

      <section id="lifecycle" className="lifecycle-section" aria-labelledby="lifecycle-heading">
        <div className="section-heading">
          <p className="eyebrow">Lifecycle</p>
          <h2 id="lifecycle-heading">Four operator moments, one controlled path to settlement.</h2>
        </div>
        <div className="timeline-grid">
          <article>
            <p className="timeline-step">01</p>
            <h3>Authenticate by role</h3>
            <p>Promoter and admin tokens unlock only the actions their lifecycle step requires.</p>
          </article>
          <article>
            <p className="timeline-step">02</p>
            <h3>Create escrows</h3>
            <p>Prepare, reconcile signing, then confirm validated `EscrowCreate` transactions for all four bout escrows.</p>
          </article>
          <article>
            <p className="timeline-step">03</p>
            <h3>Record the result</h3>
            <p>Admin enters the winner once escrow creation has completed and before payout closeout begins.</p>
          </article>
          <article>
            <p className="timeline-step">04</p>
            <h3>Finish or cancel payouts</h3>
            <p>Promoter finalizes payout operations, while the backend validates evidence before the bout reaches `closed`.</p>
          </article>
        </div>
      </section>

      <section className="roles-section" aria-labelledby="roles-heading">
        <div className="section-heading">
          <p className="eyebrow">Operators</p>
          <h2 id="roles-heading">Built for promoters and admins, not for spectators.</h2>
        </div>
        <div className="roles-grid">
          <article>
            <h3>Promoter</h3>
            <p>Controls escrow and payout signing, reviews transaction evidence, and drives Xaman-linked actions.</p>
          </article>
          <article>
            <h3>Admin</h3>
            <p>Records fight outcomes and advances the lifecycle only through the result-entry boundary.</p>
          </article>
          <article>
            <h3>Platform</h3>
            <p>Owns fulfillment secrets and lifecycle enforcement while keeping frontend trust deliberately low.</p>
          </article>
        </div>
      </section>

      <section className="final-cta" aria-labelledby="cta-heading">
        <div>
          <p className="eyebrow">Workspace</p>
          <h2 id="cta-heading">Move from product story to the operating surface.</h2>
        </div>
        <div className="final-cta-actions">
          <NavLink currentPath={currentPath} href="/app" label="Open the app" onNavigate={onNavigate} variant="strong" />
          <p>Use the guided operator workspace to authenticate, stage escrows, submit results, and complete payouts.</p>
        </div>
      </section>
    </main>
  );
}

function OperatorWorkspacePage() {
  const model = useRingLedgerConsole();
  const activeRoles = model.currentRoleSummary === "none" ? [] : model.currentRoleSummary.split(", ");
  const latestActionTimestamp = model.actionLog[0]?.split("|")[0]?.trim() ?? "No actions yet.";
  const hasPromoter = activeRoles.includes("promoter");
  const hasAdmin = activeRoles.includes("admin");

  const stageCards = [
    {
      key: "auth",
      label: "Auth",
      title: "Session roles",
      summary: hasPromoter || hasAdmin ? `${activeRoles.join(", ")} token(s) loaded` : "No active role tokens",
      status: hasPromoter || hasAdmin ? "Ready" : "Required",
    },
    {
      key: "escrow",
      label: "Escrows",
      title: "Escrow creation",
      summary: model.escrowConfirmResult ? "Ledger confirmation recorded" : "Prepare, reconcile, and confirm creation",
      status: model.escrowConfirmResult ? "Advanced" : "Open",
    },
    {
      key: "result",
      label: "Result",
      title: "Winner entry",
      summary: model.resultEntry ? `Winner ${model.resultEntry.winner} submitted` : "Admin action still pending",
      status: model.resultEntry ? "Locked" : "Pending",
    },
    {
      key: "payout",
      label: "Payout",
      title: "Settlement closeout",
      summary: model.payoutConfirmResult ? "Payout confirmation recorded" : "Awaiting payout operations",
      status: model.payoutConfirmResult ? "Closed path" : "Queued",
    },
  ];

  return (
    <main className="site-shell app-shell">
      <section className="app-hero">
        <div className="app-hero-copy">
          <p className="eyebrow">Operator workspace</p>
          <h1>Guided settlement workflow for promoter and admin execution.</h1>
          <p className="hero-body">
            The app is organized around the bout lifecycle instead of raw panel sprawl. Actions still map directly to
            the existing backend contracts.
          </p>
        </div>
        <div className="hero-status-grid" aria-label="Workspace status">
          <article>
            <span>Active roles</span>
            <strong>{activeRoles.length}</strong>
          </article>
          <article>
            <span>Bout context</span>
            <strong>{model.boutId.trim() || "Unset"}</strong>
          </article>
          <article>
            <span>Latest action</span>
            <strong>{model.actionLog.length > 0 ? "Recorded" : "Pending"}</strong>
          </article>
          <article>
            <span>Timestamp</span>
            <strong>{latestActionTimestamp}</strong>
          </article>
        </div>
      </section>

      <section className="stage-overview" aria-label="Lifecycle overview">
        {stageCards.map((stage) => (
          <article className="stage-overview-card" key={stage.key}>
            <p className="mini-label">{stage.label}</p>
            <h2>{stage.title}</h2>
            <p>{stage.summary}</p>
            <span className="status-pill">{stage.status}</span>
          </article>
        ))}
      </section>

      <div className="app-grid">
        <section className="app-main-column">
          <section className="stage-section" aria-labelledby="stage-auth">
            <div className="stage-header">
              <p className="stage-index">01</p>
              <div>
                <h2 id="stage-auth">Authenticate and load roles</h2>
                <p>Keep promoter and admin tokens available in-session before moving deeper into the lifecycle.</p>
              </div>
            </div>
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
          </section>

          <section className="stage-section" aria-labelledby="stage-escrow">
            <div className="stage-header">
              <p className="stage-index">02</p>
              <div>
                <h2 id="stage-escrow">Create escrows for the active bout</h2>
                <p>Set bout context once, then drive prepare, signing reconciliation, and final confirmation in order.</p>
              </div>
            </div>
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
          </section>

          <section className="stage-section" aria-labelledby="stage-result">
            <div className="stage-header">
              <p className="stage-index">03</p>
              <div>
                <h2 id="stage-result">Record the bout result</h2>
                <p>Admin winner entry is isolated as its own step so payout direction is obvious before closeout begins.</p>
              </div>
            </div>
            <ResultEntryPanel
              busy={model.busy}
              winner={model.winner}
              onWinnerChange={model.setWinner}
              onSubmit={() => {
                void model.handleResultEntry();
              }}
            />
          </section>

          <section className="stage-section" aria-labelledby="stage-payout">
            <div className="stage-header">
              <p className="stage-index">04</p>
              <div>
                <h2 id="stage-payout">Complete payout settlement</h2>
                <p>Prepare payout actions, reconcile signing state, and confirm validated ledger closeout artifacts.</p>
              </div>
            </div>
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
          </section>
        </section>

        <aside className="app-side-column">
          {model.lastError ? <p className="error-banner">{model.lastError}</p> : null}

          <section className="panel rail-panel">
            <div className="panel-header">
              <h2>Operator snapshot</h2>
              <p className="panel-note">Fast orientation for the current session, bout, and role posture.</p>
            </div>
            <dl className="definition-grid">
              <div>
                <dt>Roles</dt>
                <dd>{model.currentRoleSummary}</dd>
              </div>
              <div>
                <dt>Bout ID</dt>
                <dd>{model.boutId.trim() || "No bout selected"}</dd>
              </div>
              <div>
                <dt>Winner</dt>
                <dd>{model.resultEntry?.winner ?? model.winner}</dd>
              </div>
              <div>
                <dt>Action timestamp</dt>
                <dd>{latestActionTimestamp}</dd>
              </div>
            </dl>
          </section>

          <StatusConsole entries={model.actionLog} />

          <section className="results-section">
            <div className="panel-header">
              <h2>Payload evidence</h2>
              <p className="panel-note">Latest backend responses remain available as operator reference data.</p>
            </div>
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
          </section>
        </aside>
      </div>
    </main>
  );
}

function NotFoundPage({ onNavigate, currentPath }: HomePageProps) {
  return (
    <main className="site-shell not-found-shell">
      <section className="final-cta">
        <div>
          <p className="eyebrow">404</p>
          <h1>That route does not belong to the workflow.</h1>
        </div>
        <div className="final-cta-actions">
          <NavLink currentPath={currentPath} href="/" label="Back to homepage" onNavigate={onNavigate} variant="strong" />
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
        <nav className="topbar-nav" aria-label="Primary">
          <NavLink currentPath={pathname} href="/" label="Home" onNavigate={navigate} />
          <NavLink currentPath={pathname} href="/app" label="Workspace" onNavigate={navigate} />
        </nav>
      </header>

      {route === "/" ? <HomePage currentPath={pathname} onNavigate={navigate} /> : null}
      {route === "/app" ? <OperatorWorkspacePage /> : null}
      {route === "/404" ? <NotFoundPage currentPath={pathname} onNavigate={navigate} /> : null}
    </div>
  );
}
