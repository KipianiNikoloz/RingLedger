import type { FormEvent } from "react";
import { useState } from "react";

import type {
  BoutResultResponse,
  BoutListResponse,
  BoutSummaryResponse,
  EscrowConfirmResponse,
  EscrowKind,
  EscrowPrepareResponse,
  FighterProfileResponse,
  PayoutConfirmResponse,
  PayoutPrepareResponse,
  SigningReconcileResponse,
  UserRole,
} from "../api/types";
import type { SigningStatus } from "../constants";
import { useActionRunner } from "./useActionRunner";
import { useAuthWorkflow } from "./useAuthWorkflow";
import { useEscrowWorkflow } from "./useEscrowWorkflow";
import { useManagementWorkflow } from "./useManagementWorkflow";
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
  provisionEmail: string;
  provisionPassword: string;
  provisionRole: Exclude<UserRole, "fighter">;
  loginEmail: string;
  loginPassword: string;
  boutId: string;
  fighterDisplayName: string;
  fighterXrplAddress: string;
  fighterProfileResult: FighterProfileResponse | null;
  createFighterAUserId: string;
  createFighterBUserId: string;
  createEventDatetimeUtc: string;
  createPromoterOwnerAddress: string;
  createShowADrops: string;
  createShowBDrops: string;
  createBonusADrops: string;
  createBonusBDrops: string;
  boutCreateResult: BoutSummaryResponse | null;
  boutListResult: BoutListResponse | null;
  boutDetailResult: BoutSummaryResponse | null;
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
  setProvisionEmail: (value: string) => void;
  setProvisionPassword: (value: string) => void;
  setProvisionRole: (value: Exclude<UserRole, "fighter">) => void;
  setLoginEmail: (value: string) => void;
  setLoginPassword: (value: string) => void;
  setBoutId: (value: string) => void;
  setFighterDisplayName: (value: string) => void;
  setFighterXrplAddress: (value: string) => void;
  setCreateFighterAUserId: (value: string) => void;
  setCreateFighterBUserId: (value: string) => void;
  setCreateEventDatetimeUtc: (value: string) => void;
  setCreatePromoterOwnerAddress: (value: string) => void;
  setCreateShowADrops: (value: string) => void;
  setCreateShowBDrops: (value: string) => void;
  setCreateBonusADrops: (value: string) => void;
  setCreateBonusBDrops: (value: string) => void;
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
  handleProvision: (event: FormEvent<HTMLFormElement>) => Promise<void>;
  handleLogin: (event: FormEvent<HTMLFormElement>) => Promise<void>;
  handleFighterProfileUpsert: (event: FormEvent<HTMLFormElement>) => Promise<void>;
  handleBoutCreate: (event: FormEvent<HTMLFormElement>) => Promise<void>;
  handleBoutList: () => Promise<void>;
  handleBoutLoad: () => Promise<void>;
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
  const management = useManagementWorkflow({
    promoterToken: auth.promoterToken,
    fighterToken: auth.fighterToken,
    adminToken: auth.adminToken,
    boutId,
    setBoutId,
    runAction: actionRunner.runAction,
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
    provisionEmail: auth.provisionEmail,
    provisionPassword: auth.provisionPassword,
    provisionRole: auth.provisionRole,
    loginEmail: auth.loginEmail,
    loginPassword: auth.loginPassword,
    boutId,
    fighterDisplayName: management.fighterDisplayName,
    fighterXrplAddress: management.fighterXrplAddress,
    fighterProfileResult: management.fighterProfileResult,
    createFighterAUserId: management.createFighterAUserId,
    createFighterBUserId: management.createFighterBUserId,
    createEventDatetimeUtc: management.createEventDatetimeUtc,
    createPromoterOwnerAddress: management.createPromoterOwnerAddress,
    createShowADrops: management.createShowADrops,
    createShowBDrops: management.createShowBDrops,
    createBonusADrops: management.createBonusADrops,
    createBonusBDrops: management.createBonusBDrops,
    boutCreateResult: management.boutCreateResult,
    boutListResult: management.boutListResult,
    boutDetailResult: management.boutDetailResult,
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
    setProvisionEmail: auth.setProvisionEmail,
    setProvisionPassword: auth.setProvisionPassword,
    setProvisionRole: auth.setProvisionRole,
    setLoginEmail: auth.setLoginEmail,
    setLoginPassword: auth.setLoginPassword,
    setBoutId,
    setFighterDisplayName: management.setFighterDisplayName,
    setFighterXrplAddress: management.setFighterXrplAddress,
    setCreateFighterAUserId: management.setCreateFighterAUserId,
    setCreateFighterBUserId: management.setCreateFighterBUserId,
    setCreateEventDatetimeUtc: management.setCreateEventDatetimeUtc,
    setCreatePromoterOwnerAddress: management.setCreatePromoterOwnerAddress,
    setCreateShowADrops: management.setCreateShowADrops,
    setCreateShowBDrops: management.setCreateShowBDrops,
    setCreateBonusADrops: management.setCreateBonusADrops,
    setCreateBonusBDrops: management.setCreateBonusBDrops,
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
    handleProvision: auth.handleProvision,
    handleLogin: auth.handleLogin,
    handleFighterProfileUpsert: management.handleFighterProfileUpsert,
    handleBoutCreate: management.handleBoutCreate,
    handleBoutList: management.handleBoutList,
    handleBoutLoad: management.handleBoutLoad,
    handleEscrowPrepare: escrow.handleEscrowPrepare,
    handleEscrowReconcile: escrow.handleEscrowReconcile,
    handleEscrowConfirm: escrow.handleEscrowConfirm,
    handleResultEntry: resultPayout.handleResultEntry,
    handlePayoutPrepare: resultPayout.handlePayoutPrepare,
    handlePayoutReconcile: resultPayout.handlePayoutReconcile,
    handlePayoutConfirm: resultPayout.handlePayoutConfirm,
  };
}
