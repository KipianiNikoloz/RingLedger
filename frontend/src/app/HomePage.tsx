interface HomePageProps {
  currentPath: string;
  onNavigate: (href: string) => void;
}

export function HomePage({ currentPath, onNavigate }: HomePageProps) {
  return (
    <main className="site-shell home-shell">
      <section className="entry-console" aria-labelledby="home-heading">
        <div className="entry-copy">
          <p className="eyebrow">RingLedger</p>
          <h1 id="home-heading">Backend-authoritative escrow settlement console.</h1>
          <p className="hero-body">RingLedger unifies XRPL escrow preparation, Xaman reconciliation, result entry, payout closeout, and evidence review.</p>
          <div className="hero-actions">
            <a className="nav-link nav-link-strong" data-active={currentPath === "/app"} href="/app" onClick={(event) => { event.preventDefault(); onNavigate("/app"); }}>
              Enter operator workspace
            </a>
            <a className="text-link" href="#trust-boundaries">Review trust boundaries</a>
          </div>
        </div>
        <div className="entry-status-board" aria-label="RingLedger trust boundary summary">
          <div className="entry-status-header"><span>Settlement Control</span><strong>XRPL Testnet</strong></div>
          <div className="entry-status-grid">
            <article data-tone="operator"><span>Operator action</span><strong>Prepare and submit</strong></article>
            <article data-tone="signing"><span>Xaman signing</span><strong>Payload status</strong></article>
            <article data-tone="backend"><span>Backend authority</span><strong>Lifecycle gates</strong></article>
            <article data-tone="ledger"><span>XRPL evidence</span><strong>Validated results</strong></article>
          </div>
        </div>
      </section>
      <section id="trust-boundaries" className="home-trust-band" aria-labelledby="trust-heading">
        <div><p className="eyebrow">Operating model</p><h2 id="trust-heading">The browser drives approved actions. The backend and ledger remain the source of truth.</h2></div>
        <div className="trust-grid">
          <article><h3>Authenticate</h3><p>Role tokens stay visible as session posture.</p></article>
          <article><h3>Escrows</h3><p>Prepare, reconcile, and confirm against XRPL.</p></article>
          <article><h3>Result</h3><p>Winner entry is isolated before payout direction.</p></article>
          <article><h3>Payouts</h3><p>Finish and cancel actions expose ledger evidence.</p></article>
        </div>
      </section>
    </main>
  );
}
