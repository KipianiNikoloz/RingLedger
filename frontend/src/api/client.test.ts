import { beforeEach, describe, expect, it, vi } from "vitest";

import { confirmEscrowCreate, createBout, listBouts, loginUser, prepareEscrows, registerUser, upsertFighterProfile } from "./client";

const fetchMock = vi.fn<typeof fetch>();

beforeEach(() => {
  fetchMock.mockReset();
  vi.stubGlobal("fetch", fetchMock);
});

describe("api/client", () => {
  it("sends register request to auth endpoint", async () => {
    fetchMock.mockResolvedValueOnce(
      new Response(
        JSON.stringify({
          user_id: "6e688226-15ee-4c47-b0cd-8f1188ca7155",
          email: "promoter.frontend@example.com",
          role: "fighter",
        }),
        { status: 201, headers: { "Content-Type": "application/json" } },
      ),
    );

    const result = await registerUser({
      email: "promoter.frontend@example.com",
      password: "PromoterPass123!",
    });

    expect(result.role).toBe("fighter");
    expect(fetchMock).toHaveBeenCalledTimes(1);
    const [url, init] = fetchMock.mock.calls[0];
    expect(init).toBeDefined();
    expect(url).toContain("/auth/register");
    expect(init?.method).toBe("POST");
  });

  it("attaches auth and idempotency headers for escrow confirm", async () => {
    fetchMock.mockResolvedValueOnce(
      new Response(
        JSON.stringify({
          bout_id: "bout-1",
          escrow_id: "escrow-1",
          escrow_kind: "show_a",
          escrow_status: "created",
          bout_status: "draft",
          tx_hash: "TX1",
          offer_sequence: 1001,
        }),
        { status: 200, headers: { "Content-Type": "application/json" } },
      ),
    );

    await confirmEscrowCreate("bout-1", "jwt-token", "idem-1", {
      escrow_kind: "show_a",
      tx_hash: "TX1",
    });

    const [, init] = fetchMock.mock.calls[0];
    expect(init).toBeDefined();
    const headers = new Headers(init?.headers);
    expect(headers.get("Authorization")).toBe("Bearer jwt-token");
    expect(headers.get("Idempotency-Key")).toBe("idem-1");
  });

  it("surfaces API error details deterministically", async () => {
    fetchMock.mockResolvedValueOnce(
      new Response(JSON.stringify({ detail: "Invalid credentials." }), {
        status: 401,
        headers: { "Content-Type": "application/json" },
      }),
    );

    await expect(loginUser({ email: "bad@example.com", password: "wrong" })).rejects.toMatchObject({
      name: "ApiRequestError",
      status: 401,
      message: "Invalid credentials.",
    });
  });

  it("calls protected prepare endpoint with bearer token", async () => {
    fetchMock.mockResolvedValueOnce(
      new Response(JSON.stringify({ bout_id: "bout-1", escrows: [] }), {
        status: 200,
        headers: { "Content-Type": "application/json" },
      }),
    );

    await prepareEscrows("bout-1", "jwt-promoter");

    const [url, init] = fetchMock.mock.calls[0];
    expect(url).toContain("/bouts/bout-1/escrows/prepare");
    expect(init).toBeDefined();
    const headers = new Headers(init?.headers);
    expect(headers.get("Authorization")).toBe("Bearer jwt-promoter");
  });

  it("calls fighter profile upsert with PUT and bearer token", async () => {
    fetchMock.mockResolvedValueOnce(
      new Response(
        JSON.stringify({
          profile_id: "profile-1",
          user_id: "fighter-1",
          display_name: "Fighter Alpha",
          xrpl_address: "rAAAAAAAAAAAAAAAAAAAAAAAA",
        }),
        { status: 200, headers: { "Content-Type": "application/json" } },
      ),
    );

    await upsertFighterProfile("jwt-fighter", {
      display_name: "Fighter Alpha",
      xrpl_address: "rAAAAAAAAAAAAAAAAAAAAAAAA",
    });

    const [url, init] = fetchMock.mock.calls[0];
    expect(url).toContain("/fighters/me");
    expect(init?.method).toBe("PUT");
    const headers = new Headers(init?.headers);
    expect(headers.get("Authorization")).toBe("Bearer jwt-fighter");
  });

  it("creates and lists bouts through management endpoints", async () => {
    fetchMock
      .mockResolvedValueOnce(
        new Response(JSON.stringify(boutSummary("bout-1")), {
          status: 201,
          headers: { "Content-Type": "application/json" },
        }),
      )
      .mockResolvedValueOnce(
        new Response(JSON.stringify({ bouts: [boutSummary("bout-1")] }), {
          status: 200,
          headers: { "Content-Type": "application/json" },
        }),
      );

    await createBout("jwt-promoter", {
      fighter_a_user_id: "fighter-a",
      fighter_b_user_id: "fighter-b",
      event_datetime_utc: "2026-02-18T20:00:00Z",
      promoter_owner_address: "rCCCCCCCCCCCCCCCCCCCCCCCC",
      show_a_drops: 2000000,
      show_b_drops: 2500000,
      bonus_a_drops: 500000,
      bonus_b_drops: 750000,
    });
    await listBouts("jwt-promoter");

    expect(fetchMock).toHaveBeenCalledTimes(2);
    expect(fetchMock.mock.calls[0][0]).toContain("/bouts");
    expect(fetchMock.mock.calls[0][1]?.method).toBe("POST");
    expect(fetchMock.mock.calls[1][0]).toContain("/bouts");
    expect(fetchMock.mock.calls[1][1]?.method).toBe("GET");
  });
});

function boutSummary(boutId: string) {
  return {
    bout_id: boutId,
    promoter_user_id: "promoter-1",
    fighter_a_user_id: "fighter-a",
    fighter_b_user_id: "fighter-b",
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
