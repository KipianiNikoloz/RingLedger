import { expect, test, type Page } from "@playwright/test";

const BOUT_ID = "4c2f8a58-1963-473a-8f90-2239950f0058";
const FIGHTER_A_ID = "11111111-1111-4111-8111-111111111111";
const FIGHTER_B_ID = "22222222-2222-4222-8222-222222222222";

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
      const role =
        typeof body.email === "string" && body.email.includes("admin")
          ? "admin"
          : typeof body.email === "string" && body.email.includes("fighter")
            ? "fighter"
            : "promoter";
      await route.fulfill({
        status: 200,
        contentType: "application/json",
        body: JSON.stringify({ access_token: jwtForRole(role), token_type: "bearer" }),
      });
      return;
    }

    if (path === "/fighters/me") {
      await route.fulfill({
        status: 200,
        contentType: "application/json",
        body: JSON.stringify({
          profile_id: "profile-fighter-a",
          user_id: FIGHTER_A_ID,
          display_name: "Fighter Alpha",
          xrpl_address: "rAAAAAAAAAAAAAAAAAAAAAAAA",
        }),
      });
      return;
    }

    if (path === "/bouts" && request.method() === "POST") {
      await route.fulfill({
        status: 201,
        contentType: "application/json",
        body: JSON.stringify(boutSummary(BOUT_ID)),
      });
      return;
    }

    if (path === "/bouts" && request.method() === "GET") {
      await route.fulfill({
        status: 200,
        contentType: "application/json",
        body: JSON.stringify({ bouts: [boutSummary(BOUT_ID)] }),
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
  await expect(page.getByRole("heading", { name: /Backend-authoritative escrow settlement console/i })).toBeVisible();
  await page.getByRole("link", { name: /Enter operator workspace/i }).click();
  await expect(page.getByRole("heading", { name: /Settlement control room/i })).toBeVisible();

  await page.locator('input[name="login_email"]').fill("fighter.frontend@example.com");
  await page.getByTestId("login-submit").click();
  await expectActionLog(page, /token stored for role=fighter/);

  await page.getByTestId("fighter-profile-submit").click();
  await expectActionLog(page, /fighter_profile_upsert: success/);

  await page.locator('input[name="login_email"]').fill("promoter.frontend@example.com");
  await page.locator('input[name="login_password"]').fill("PromoterPass123!");
  await page.getByTestId("login-submit").click();
  await expectActionLog(page, /token stored for role=promoter/);

  await page.locator('input[name="fighter_a_user_id"]').fill(FIGHTER_A_ID);
  await page.locator('input[name="fighter_b_user_id"]').fill(FIGHTER_B_ID);
  await page.getByTestId("bout-create-submit").click();
  await expectActionLog(page, /bout_create: success/);
  await expect(page.getByLabel("Bout ID")).toHaveValue(BOUT_ID);

  await page.getByTestId("escrow-prepare-submit").click();
  await expectActionLog(page, /escrow_prepare: success/);

  await page.getByTestId("escrow-reconcile-submit").click();
  await expectActionLog(page, /escrow_signing_reconcile: success/);

  await page.getByTestId("escrow-confirm-submit").click();
  await expectActionLog(page, /escrow_confirm: success/);

  await page.locator('input[name="login_email"]').fill("admin.frontend@example.com");
  await page.locator('input[name="login_password"]').fill("AdminPass123!");
  await page.getByTestId("login-submit").click();
  await expectActionLog(page, /token stored for role=admin/);

  await page.getByTestId("result-submit").click();
  await expectActionLog(page, /result_entry: success/);

  await page.getByTestId("payout-prepare-submit").click();
  await expectActionLog(page, /payout_prepare: success/);

  await page.getByTestId("payout-reconcile-submit").click();
  await expectActionLog(page, /payout_signing_reconcile: success/);

  await page.getByTestId("payout-confirm-submit").click();
  await expectActionLog(page, /payout_confirm: success/);

  expect(seenPaths.has("/auth/login")).toBe(true);
  expect(seenPaths.has("/fighters/me")).toBe(true);
  expect(seenPaths.has("/bouts")).toBe(true);
  expect(seenPaths.has(`/bouts/${BOUT_ID}/escrows/prepare`)).toBe(true);
  expect(seenPaths.has(`/bouts/${BOUT_ID}/escrows/signing/reconcile`)).toBe(true);
  expect(seenPaths.has(`/bouts/${BOUT_ID}/escrows/confirm`)).toBe(true);
  expect(seenPaths.has(`/bouts/${BOUT_ID}/result`)).toBe(true);
  expect(seenPaths.has(`/bouts/${BOUT_ID}/payouts/prepare`)).toBe(true);
  expect(seenPaths.has(`/bouts/${BOUT_ID}/payouts/signing/reconcile`)).toBe(true);
  expect(seenPaths.has(`/bouts/${BOUT_ID}/payouts/confirm`)).toBe(true);
});

async function expectActionLog(page: Page, text: RegExp) {
  await expect(page.getByRole("listitem").filter({ hasText: text }).first()).toBeVisible();
}

function boutSummary(boutId: string) {
  return {
    bout_id: boutId,
    promoter_user_id: "promoter-1",
    fighter_a_user_id: FIGHTER_A_ID,
    fighter_b_user_id: FIGHTER_B_ID,
    event_datetime_utc: "2026-02-18T20:00:00Z",
    finish_after_utc: "2026-02-18T22:00:00Z",
    cancel_after_utc: "2026-02-25T20:00:00Z",
    show_a_drops: 2000000,
    show_b_drops: 2500000,
    bonus_a_drops: 500000,
    bonus_b_drops: 750000,
    bout_status: "draft",
    winner: null,
    escrows: [],
  };
}

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
