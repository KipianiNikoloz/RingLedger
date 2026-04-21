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
        <div className="hero-copy">
          <p className="eyebrow">RingLedger</p>
          <h1>Control bout settlement with a calmer financial workflow.</h1>
          <p className="hero-body">
            RingLedger gives promoters and admins one surface for XRPL escrow creation, result entry, payout closeout,
            and evidence review without shifting lifecycle authority away from the backend.
          </p>
          <div className="hero-actions">
            <NavLink currentPath={currentPath} href="/app" label="Enter operator workspace" onNavigate={onNavigate} variant="strong" />
            <a className="text-link" href="#capabilities">
              Explore the platform
            </a>
          </div>
          <div className="hero-proof-row" aria-label="Platform proof points">
            <span>Promoter signing via Xaman</span>
            <span>Admin result control</span>
            <span>Ledger-validated closeout</span>
          </div>
        </div>

        <section className="hero-product-shot" aria-label="RingLedger workflow product preview">
          <div className="product-shot-frame">
            <div className="product-topline">
              <span>RingLedger Workspace</span>
              <span>Live operator view</span>
            </div>
            <div className="product-layout">
              <article className="product-primary-pane">
                <div className="product-pane-head">
                  <p className="mini-label">Bout lifecycle</p>
                  <strong>BK-2048 · Event ready</strong>
                </div>
                <ul className="product-stage-list">
                  <li>
                    <span>Escrow creation</span>
                    <strong>Validated</strong>
                  </li>
                  <li>
                    <span>Result entry</span>
                    <strong>Pending admin</strong>
                  </li>
                  <li>
                    <span>Payout closeout</span>
                    <strong>Queued</strong>
                  </li>
                </ul>
              </article>
              <article className="product-detail-pane">
                <div>
                  <p className="mini-label">Role posture</p>
                  <strong>Promoter + admin tokens active</strong>
                </div>
                <div>
                  <p className="mini-label">Latest confirmed action</p>
                  <strong>EscrowCreate evidence accepted</strong>
                </div>
                <div>
                  <p className="mini-label">Control model</p>
                  <strong>Frontend untrusted, backend authoritative</strong>
                </div>
              </article>
            </div>
          </div>
        </section>
      </section>

      <section className="proof-band" aria-label="Platform scale and control">
        <article>
          <span className="proof-value">4</span>
          <p>escrows planned per 1v1 bout lifecycle</p>
        </article>
        <article>
          <span className="proof-value">2</span>
          <p>operator roles driving promoter and admin actions</p>
        </article>
        <article>
          <span className="proof-value">100%</span>
          <p>ledger state transitions gated by validated backend evidence</p>
        </article>
      </section>

      <section className="story-section" aria-labelledby="trust-heading">
        <div className="section-heading">
          <p className="eyebrow">Who it serves</p>
          <h2 id="trust-heading">Built for the people who actually move the bout lifecycle forward.</h2>
        </div>
        <div className="feature-ribbon">
          <article>
            <h3>Promoters</h3>
            <p>Prepare escrows, reconcile signing, and confirm payout actions with Xaman-linked evidence in one place.</p>
          </article>
          <article>
            <h3>Admins</h3>
            <p>Record winners at the correct lifecycle point and keep payout direction explicit before closeout starts.</p>
          </article>
          <article>
            <h3>Operations teams</h3>
            <p>Review tokens, logs, and raw backend payloads without losing the structure of the workflow itself.</p>
          </article>
        </div>
      </section>

      <section id="capabilities" className="lifecycle-section capabilities-section" aria-labelledby="capabilities-heading">
        <div className="section-heading">
          <p className="eyebrow">Foundation</p>
          <h2 id="capabilities-heading">A strong operational foundation for a high-risk settlement path.</h2>
          <p className="section-body">
            RingLedger keeps the workflow calm by separating signing, lifecycle control, and proof review into a single
            operator surface with typed backend contracts underneath.
          </p>
        </div>
        <div className="timeline-grid capabilities-grid">
          <article>
            <h3>Backend-authoritative lifecycle</h3>
            <p>Role checks, timing rules, and ledger truth stay server-side. The frontend only drives the approved path.</p>
          </article>
          <article>
            <h3>Xaman-first signing</h3>
            <p>Promoters sign without the platform storing private keys, while the workflow still captures payload status and evidence.</p>
          </article>
          <article>
            <h3>Typed API evidence</h3>
            <p>Each action returns deterministic payloads so operators can inspect exactly what the backend accepted.</p>
          </article>
        </div>
      </section>

      <section className="platform-section" aria-labelledby="platform-heading">
        <div className="section-heading">
          <p className="eyebrow">Modern capabilities</p>
          <h2 id="platform-heading">One product surface for preparation, confirmation, and closeout.</h2>
        </div>
        <div className="platform-grid">
          <article>
            <p className="timeline-step">01</p>
            <h3>Authenticate by role</h3>
            <p>Load promoter and admin tokens into the active session before acting on bout state.</p>
          </article>
          <article>
            <p className="timeline-step">02</p>
            <h3>Create escrows</h3>
            <p>Prepare, reconcile, and confirm validated `EscrowCreate` transactions for each escrow kind.</p>
          </article>
          <article>
            <p className="timeline-step">03</p>
            <h3>Record the result</h3>
            <p>Keep winner entry isolated to the admin checkpoint before payout operations begin.</p>
          </article>
          <article>
            <p className="timeline-step">04</p>
            <h3>Close out payouts</h3>
            <p>Finish or cancel payout escrows and only advance the bout when the evidence is valid.</p>
          </article>
        </div>
      </section>

      <section className="roles-section security-section" aria-labelledby="roles-heading">
        <div className="section-heading">
          <p className="eyebrow">Secure by design</p>
          <h2 id="roles-heading">Trust comes from controls, not from a prettier dashboard.</h2>
        </div>
        <div className="roles-grid">
          <article>
            <h3>Untrusted frontend model</h3>
            <p>Operators can drive workflows, but lifecycle invariants and settlement rules are never enforced in the browser.</p>
          </article>
          <article>
            <h3>Role-scoped actions</h3>
            <p>Promoter and admin capabilities stay separated, which keeps result entry and signing responsibilities clear.</p>
          </article>
          <article>
            <h3>Evidence-led transitions</h3>
            <p>Confirmed ledger results, idempotent endpoints, and deterministic payloads keep closeout auditable.</p>
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
