import type {
  BoutResultRequest,
  BoutResultResponse,
  EscrowConfirmRequest,
  EscrowConfirmResponse,
  EscrowPrepareResponse,
  LoginRequest,
  PayoutConfirmRequest,
  PayoutConfirmResponse,
  PayoutPrepareResponse,
  RegisterRequest,
  RegisterResponse,
  SigningReconcileRequest,
  SigningReconcileResponse,
  TokenResponse,
} from "./types";

const API_BASE_URL: string = import.meta.env.VITE_API_BASE_URL ?? "http://127.0.0.1:8000";

export class ApiRequestError extends Error {
  public readonly status: number;

  public constructor(message: string, status: number) {
    super(message);
    this.name = "ApiRequestError";
    this.status = status;
  }
}

interface RequestOptions {
  method?: "GET" | "POST";
  token?: string;
  body?: unknown;
  idempotencyKey?: string;
}

async function requestJson<T>(path: string, options: RequestOptions = {}): Promise<T> {
  const headers = new Headers({
    "Content-Type": "application/json",
  });

  if (options.token) {
    headers.set("Authorization", `Bearer ${options.token}`);
  }
  if (options.idempotencyKey) {
    headers.set("Idempotency-Key", options.idempotencyKey);
  }

  const response = await fetch(`${API_BASE_URL}${path}`, {
    method: options.method ?? "GET",
    headers,
    body: options.body !== undefined ? JSON.stringify(options.body) : undefined,
  });

  if (!response.ok) {
    const detail = await readErrorDetail(response);
    throw new ApiRequestError(detail, response.status);
  }

  return (await response.json()) as T;
}

async function readErrorDetail(response: Response): Promise<string> {
  try {
    const payload = (await response.json()) as { detail?: unknown };
    if (typeof payload.detail === "string") {
      return payload.detail;
    }
  } catch {
    // Fall through to generic error text.
  }
  return `Request failed with status ${response.status}`;
}

export function registerUser(payload: RegisterRequest): Promise<RegisterResponse> {
  return requestJson<RegisterResponse>("/auth/register", {
    method: "POST",
    body: payload,
  });
}

export function loginUser(payload: LoginRequest): Promise<TokenResponse> {
  return requestJson<TokenResponse>("/auth/login", {
    method: "POST",
    body: payload,
  });
}

export function prepareEscrows(boutId: string, token: string): Promise<EscrowPrepareResponse> {
  return requestJson<EscrowPrepareResponse>(`/bouts/${boutId}/escrows/prepare`, {
    method: "POST",
    token,
  });
}

export function reconcileEscrowSigning(
  boutId: string,
  token: string,
  payload: SigningReconcileRequest,
): Promise<SigningReconcileResponse> {
  return requestJson<SigningReconcileResponse>(`/bouts/${boutId}/escrows/signing/reconcile`, {
    method: "POST",
    token,
    body: payload,
  });
}

export function confirmEscrowCreate(
  boutId: string,
  token: string,
  idempotencyKey: string,
  payload: EscrowConfirmRequest,
): Promise<EscrowConfirmResponse> {
  return requestJson<EscrowConfirmResponse>(`/bouts/${boutId}/escrows/confirm`, {
    method: "POST",
    token,
    idempotencyKey,
    body: payload,
  });
}

export function enterResult(
  boutId: string,
  token: string,
  payload: BoutResultRequest,
): Promise<BoutResultResponse> {
  return requestJson<BoutResultResponse>(`/bouts/${boutId}/result`, {
    method: "POST",
    token,
    body: payload,
  });
}

export function preparePayouts(boutId: string, token: string): Promise<PayoutPrepareResponse> {
  return requestJson<PayoutPrepareResponse>(`/bouts/${boutId}/payouts/prepare`, {
    method: "POST",
    token,
  });
}

export function reconcilePayoutSigning(
  boutId: string,
  token: string,
  payload: SigningReconcileRequest,
): Promise<SigningReconcileResponse> {
  return requestJson<SigningReconcileResponse>(`/bouts/${boutId}/payouts/signing/reconcile`, {
    method: "POST",
    token,
    body: payload,
  });
}

export function confirmPayout(
  boutId: string,
  token: string,
  idempotencyKey: string,
  payload: PayoutConfirmRequest,
): Promise<PayoutConfirmResponse> {
  return requestJson<PayoutConfirmResponse>(`/bouts/${boutId}/payouts/confirm`, {
    method: "POST",
    token,
    idempotencyKey,
    body: payload,
  });
}
