import type { EscrowKind, EscrowPrepareItem, PayoutPrepareItem } from "./api/types";

export function requiredBoutId(value: string): string {
  const normalized = value.trim();
  if (!normalized) {
    throw new Error("Bout ID is required.");
  }
  return normalized;
}

export function findEscrowPrepareItem(items: EscrowPrepareItem[], kind: EscrowKind): EscrowPrepareItem {
  const item = items.find((candidate) => candidate.escrow_kind === kind);
  if (!item) {
    throw new Error(`Escrow prepare item not found for kind=${kind}.`);
  }
  return item;
}

export function findPayoutPrepareItem(items: PayoutPrepareItem[], kind: EscrowKind): PayoutPrepareItem {
  const item = items.find((candidate) => candidate.escrow_kind === kind);
  if (!item) {
    throw new Error(`Payout prepare item not found for kind=${kind}.`);
  }
  return item;
}

export function readRequiredString(record: Record<string, unknown>, field: string): string {
  const value = record[field];
  if (typeof value === "string" && value.trim().length > 0) {
    return value;
  }
  throw new Error(`Missing required string field: ${field}`);
}

export function readOptionalString(record: Record<string, unknown>, field: string): string | null {
  const value = record[field];
  if (value === undefined || value === null) {
    return null;
  }
  if (typeof value === "string") {
    const normalized = value.trim();
    return normalized.length > 0 ? normalized : null;
  }
  throw new Error(`Expected optional string field: ${field}`);
}

export function readRequiredNumber(record: Record<string, unknown>, field: string): number {
  const value = record[field];
  if (typeof value === "number" && Number.isFinite(value)) {
    return value;
  }
  if (typeof value === "string") {
    return parseRequiredInteger(value, field);
  }
  throw new Error(`Missing required numeric field: ${field}`);
}

export function readOptionalNumber(record: Record<string, unknown>, field: string): number | null {
  const value = record[field];
  if (value === undefined || value === null) {
    return null;
  }
  if (typeof value === "number" && Number.isFinite(value)) {
    return value;
  }
  if (typeof value === "string") {
    return parseRequiredInteger(value, field);
  }
  throw new Error(`Expected optional numeric field: ${field}`);
}

export function readRequiredPayoutType(record: Record<string, unknown>, field: string): "EscrowFinish" | "EscrowCancel" {
  const value = readRequiredString(record, field);
  if (value === "EscrowFinish" || value === "EscrowCancel") {
    return value;
  }
  throw new Error(`Unexpected payout transaction type: ${value}`);
}

export function parseRequiredInteger(rawValue: string, field: string): number {
  const normalized = rawValue.trim();
  if (!/^-?\d+$/.test(normalized)) {
    throw new Error(`Invalid integer value for ${field}.`);
  }
  const parsed = Number.parseInt(normalized, 10);
  if (!Number.isFinite(parsed)) {
    throw new Error(`Invalid integer value for ${field}.`);
  }
  return parsed;
}

