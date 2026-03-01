export type UserRole = "promoter" | "fighter" | "management" | "admin";

export type EscrowKind = "show_a" | "show_b" | "bonus_a" | "bonus_b";

export type EscrowStatus = "planned" | "created" | "finished" | "cancelled" | "failed";

export type BoutStatus =
  | "draft"
  | "ready_for_escrow"
  | "escrows_created"
  | "result_entered"
  | "payouts_in_progress"
  | "closed";

export type BoutWinner = "A" | "B";

export interface RegisterRequest {
  email: string;
  password: string;
  role: UserRole;
}

export interface RegisterResponse {
  user_id: string;
  email: string;
  role: UserRole;
}

export interface LoginRequest {
  email: string;
  password: string;
}

export interface TokenResponse {
  access_token: string;
  token_type: "bearer";
}

export interface ApiError {
  detail: string;
}

export interface XamanSignRequest {
  payload_id: string;
  deep_link_url: string;
  qr_png_url: string;
  websocket_status_url: string | null;
  mode: "stub" | "api";
}

export interface EscrowPrepareItem {
  escrow_id: string;
  escrow_kind: EscrowKind;
  unsigned_tx: Record<string, unknown>;
  xaman_sign_request: XamanSignRequest;
}

export interface EscrowPrepareResponse {
  bout_id: string;
  escrows: EscrowPrepareItem[];
}

export interface EscrowConfirmRequest {
  escrow_kind: EscrowKind;
  tx_hash: string;
  offer_sequence: number;
  validated: boolean;
  engine_result: string;
  owner_address: string;
  destination_address: string;
  amount_drops: number;
  finish_after_ripple: number;
  cancel_after_ripple: number | null;
  condition_hex: string | null;
}

export interface EscrowConfirmResponse {
  bout_id: string;
  escrow_id: string;
  escrow_kind: EscrowKind;
  escrow_status: EscrowStatus;
  bout_status: BoutStatus;
  tx_hash: string;
  offer_sequence: number;
}

export interface SigningReconcileRequest {
  escrow_kind: EscrowKind;
  payload_id: string;
  observed_status?: "open" | "signed" | "declined" | "expired" | "unknown";
  observed_tx_hash?: string;
}

export interface SigningReconcileResponse {
  bout_id: string;
  escrow_id: string;
  escrow_kind: EscrowKind;
  escrow_status: EscrowStatus;
  payload_id: string;
  signing_status: "open" | "signed" | "declined" | "expired" | "unknown";
  tx_hash: string | null;
  failure_code: string | null;
}

export interface BoutResultRequest {
  winner: BoutWinner;
}

export interface BoutResultResponse {
  bout_id: string;
  bout_status: BoutStatus;
  winner: BoutWinner;
}

export interface PayoutPrepareItem {
  escrow_id: string;
  escrow_kind: EscrowKind;
  action: "finish" | "cancel";
  unsigned_tx: Record<string, unknown>;
  xaman_sign_request: XamanSignRequest;
}

export interface PayoutPrepareResponse {
  bout_id: string;
  bout_status: BoutStatus;
  escrows: PayoutPrepareItem[];
}

export interface PayoutConfirmRequest {
  escrow_kind: EscrowKind;
  tx_hash: string;
  validated: boolean;
  engine_result: string;
  transaction_type: "EscrowFinish" | "EscrowCancel";
  owner_address: string;
  offer_sequence: number;
  close_time_ripple: number;
  fulfillment_hex: string | null;
}

export interface PayoutConfirmResponse {
  bout_id: string;
  escrow_id: string;
  escrow_kind: EscrowKind;
  escrow_status: EscrowStatus;
  bout_status: BoutStatus;
  tx_hash: string;
}
