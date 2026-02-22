import type { FormEvent } from "react";
import { useState } from "react";

import type {
  BoutResultResponse,
  EscrowConfirmResponse,
  EscrowKind,
  EscrowPrepareResponse,
  PayoutConfirmResponse,
  PayoutPrepareResponse,
  SigningReconcileResponse,
  UserRole,
} from "../api/types";
import type { SigningStatus } from "../constants";
import { useActionRunner } from "./useActionRunner";
import { useAuthWorkflow } from "./useAuthWorkflow";
import { useEscrowWorkflow } from "./useEscrowWorkflow";
import { useResultPayoutWorkflow } from "./useResultPayoutWorkflow";

export interface RingLedgerConsoleModel {
  busy: boolean;
  lastError: string | null;
  actionLog: string[];
  currentRoleSummary: string;
  registerEmail: string;
  registerPassword: string;
  registerRole: UserRole;
  registerResult: unknown;
  loginEmail: string;
  loginPassword: string;
  boutId: string;
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
  setRegisterEmail: (value: string) => void;
  setRegisterPassword: (value: string) => void;
  setRegisterRole: (value: UserRole) => void;
  setLoginEmail: (value: string) => void;
  setLoginPassword: (value: string) => void;
  setBoutId: (value: string) => void;
  setEscrowReconcileKind: (value: EscrowKind) => void;
  setEscrowReconcileStatus: (value: SigningStatus) => void;
  setEscrowReconcileTxHash: (value: string) => void;
  setEscrowConfirmKind: (value: EscrowKind) => void;
  setEscrowConfirmTxHash: (value: string) => void;
  setEscrowConfirmOfferSequence: (value: string) => void;
  setEscrowConfirmValidated: (value: boolean) => void;
  setEscrowConfirmEngineResult: (value: string) => void;
  setWinner: (value: "A" | "B") => void;
  setPayoutReconcileKind: (value: EscrowKind) => void;
  setPayoutReconcileStatus: (value: SigningStatus) => void;
  setPayoutReconcileTxHash: (value: string) => void;
  setPayoutConfirmKind: (value: EscrowKind) => void;
  setPayoutConfirmTxHash: (value: string) => void;
  setPayoutConfirmValidated: (value: boolean) => void;
  setPayoutConfirmEngineResult: (value: string) => void;
  setPayoutCloseTimeRipple: (value: string) => void;
  handleRegister: (event: FormEvent<HTMLFormElement>) => Promise<void>;
  handleLogin: (event: FormEvent<HTMLFormElement>) => Promise<void>;
  handleEscrowPrepare: () => Promise<void>;
  handleEscrowReconcile: () => Promise<void>;
  handleEscrowConfirm: () => Promise<void>;
  handleResultEntry: () => Promise<void>;
  handlePayoutPrepare: () => Promise<void>;
  handlePayoutReconcile: () => Promise<void>;
  handlePayoutConfirm: () => Promise<void>;
}

