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
});

describe("App", () => {
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
      expect(screen.getByText("Escrow Prepare")).toBeInTheDocument();
      const prepareBlock = screen.getByText("Escrow Prepare").closest("section");
      expect(prepareBlock).not.toBeNull();
      expect(prepareBlock).toHaveTextContent("4c2f8a58-1963-473a-8f90-2239950f0058");
    });
  });

  it("shows deterministic API error message", async () => {
    fetchMock.mockResolvedValueOnce(
      new Response(JSON.stringify({ detail: "Invalid credentials." }), {
        status: 401,
        headers: { "Content-Type": "application/json" },
      }),
    );

    render(<App />);
    fireEvent.click(screen.getByTestId("login-submit"));

    await waitFor(() => {
      expect(screen.getByText("[401] Invalid credentials.")).toBeInTheDocument();
    });
  });
});
