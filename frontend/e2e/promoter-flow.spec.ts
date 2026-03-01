import { expect, test } from "@playwright/test";

const BOUT_ID = "4c2f8a58-1963-473a-8f90-2239950f0058";

function jwtForRole(role: string): string {
  const payload = Buffer.from(JSON.stringify({ role })).toString("base64url");
  return `header.${payload}.signature`;
}

test("promoter and admin browser journey covers escrow and payout contracts", async ({ page }) => {
  const seenPaths = new Set<string>();

  await page.route("**/*", async (route) => {
    const request = route.request();
    if (request.url().includes("127.0.0.1:4173")) {
      await route.continue();
      return;
    }

    const url = new URL(request.url());
    const path = url.pathname;
    seenPaths.add(path);

    if (path === "/auth/login") {
      const body = request.postDataJSON() as { email?: string };
      const role = typeof body.email === "string" && body.email.includes("admin") ? "admin" : "promoter";
      await route.fulfill({
        status: 200,
        contentType: "application/json",
        body: JSON.stringify({ access_token: jwtForRole(role), token_type: "bearer" }),
      });
      return;
    }

    if (path === `/bouts/${BOUT_ID}/escrows/prepare`) {
      const body = {
        bout_id: BOUT_ID,
        escrows: [
          escrowPrepareItem("show_a", "1", null, null),
          escrowPrepareItem("show_b", "2", null, null),
          escrowPrepareItem("bonus_a", "3", 823604800, "ABCDEF"),
          escrowPrepareItem("bonus_b", "4", 823604800, "FEDCBA"),
        ],
      };
      await route.fulfill({ status: 200, contentType: "application/json", body: JSON.stringify(body) });
      return;
    }

    if (path === `/bouts/${BOUT_ID}/escrows/signing/reconcile`) {
      await route.fulfill({
        status: 200,
        contentType: "application/json",
        body: JSON.stringify({
          bout_id: BOUT_ID,
          escrow_id: "escrow-show-a",
          escrow_kind: "show_a",
          escrow_status: "planned",
          payload_id: "payload-show-a",
          signing_status: "open",
          tx_hash: null,
          failure_code: null,
        }),
      });
      return;
    }

    if (path === `/bouts/${BOUT_ID}/escrows/confirm`) {
      await route.fulfill({
        status: 200,
        contentType: "application/json",
        body: JSON.stringify({
          bout_id: BOUT_ID,
          escrow_id: "escrow-show-a",
          escrow_kind: "show_a",
          escrow_status: "created",
          bout_status: "draft",
          tx_hash: "TXESCROWFRONTEND001",
          offer_sequence: 1001,
        }),
      });
      return;
    }

    if (path === `/bouts/${BOUT_ID}/result`) {
      await route.fulfill({
        status: 200,
        contentType: "application/json",
        body: JSON.stringify({
          bout_id: BOUT_ID,
          bout_status: "result_entered",
          winner: "A",
        }),
      });
      return;
    }

    if (path === `/bouts/${BOUT_ID}/payouts/prepare`) {
      await route.fulfill({
        status: 200,
        contentType: "application/json",
        body: JSON.stringify({
          bout_id: BOUT_ID,
          bout_status: "result_entered",
          escrows: [
            payoutPrepareItem("show_a", "finish", "EscrowFinish", 7001),
            payoutPrepareItem("show_b", "finish", "EscrowFinish", 7002),
            payoutPrepareItem("bonus_a", "finish", "EscrowFinish", 7003),
            payoutPrepareItem("bonus_b", "cancel", "EscrowCancel", 7004),
          ],
        }),
      });
      return;
    }

    if (path === `/bouts/${BOUT_ID}/payouts/signing/reconcile`) {
      await route.fulfill({
        status: 200,
        contentType: "application/json",
        body: JSON.stringify({
          bout_id: BOUT_ID,
          escrow_id: "escrow-show-a",
          escrow_kind: "show_a",
          escrow_status: "created",
          payload_id: "payload-payout-show-a",
          signing_status: "signed",
          tx_hash: "TXSIGNEDE2E",
          failure_code: null,
        }),
      });
      return;
    }

    if (path === `/bouts/${BOUT_ID}/payouts/confirm`) {
      await route.fulfill({
        status: 200,
        contentType: "application/json",
        body: JSON.stringify({
          bout_id: BOUT_ID,
          escrow_id: "escrow-bonus-a",
          escrow_kind: "bonus_a",
          escrow_status: "finished",
          bout_status: "closed",
          tx_hash: "TXPAYOUTFRONTEND001",
        }),
      });
      return;
    }

    await route.fulfill({
      status: 404,
      contentType: "application/json",
      body: JSON.stringify({ detail: `Unhandled route in test: ${path}` }),
    });
  });

  await page.goto("/");
  await page.getByLabel("Bout ID").fill(BOUT_ID);

  await page.getByTestId("login-submit").click();
  await expect(page.getByText(/token stored for role=promoter/)).toBeVisible();

  await page.getByTestId("escrow-prepare-submit").click();
  await expect(page.getByText(/escrow_prepare: success/)).toBeVisible();

  await page.getByTestId("escrow-reconcile-submit").click();
  await expect(page.getByText(/escrow_signing_reconcile: success/)).toBeVisible();

  await page.getByTestId("escrow-confirm-submit").click();
  await expect(page.getByText(/escrow_confirm: success/)).toBeVisible();

  await page.locator('input[name="login_email"]').fill("admin.frontend@example.com");
  await page.locator('input[name="login_password"]').fill("AdminPass123!");
  await page.getByTestId("login-submit").click();
  await expect(page.getByText(/token stored for role=admin/)).toBeVisible();

  await page.getByTestId("result-submit").click();
  await expect(page.getByText(/result_entry: success/)).toBeVisible();

  await page.getByTestId("payout-prepare-submit").click();
  await expect(page.getByText(/payout_prepare: success/)).toBeVisible();

  await page.getByTestId("payout-reconcile-submit").click();
  await expect(page.getByText(/payout_signing_reconcile: success/)).toBeVisible();

  await page.getByTestId("payout-confirm-submit").click();
  await expect(page.getByText(/payout_confirm: success/)).toBeVisible();

  expect(seenPaths.has("/auth/login")).toBe(true);
  expect(seenPaths.has(`/bouts/${BOUT_ID}/escrows/prepare`)).toBe(true);
  expect(seenPaths.has(`/bouts/${BOUT_ID}/escrows/signing/reconcile`)).toBe(true);
  expect(seenPaths.has(`/bouts/${BOUT_ID}/escrows/confirm`)).toBe(true);
  expect(seenPaths.has(`/bouts/${BOUT_ID}/result`)).toBe(true);
  expect(seenPaths.has(`/bouts/${BOUT_ID}/payouts/prepare`)).toBe(true);
  expect(seenPaths.has(`/bouts/${BOUT_ID}/payouts/signing/reconcile`)).toBe(true);
  expect(seenPaths.has(`/bouts/${BOUT_ID}/payouts/confirm`)).toBe(true);
});