export function useRingLedgerConsole(): RingLedgerConsoleModel {
  const actionRunner = useActionRunner();
  const [boutId, setBoutId] = useState("");

  const auth = useAuthWorkflow({
    runAction: actionRunner.runAction,
    pushLog: actionRunner.pushLog,
  });
  const escrow = useEscrowWorkflow({
    promoterToken: auth.promoterToken,
    boutId,
    runAction: actionRunner.runAction,
    setLastError: actionRunner.setLastError,
  });
  const resultPayout = useResultPayoutWorkflow({
    promoterToken: auth.promoterToken,
    adminToken: auth.adminToken,
    boutId,
    runAction: actionRunner.runAction,
    setLastError: actionRunner.setLastError,
  });

  return {
    busy: actionRunner.busy,
    lastError: actionRunner.lastError,
    actionLog: actionRunner.actionLog,
    currentRoleSummary: auth.currentRoleSummary,
    registerEmail: auth.registerEmail,
    registerPassword: auth.registerPassword,
    registerRole: auth.registerRole,
    registerResult: auth.registerResult,
    loginEmail: auth.loginEmail,
    loginPassword: auth.loginPassword,
    boutId,
    escrowPrepareResult: escrow.escrowPrepareResult,
    escrowReconcileKind: escrow.escrowReconcileKind,
    escrowReconcileStatus: escrow.escrowReconcileStatus,
    escrowReconcileTxHash: escrow.escrowReconcileTxHash,
    escrowReconcileResult: escrow.escrowReconcileResult,
    escrowConfirmKind: escrow.escrowConfirmKind,
    escrowConfirmTxHash: escrow.escrowConfirmTxHash,
    escrowConfirmOfferSequence: escrow.escrowConfirmOfferSequence,
    escrowConfirmValidated: escrow.escrowConfirmValidated,
    escrowConfirmEngineResult: escrow.escrowConfirmEngineResult,
    escrowConfirmResult: escrow.escrowConfirmResult,
    winner: resultPayout.winner,
    resultEntry: resultPayout.resultEntry,
    payoutPrepareResult: resultPayout.payoutPrepareResult,
    payoutReconcileKind: resultPayout.payoutReconcileKind,
    payoutReconcileStatus: resultPayout.payoutReconcileStatus,
    payoutReconcileTxHash: resultPayout.payoutReconcileTxHash,
    payoutReconcileResult: resultPayout.payoutReconcileResult,
    payoutConfirmKind: resultPayout.payoutConfirmKind,
    payoutConfirmTxHash: resultPayout.payoutConfirmTxHash,
    payoutConfirmValidated: resultPayout.payoutConfirmValidated,
    payoutConfirmEngineResult: resultPayout.payoutConfirmEngineResult,
    payoutCloseTimeRipple: resultPayout.payoutCloseTimeRipple,
    payoutConfirmResult: resultPayout.payoutConfirmResult,
    setRegisterEmail: auth.setRegisterEmail,
    setRegisterPassword: auth.setRegisterPassword,
    setRegisterRole: auth.setRegisterRole,
    setLoginEmail: auth.setLoginEmail,
    setLoginPassword: auth.setLoginPassword,
    setBoutId,
    setEscrowReconcileKind: escrow.setEscrowReconcileKind,
    setEscrowReconcileStatus: escrow.setEscrowReconcileStatus,
    setEscrowReconcileTxHash: escrow.setEscrowReconcileTxHash,
    setEscrowConfirmKind: escrow.setEscrowConfirmKind,
    setEscrowConfirmTxHash: escrow.setEscrowConfirmTxHash,
    setEscrowConfirmOfferSequence: escrow.setEscrowConfirmOfferSequence,
    setEscrowConfirmValidated: escrow.setEscrowConfirmValidated,
    setEscrowConfirmEngineResult: escrow.setEscrowConfirmEngineResult,
    setWinner: resultPayout.setWinner,
    setPayoutReconcileKind: resultPayout.setPayoutReconcileKind,
    setPayoutReconcileStatus: resultPayout.setPayoutReconcileStatus,
    setPayoutReconcileTxHash: resultPayout.setPayoutReconcileTxHash,
    setPayoutConfirmKind: resultPayout.setPayoutConfirmKind,
    setPayoutConfirmTxHash: resultPayout.setPayoutConfirmTxHash,
    setPayoutConfirmValidated: resultPayout.setPayoutConfirmValidated,
    setPayoutConfirmEngineResult: resultPayout.setPayoutConfirmEngineResult,
    setPayoutCloseTimeRipple: resultPayout.setPayoutCloseTimeRipple,
    handleRegister: auth.handleRegister,
    handleLogin: auth.handleLogin,
    handleEscrowPrepare: escrow.handleEscrowPrepare,
    handleEscrowReconcile: escrow.handleEscrowReconcile,
    handleEscrowConfirm: escrow.handleEscrowConfirm,
    handleResultEntry: resultPayout.handleResultEntry,
    handlePayoutPrepare: resultPayout.handlePayoutPrepare,
    handlePayoutReconcile: resultPayout.handlePayoutReconcile,
    handlePayoutConfirm: resultPayout.handlePayoutConfirm,
  };
}
