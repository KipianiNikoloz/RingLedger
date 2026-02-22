import { useState } from "react";

import { confirmEscrowCreate, prepareEscrows, reconcileEscrowSigning } from "../api/client";
import type { EscrowConfirmResponse, EscrowKind, EscrowPrepareResponse, SigningReconcileResponse } from "../api/types";
import { createIdempotencyKey } from "../auth";
import type { SigningStatus } from "../constants";
import {
  findEscrowPrepareItem,
  parseRequiredInteger,
  readOptionalNumber,
  readOptionalString,
  readRequiredNumber,
  readRequiredString,
  requiredBoutId,
} from "../flow-utils";

interface EscrowWorkflowOptions {
  promoterToken: string | undefined;
  boutId: string;
  runAction: (label: string, callback: () => Promise<void>) => Promise<void>;
  setLastError: (message: string | null) => void;
}

export interface EscrowWorkflowModel {
  escrowPrepareResult: EscrowPrepareResponse | null;
  escrowReconcileKind: EscrowKind;
  escrowReconcileStatus: SigningStatus;
  escrowReconcileTxHash: string;
  escrowReconcileResult: SigningReconcileResponse | null;
  escrowConfirmKind: EscrowKind;
  escrowConfirmTxHash: string;
  escrowConfirmOfferSequence: string;
  escrowConfirmValidated: boolean;
  escrowConfirmEngineResult: string;
  escrowConfirmResult: EscrowConfirmResponse | null;
  setEscrowReconcileKind: (value: EscrowKind) => void;
  setEscrowReconcileStatus: (value: SigningStatus) => void;
  setEscrowReconcileTxHash: (value: string) => void;
  setEscrowConfirmKind: (value: EscrowKind) => void;
  setEscrowConfirmTxHash: (value: string) => void;
  setEscrowConfirmOfferSequence: (value: string) => void;
  setEscrowConfirmValidated: (value: boolean) => void;
  setEscrowConfirmEngineResult: (value: string) => void;
  handleEscrowPrepare: () => Promise<void>;
  handleEscrowReconcile: () => Promise<void>;
  handleEscrowConfirm: () => Promise<void>;
}

export function useEscrowWorkflow({
  promoterToken,
  boutId,
  runAction,
  setLastError,
}: EscrowWorkflowOptions): EscrowWorkflowModel {
  const [escrowPrepareResult, setEscrowPrepareResult] = useState<EscrowPrepareResponse | null>(null);
  const [escrowReconcileKind, setEscrowReconcileKind] = useState<EscrowKind>("show_a");
  const [escrowReconcileStatus, setEscrowReconcileStatus] = useState<SigningStatus>("open");
  const [escrowReconcileTxHash, setEscrowReconcileTxHash] = useState("");
  const [escrowReconcileResult, setEscrowReconcileResult] = useState<SigningReconcileResponse | null>(null);

  const [escrowConfirmKind, setEscrowConfirmKind] = useState<EscrowKind>("show_a");
  const [escrowConfirmTxHash, setEscrowConfirmTxHash] = useState("TXESCROWFRONTEND001");
  const [escrowConfirmOfferSequence, setEscrowConfirmOfferSequence] = useState("1001");
  const [escrowConfirmValidated, setEscrowConfirmValidated] = useState(true);
  const [escrowConfirmEngineResult, setEscrowConfirmEngineResult] = useState("tesSUCCESS");
  const [escrowConfirmResult, setEscrowConfirmResult] = useState<EscrowConfirmResponse | null>(null);

  async function handleEscrowPrepare(): Promise<void> {
    if (!promoterToken) {
      setLastError("Promoter token is required. Log in as promoter first.");
      return;
    }
    await runAction("escrow_prepare", async () => {
      const response = await prepareEscrows(requiredBoutId(boutId), promoterToken);
      setEscrowPrepareResult(response);
    });
  }

  async function handleEscrowReconcile(): Promise<void> {
    if (!promoterToken) {
      setLastError("Promoter token is required. Log in as promoter first.");
      return;
    }
    if (!escrowPrepareResult) {
      setLastError("Run escrow prepare first.");
      return;
    }

    await runAction("escrow_signing_reconcile", async () => {
      const selected = findEscrowPrepareItem(escrowPrepareResult.escrows, escrowReconcileKind);
      const response = await reconcileEscrowSigning(requiredBoutId(boutId), promoterToken, {
        escrow_kind: escrowReconcileKind,
        payload_id: selected.xaman_sign_request.payload_id,
        observed_status: escrowReconcileStatus,
        observed_tx_hash: escrowReconcileTxHash || undefined,
      });
      setEscrowReconcileResult(response);
    });
  }

  async function handleEscrowConfirm(): Promise<void> {
    if (!promoterToken) {
      setLastError("Promoter token is required. Log in as promoter first.");
      return;
    }
    if (!escrowPrepareResult) {
      setLastError("Run escrow prepare first.");
      return;
    }

    await runAction("escrow_confirm", async () => {
      const selected = findEscrowPrepareItem(escrowPrepareResult.escrows, escrowConfirmKind);
      const tx = selected.unsigned_tx;
      const response = await confirmEscrowCreate(requiredBoutId(boutId), promoterToken, createIdempotencyKey("escrow-confirm"), {
        escrow_kind: escrowConfirmKind,
        tx_hash: escrowConfirmTxHash,
        offer_sequence: parseRequiredInteger(escrowConfirmOfferSequence, "offer_sequence"),
        validated: escrowConfirmValidated,
        engine_result: escrowConfirmEngineResult,
        owner_address: readRequiredString(tx, "Account"),
        destination_address: readRequiredString(tx, "Destination"),
        amount_drops: parseRequiredInteger(readRequiredString(tx, "Amount"), "Amount"),
        finish_after_ripple: readRequiredNumber(tx, "FinishAfter"),
        cancel_after_ripple: readOptionalNumber(tx, "CancelAfter"),
        condition_hex: readOptionalString(tx, "Condition"),
      });
      setEscrowConfirmResult(response);
    });
  }

  return {
    escrowPrepareResult,
    escrowReconcileKind,
    escrowReconcileStatus,
    escrowReconcileTxHash,
    escrowReconcileResult,
    escrowConfirmKind,
    escrowConfirmTxHash,
    escrowConfirmOfferSequence,
    escrowConfirmValidated,
    escrowConfirmEngineResult,
    escrowConfirmResult,
    setEscrowReconcileKind,
    setEscrowReconcileStatus,
    setEscrowReconcileTxHash,
    setEscrowConfirmKind,
    setEscrowConfirmTxHash,
    setEscrowConfirmOfferSequence,
    setEscrowConfirmValidated,
    setEscrowConfirmEngineResult,
    handleEscrowPrepare,
    handleEscrowReconcile,
    handleEscrowConfirm,
  };
}

