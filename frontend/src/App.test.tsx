import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import { beforeEach, describe, expect, it, vi } from "vitest";

import App from "./App";

const fetchMock = vi.fn<typeof fetch>();

function buildJwtWithRole(role: string): string {
  const payload = JSON.stringify({ role });
  const base64 = btoa(payload).replace(/\+/g, "-").replace(/\//g, "_").replace(/=+$/g, "");
  return `header.${base64}.signature`;
}

beforeEach(() => {
  fetchMock.mockReset();
  vi.stubGlobal("fetch", fetchMock);
  window.history.pushState({}, "", "/");
});

describe("App", () => {
  it("renders homepage and navigates to operator workspace", async () => {
    render(<App />);

    expect(screen.getByRole("heading", { name: /Backend-authoritative escrow settlement console/i })).toBeInTheDocument();

    fireEvent.click(screen.getByRole("link", { name: /Enter operator workspace/i }));

    await waitFor(() => {
      expect(screen.getByRole("heading", { name: /Settlement control room/i })).toBeInTheDocument();
      expect(screen.getByLabelText("Bout ID")).toBeInTheDocument();
    });
  });

  it("logs in promoter and prepares escrow payloads", async () => {
    fetchMock
      .mockResolvedValueOnce(
        new Response(
          JSON.stringify({
            access_token: buildJwtWithRole("promoter"),
            token_type: "bearer",
          }),
          { status: 200, headers: { "Content-Type": "application/json" } },
        ),
      )
      .mockResolvedValueOnce(
        new Response(
          JSON.stringify({
            bout_id: "4c2f8a58-1963-473a-8f90-2239950f0058",
            escrows: [],
          }),
          { status: 200, headers: { "Content-Type": "application/json" } },
        ),
      );

    window.history.pushState({}, "", "/app");
    render(<App />);

    fireEvent.change(screen.getByLabelText("Bout ID"), {
      target: { value: "4c2f8a58-1963-473a-8f90-2239950f0058" },
    });
    fireEvent.click(screen.getByTestId("login-submit"));

    await waitFor(() => {
      expect(fetchMock).toHaveBeenCalledTimes(1);
    });

    fireEvent.click(screen.getByTestId("escrow-prepare-submit"));

    await waitFor(() => {
      expect(fetchMock).toHaveBeenCalledTimes(2);
      const prepareHeading = screen.getByRole("heading", { name: "Escrow Prepare" });
      expect(prepareHeading).toBeInTheDocument();
      const prepareBlock = prepareHeading.closest("section");
      expect(prepareBlock).not.toBeNull();
      expect(prepareBlock).toHaveTextContent("4c2f8a58-1963-473a-8f90-2239950f0058");
    });
  });

  it("sets up fighter profile and creates an active bout", async () => {
    fetchMock
      .mockResolvedValueOnce(
        new Response(JSON.stringify({ access_token: buildJwtWithRole("fighter"), token_type: "bearer" }), {
          status: 200,
          headers: { "Content-Type": "application/json" },
        }),
      )
      .mockResolvedValueOnce(
        new Response(
          JSON.stringify({
            profile_id: "profile-1",
            user_id: "fighter-a",
            display_name: "Fighter Alpha",
            xrpl_address: "rAAAAAAAAAAAAAAAAAAAAAAAA",
          }),
          { status: 200, headers: { "Content-Type": "application/json" } },
        ),
      )
      .mockResolvedValueOnce(
        new Response(JSON.stringify({ access_token: buildJwtWithRole("promoter"), token_type: "bearer" }), {
          status: 200,
          headers: { "Content-Type": "application/json" },
        }),
      )
      .mockResolvedValueOnce(
        new Response(JSON.stringify(boutSummary("11111111-1111-4111-8111-111111111111")), {
          status: 201,
          headers: { "Content-Type": "application/json" },
        }),
      );

    window.history.pushState({}, "", "/app");
    render(<App />);

    fireEvent.click(screen.getByTestId("login-submit"));
    await waitFor(() => {
      expect(fetchMock).toHaveBeenCalledTimes(1);
    });

    fireEvent.click(screen.getByTestId("fighter-profile-submit"));
    await waitFor(() => {
      expect(fetchMock).toHaveBeenCalledTimes(2);
      expect(screen.getByRole("heading", { name: "Fighter Profile" })).toBeInTheDocument();
    });

    fireEvent.click(screen.getByTestId("login-submit"));
    await waitFor(() => {
      expect(fetchMock).toHaveBeenCalledTimes(3);
    });

    fireEvent.change(screen.getByLabelText("Fighter A user ID"), { target: { value: "fighter-a" } });
    fireEvent.change(screen.getByLabelText("Fighter B user ID"), { target: { value: "fighter-b" } });
    fireEvent.click(screen.getByTestId("bout-create-submit"));

    await waitFor(() => {
      expect(fetchMock).toHaveBeenCalledTimes(4);
      expect(screen.getByLabelText("Bout ID")).toHaveValue("11111111-1111-4111-8111-111111111111");
      expect(screen.getByRole("heading", { name: "Bout Create" })).toBeInTheDocument();
    });
  });

  it("shows deterministic API error message", async () => {
    fetchMock.mockResolvedValueOnce(
      new Response(JSON.stringify({ detail: "Invalid credentials." }), {
        status: 401,
        headers: { "Content-Type": "application/json" },
      }),
    );

    window.history.pushState({}, "", "/app");
    render(<App />);
    fireEvent.click(screen.getByTestId("login-submit"));

    await waitFor(() => {
      expect(screen.getAllByText("[401] Invalid credentials.").length).toBeGreaterThan(0);
    });
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
