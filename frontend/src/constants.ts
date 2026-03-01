import type { EscrowKind } from "./api/types";

export const ESCROW_KINDS: EscrowKind[] = ["show_a", "show_b", "bonus_a", "bonus_b"];

export const SIGNING_STATUSES = ["open", "signed", "declined", "expired", "unknown"] as const;

export type SigningStatus = (typeof SIGNING_STATUSES)[number];

