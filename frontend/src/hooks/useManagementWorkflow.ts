import type { FormEvent } from "react";
import { useState } from "react";

import { createBout, getBout, listBouts, upsertFighterProfile } from "../api/client";
import type { BoutListResponse, BoutSummaryResponse, FighterProfileResponse } from "../api/types";

interface ManagementWorkflowOptions {
  promoterToken: string | undefined;
  fighterToken: string | undefined;
  adminToken: string | undefined;
  boutId: string;
  setBoutId: (value: string) => void;
  runAction: (label: string, callback: () => Promise<void>) => Promise<void>;
}

export interface ManagementWorkflowModel {
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
  handleFighterProfileUpsert: (event: FormEvent<HTMLFormElement>) => Promise<void>;
  handleBoutCreate: (event: FormEvent<HTMLFormElement>) => Promise<void>;
  handleBoutList: () => Promise<void>;
  handleBoutLoad: () => Promise<void>;
}

export function useManagementWorkflow({
  promoterToken,
  fighterToken,
  adminToken,
  boutId,
  setBoutId,
  runAction,
}: ManagementWorkflowOptions): ManagementWorkflowModel {
  const [fighterDisplayName, setFighterDisplayName] = useState("Fighter Alpha");
  const [fighterXrplAddress, setFighterXrplAddress] = useState("rAAAAAAAAAAAAAAAAAAAAAAAA");
  const [fighterProfileResult, setFighterProfileResult] = useState<FighterProfileResponse | null>(null);

  const [createFighterAUserId, setCreateFighterAUserId] = useState("");
  const [createFighterBUserId, setCreateFighterBUserId] = useState("");
  const [createEventDatetimeUtc, setCreateEventDatetimeUtc] = useState("2026-02-18T20:00:00Z");
  const [createPromoterOwnerAddress, setCreatePromoterOwnerAddress] = useState("rCCCCCCCCCCCCCCCCCCCCCCCC");
  const [createShowADrops, setCreateShowADrops] = useState("2000000");
  const [createShowBDrops, setCreateShowBDrops] = useState("2500000");
  const [createBonusADrops, setCreateBonusADrops] = useState("500000");
  const [createBonusBDrops, setCreateBonusBDrops] = useState("750000");
  const [boutCreateResult, setBoutCreateResult] = useState<BoutSummaryResponse | null>(null);
  const [boutListResult, setBoutListResult] = useState<BoutListResponse | null>(null);
  const [boutDetailResult, setBoutDetailResult] = useState<BoutSummaryResponse | null>(null);

  async function handleFighterProfileUpsert(event: FormEvent<HTMLFormElement>): Promise<void> {
    event.preventDefault();
    await runAction("fighter_profile_upsert", async () => {
      if (!fighterToken) {
        throw new Error("Fighter token is required for profile setup.");
      }
      const response = await upsertFighterProfile(fighterToken, {
        display_name: fighterDisplayName,
        xrpl_address: fighterXrplAddress,
      });
      setFighterProfileResult(response);
    });
  }

  async function handleBoutCreate(event: FormEvent<HTMLFormElement>): Promise<void> {
    event.preventDefault();
    await runAction("bout_create", async () => {
      if (!promoterToken) {
        throw new Error("Promoter token is required for bout creation.");
      }
      const response = await createBout(promoterToken, {
        fighter_a_user_id: createFighterAUserId,
        fighter_b_user_id: createFighterBUserId,
        event_datetime_utc: createEventDatetimeUtc,
        promoter_owner_address: createPromoterOwnerAddress,
        show_a_drops: parseDrops(createShowADrops, "show A drops"),
        show_b_drops: parseDrops(createShowBDrops, "show B drops"),
        bonus_a_drops: parseDrops(createBonusADrops, "bonus A drops"),
        bonus_b_drops: parseDrops(createBonusBDrops, "bonus B drops"),
      });
      setBoutCreateResult(response);
      setBoutDetailResult(response);
      setBoutId(response.bout_id);
    });
  }

  async function handleBoutList(): Promise<void> {
    await runAction("bout_list", async () => {
      const token = promoterToken ?? adminToken ?? fighterToken;
      if (!token) {
        throw new Error("A role token is required to list bouts.");
      }
      const response = await listBouts(token);
      setBoutListResult(response);
      if (!boutId.trim() && response.bouts[0]) {
        setBoutId(response.bouts[0].bout_id);
      }
    });
  }

  async function handleBoutLoad(): Promise<void> {
    await runAction("bout_load", async () => {
      const token = promoterToken ?? adminToken ?? fighterToken;
      if (!token) {
        throw new Error("A role token is required to load a bout.");
      }
      const selectedBoutId = boutId.trim();
      if (!selectedBoutId) {
        throw new Error("Bout ID is required to load detail.");
      }
      const response = await getBout(selectedBoutId, token);
      setBoutDetailResult(response);
      setBoutId(response.bout_id);
    });
  }

  return {
    fighterDisplayName,
    fighterXrplAddress,
    fighterProfileResult,
    createFighterAUserId,
    createFighterBUserId,
    createEventDatetimeUtc,
    createPromoterOwnerAddress,
    createShowADrops,
    createShowBDrops,
    createBonusADrops,
    createBonusBDrops,
    boutCreateResult,
    boutListResult,
    boutDetailResult,
    setFighterDisplayName,
    setFighterXrplAddress,
    setCreateFighterAUserId,
    setCreateFighterBUserId,
    setCreateEventDatetimeUtc,
    setCreatePromoterOwnerAddress,
    setCreateShowADrops,
    setCreateShowBDrops,
    setCreateBonusADrops,
    setCreateBonusBDrops,
    handleFighterProfileUpsert,
    handleBoutCreate,
    handleBoutList,
    handleBoutLoad,
  };
}

function parseDrops(value: string, label: string): number {
  const parsed = Number(value);
  if (!Number.isInteger(parsed) || parsed <= 0) {
    throw new Error(`${label} must be a positive integer.`);
  }
  return parsed;
}
