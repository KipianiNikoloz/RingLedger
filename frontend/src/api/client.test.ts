import { beforeEach, describe, expect, it, vi } from "vitest";

import { confirmEscrowCreate, loginUser, prepareEscrows, registerUser } from "./client";

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
          role: "promoter",
        }),
        { status: 201, headers: { "Content-Type": "application/json" } },
      ),
    );

    const result = await registerUser({
      email: "promoter.frontend@example.com",
      password: "PromoterPass123!",
      role: "promoter",
    });

    expect(result.role).toBe("promoter");
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
      offer_sequence: 1001,
      validated: true,
      engine_result: "tesSUCCESS",
      owner_address: "rPromoter",
      destination_address: "rFighter",
      amount_drops: 1000,
      finish_after_ripple: 820000000,
      cancel_after_ripple: null,
      condition_hex: null,
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
});