function escrowPrepareItem(kind: string, suffix: string, cancelAfter: number | null, conditionHex: string | null) {
  const unsignedTx: Record<string, unknown> = {
    TransactionType: "EscrowCreate",
    Account: "rPromoterFront",
    Destination: `rFighter${suffix}`,
    Amount: "1000",
    FinishAfter: 823000000,
  };
  if (cancelAfter !== null) {
    unsignedTx.CancelAfter = cancelAfter;
  }
  if (conditionHex !== null) {
    unsignedTx.Condition = conditionHex;
  }

  return {
    escrow_id: `escrow-${kind}`,
    escrow_kind: kind,
    unsigned_tx: unsignedTx,
    xaman_sign_request: {
      payload_id: `payload-${kind}`,
      deep_link_url: `xumm://payload/payload-${kind}`,
      qr_png_url: `https://xumm.app/sign/payload-${kind}/qr.png`,
      websocket_status_url: `wss://xumm.app/sign/payload-${kind}`,
      mode: "stub",
    },
  };
}

function payoutPrepareItem(kind: string, action: "finish" | "cancel", transactionType: string, offerSequence: number) {
  const unsignedTx: Record<string, unknown> = {
    TransactionType: transactionType,
    Account: "rPromoterFront",
    Owner: "rPromoterFront",
    OfferSequence: offerSequence,
  };
  if (kind === "bonus_a") {
    unsignedTx.Fulfillment = "FULFILLMENTA";
  }

  return {
    escrow_id: `escrow-${kind}`,
    escrow_kind: kind,
    action,
    unsigned_tx: unsignedTx,
    xaman_sign_request: {
      payload_id: `payload-payout-${kind}`,
      deep_link_url: `xumm://payload/payload-payout-${kind}`,
      qr_png_url: `https://xumm.app/sign/payload-payout-${kind}/qr.png`,
      websocket_status_url: `wss://xumm.app/sign/payload-payout-${kind}`,
      mode: "stub",
    },
  };
}
