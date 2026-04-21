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

    expect(screen.getByRole("heading", { name: /XRPL escrow settlement for fight-night operations/i })).toBeInTheDocument();

    fireEvent.click(screen.getByRole("link", { name: /Enter operator workspace/i }));

    await waitFor(() => {
      expect(screen.getByRole("heading", { name: /Guided settlement workflow for promoter and admin execution/i })).toBeInTheDocument();
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

    window.history.pushState({}, "", "/app");
    render(<App />);
    fireEvent.click(screen.getByTestId("login-submit"));

    await waitFor(() => {
      expect(screen.getByText("[401] Invalid credentials.")).toBeInTheDocument();
    });
  });
});
