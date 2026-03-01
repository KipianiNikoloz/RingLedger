import { useState } from "react";

import { confirmPayout, enterResult, preparePayouts, reconcilePayoutSigning } from "../api/client";
import type {
  BoutResultResponse,
  EscrowKind,
  PayoutConfirmResponse,
  PayoutPrepareResponse,
  SigningReconcileResponse,
} from "../api/types";
import { createIdempotencyKey } from "../auth";
import type { SigningStatus } from "../constants";
import {
  findPayoutPrepareItem,
  parseRequiredInteger,
  readOptionalString,
  readRequiredNumber,
  readRequiredPayoutType,
  readRequiredString,
  requiredBoutId,
} from "../flow-utils";

interface ResultPayoutWorkflowOptions {
  promoterToken: string | undefined;
  adminToken: string | undefined;
  boutId: string;
  runAction: (label: string, callback: () => Promise<void>) => Promise<void>;
  setLastError: (message: string | null) => void;
}

export interface ResultPayoutWorkflowModel {
  winner: "A" | "B";
  resultEntry: BoutResultResponse | null;
  payoutPrepareResult: PayoutPrepareResponse | null;
  payoutReconcileKind: EscrowKind;
  payoutReconcileStatus: SigningStatus;
  payoutReconcileTxHash: string;
  payoutReconcileResult: SigningReconcileResponse | null;
  payoutConfirmKind: EscrowKind;
  payoutConfirmTxHash: string;
  payoutConfirmValidated: boolean;
  payoutConfirmEngineResult: string;
  payoutCloseTimeRipple: string;
  payoutConfirmResult: PayoutConfirmResponse | null;
  setWinner: (value: "A" | "B") => void;
  setPayoutReconcileKind: (value: EscrowKind) => void;
  setPayoutReconcileStatus: (value: SigningStatus) => void;
  setPayoutReconcileTxHash: (value: string) => void;
  setPayoutConfirmKind: (value: EscrowKind) => void;
  setPayoutConfirmTxHash: (value: string) => void;
  setPayoutConfirmValidated: (value: boolean) => void;
  setPayoutConfirmEngineResult: (value: string) => void;
  setPayoutCloseTimeRipple: (value: string) => void;
  handleResultEntry: () => Promise<void>;
  handlePayoutPrepare: () => Promise<void>;
  handlePayoutReconcile: () => Promise<void>;
  handlePayoutConfirm: () => Promise<void>;
}

export function useResultPayoutWorkflow({
  promoterToken,
  adminToken,
  boutId,
  runAction,
  setLastError,
}: ResultPayoutWorkflowOptions): ResultPayoutWorkflowModel {
  const [winner, setWinner] = useState<"A" | "B">("A");
  const [resultEntry, setResultEntry] = useState<BoutResultResponse | null>(null);

  const [payoutPrepareResult, setPayoutPrepareResult] = useState<PayoutPrepareResponse | null>(null);
  const [payoutReconcileKind, setPayoutReconcileKind] = useState<EscrowKind>("show_a");
  const [payoutReconcileStatus, setPayoutReconcileStatus] = useState<SigningStatus>("open");
  const [payoutReconcileTxHash, setPayoutReconcileTxHash] = useState("");
  const [payoutReconcileResult, setPayoutReconcileResult] = useState<SigningReconcileResponse | null>(null);

  const [payoutConfirmKind, setPayoutConfirmKind] = useState<EscrowKind>("show_a");
  const [payoutConfirmTxHash, setPayoutConfirmTxHash] = useState("TXPAYOUTFRONTEND001");
  const [payoutConfirmValidated, setPayoutConfirmValidated] = useState(true);
  const [payoutConfirmEngineResult, setPayoutConfirmEngineResult] = useState("tesSUCCESS");
  const [payoutCloseTimeRipple, setPayoutCloseTimeRipple] = useState("823000100");
  const [payoutConfirmResult, setPayoutConfirmResult] = useState<PayoutConfirmResponse | null>(null);

  async function handleResultEntry(): Promise<void> {
    if (!adminToken) {
      setLastError("Admin token is required. Log in as admin first.");
      return;
    }
    await runAction("result_entry", async () => {
      const response = await enterResult(requiredBoutId(boutId), adminToken, { winner });
      setResultEntry(response);
    });
  }

  async function handlePayoutPrepare(): Promise<void> {
    if (!promoterToken) {
      setLastError("Promoter token is required. Log in as promoter first.");
      return;
    }
    await runAction("payout_prepare", async () => {
      const response = await preparePayouts(requiredBoutId(boutId), promoterToken);
      setPayoutPrepareResult(response);
    });
  }

  async function handlePayoutReconcile(): Promise<void> {
    if (!promoterToken) {
      setLastError("Promoter token is required. Log in as promoter first.");
      return;
    }
    if (!payoutPrepareResult) {
      setLastError("Run payout prepare first.");
      return;
    }

    await runAction("payout_signing_reconcile", async () => {
      const selected = findPayoutPrepareItem(payoutPrepareResult.escrows, payoutReconcileKind);
      const response = await reconcilePayoutSigning(requiredBoutId(boutId), promoterToken, {
        escrow_kind: payoutReconcileKind,
        payload_id: selected.xaman_sign_request.payload_id,
        observed_status: payoutReconcileStatus,
        observed_tx_hash: payoutReconcileTxHash || undefined,
      });
      setPayoutReconcileResult(response);
    });
  }

  async function handlePayoutConfirm(): Promise<void> {
    if (!promoterToken) {
      setLastError("Promoter token is required. Log in as promoter first.");
      return;
    }
    if (!payoutPrepareResult) {
      setLastError("Run payout prepare first.");
      return;
    }

    await runAction("payout_confirm", async () => {
      const selected = findPayoutPrepareItem(payoutPrepareResult.escrows, payoutConfirmKind);
      const tx = selected.unsigned_tx;
      const response = await confirmPayout(requiredBoutId(boutId), promoterToken, createIdempotencyKey("payout-confirm"), {
        escrow_kind: payoutConfirmKind,
        tx_hash: payoutConfirmTxHash,
        validated: payoutConfirmValidated,
        engine_result: payoutConfirmEngineResult,
        transaction_type: readRequiredPayoutType(tx, "TransactionType"),
        owner_address: readRequiredString(tx, "Account"),
        offer_sequence: readRequiredNumber(tx, "OfferSequence"),
        close_time_ripple: parseRequiredInteger(payoutCloseTimeRipple, "close_time_ripple"),
        fulfillment_hex: readOptionalString(tx, "Fulfillment"),
      });
      setPayoutConfirmResult(response);
    });
  }

  return {
    winner,
    resultEntry,
    payoutPrepareResult,
    payoutReconcileKind,
    payoutReconcileStatus,
    payoutReconcileTxHash,
    payoutReconcileResult,
    payoutConfirmKind,
    payoutConfirmTxHash,
    payoutConfirmValidated,
    payoutConfirmEngineResult,
    payoutCloseTimeRipple,
    payoutConfirmResult,
    setWinner,
    setPayoutReconcileKind,
    setPayoutReconcileStatus,
    setPayoutReconcileTxHash,
    setPayoutConfirmKind,
    setPayoutConfirmTxHash,
    setPayoutConfirmValidated,
    setPayoutConfirmEngineResult,
    setPayoutCloseTimeRipple,
    handleResultEntry,
    handlePayoutPrepare,
    handlePayoutReconcile,
    handlePayoutConfirm,
  };
}

