import type { FormEvent } from "react";

interface BoutWorkspacePanelProps {
  busy: boolean;
  boutId: string;
  fighterDisplayName: string;
  fighterXrplAddress: string;
  createFighterAUserId: string;
  createFighterBUserId: string;
  createEventDatetimeUtc: string;
  createPromoterOwnerAddress: string;
  createShowADrops: string;
  createShowBDrops: string;
  createBonusADrops: string;
  createBonusBDrops: string;
  listCount: number | null;
  onBoutIdChange: (value: string) => void;
  onFighterDisplayNameChange: (value: string) => void;
  onFighterXrplAddressChange: (value: string) => void;
  onCreateFighterAUserIdChange: (value: string) => void;
  onCreateFighterBUserIdChange: (value: string) => void;
  onCreateEventDatetimeUtcChange: (value: string) => void;
  onCreatePromoterOwnerAddressChange: (value: string) => void;
  onCreateShowADropsChange: (value: string) => void;
  onCreateShowBDropsChange: (value: string) => void;
  onCreateBonusADropsChange: (value: string) => void;
  onCreateBonusBDropsChange: (value: string) => void;
  onFighterProfileUpsert: (event: FormEvent<HTMLFormElement>) => void;
  onBoutCreate: (event: FormEvent<HTMLFormElement>) => void;
  onBoutList: () => void;
  onBoutLoad: () => void;
}

export function BoutWorkspacePanel({
  busy,
  boutId,
  fighterDisplayName,
  fighterXrplAddress,
  createFighterAUserId,
  createFighterBUserId,
  createEventDatetimeUtc,
  createPromoterOwnerAddress,
  createShowADrops,
  createShowBDrops,
  createBonusADrops,
  createBonusBDrops,
  listCount,
  onBoutIdChange,
  onFighterDisplayNameChange,
  onFighterXrplAddressChange,
  onCreateFighterAUserIdChange,
  onCreateFighterBUserIdChange,
  onCreateEventDatetimeUtcChange,
  onCreatePromoterOwnerAddressChange,
  onCreateShowADropsChange,
  onCreateShowBDropsChange,
  onCreateBonusADropsChange,
  onCreateBonusBDropsChange,
  onFighterProfileUpsert,
  onBoutCreate,
  onBoutList,
  onBoutLoad,
}: BoutWorkspacePanelProps) {
  return (
    <section className="panel workflow-panel">
      <div className="panel-header">
        <h2>Bout Workspace</h2>
        <p className="panel-note">Create setup records, select an active bout, then continue escrow, result, and payout actions.</p>
      </div>

      <form className="form-panel" onSubmit={onFighterProfileUpsert}>
        <h3>Fighter Profile</h3>
        <div className="grid two-col">
          <label>
            Display name
            <input
              type="text"
              name="fighter_display_name"
              value={fighterDisplayName}
              onChange={(event) => onFighterDisplayNameChange(event.target.value)}
            />
          </label>
          <label>
            XRPL address
            <input
              type="text"
              name="fighter_xrpl_address"
              value={fighterXrplAddress}
              onChange={(event) => onFighterXrplAddressChange(event.target.value)}
            />
          </label>
        </div>
        <button type="submit" disabled={busy} data-testid="fighter-profile-submit">
          Save fighter profile
        </button>
      </form>

      <form className="form-panel" onSubmit={onBoutCreate}>
        <h3>Create Bout Draft</h3>
        <div className="grid two-col">
          <label>
            Fighter A user ID
            <input
              type="text"
              name="fighter_a_user_id"
              value={createFighterAUserId}
              onChange={(event) => onCreateFighterAUserIdChange(event.target.value)}
            />
          </label>
          <label>
            Fighter B user ID
            <input
              type="text"
              name="fighter_b_user_id"
              value={createFighterBUserId}
              onChange={(event) => onCreateFighterBUserIdChange(event.target.value)}
            />
          </label>
          <label>
            Event UTC
            <input
              type="text"
              name="event_datetime_utc"
              value={createEventDatetimeUtc}
              onChange={(event) => onCreateEventDatetimeUtcChange(event.target.value)}
            />
          </label>
          <label>
            Promoter XRPL address
            <input
              type="text"
              name="promoter_owner_address"
              value={createPromoterOwnerAddress}
              onChange={(event) => onCreatePromoterOwnerAddressChange(event.target.value)}
            />
          </label>
        </div>
        <div className="grid four-col">
          <label>
            Show A drops
            <input
              type="number"
              min="1"
              name="show_a_drops"
              value={createShowADrops}
              onChange={(event) => onCreateShowADropsChange(event.target.value)}
            />
          </label>
          <label>
            Show B drops
            <input
              type="number"
              min="1"
              name="show_b_drops"
              value={createShowBDrops}
              onChange={(event) => onCreateShowBDropsChange(event.target.value)}
            />
          </label>
          <label>
            Bonus A drops
            <input
              type="number"
              min="1"
              name="bonus_a_drops"
              value={createBonusADrops}
              onChange={(event) => onCreateBonusADropsChange(event.target.value)}
            />
          </label>
          <label>
            Bonus B drops
            <input
              type="number"
              min="1"
              name="bonus_b_drops"
              value={createBonusBDrops}
              onChange={(event) => onCreateBonusBDropsChange(event.target.value)}
            />
          </label>
        </div>
        <button type="submit" disabled={busy} data-testid="bout-create-submit">
          Create bout
        </button>
      </form>

      <div className="form-panel">
        <h3>Active Bout</h3>
        <label className="wide-label">
          Bout ID
          <input
            type="text"
            name="bout_id"
            value={boutId}
            onChange={(event) => onBoutIdChange(event.target.value)}
            placeholder="e.g. 123e4567-e89b-12d3-a456-426614174000"
          />
        </label>
        <div className="grid two-col inline-action">
          <button type="button" onClick={onBoutList} disabled={busy} data-testid="bout-list-submit">
            List bouts
          </button>
          <button type="button" onClick={onBoutLoad} disabled={busy} data-testid="bout-load-submit">
            Load bout
          </button>
        </div>
        <p className="panel-note">{listCount === null ? "No list loaded" : `${listCount} accessible bouts loaded`}</p>
      </div>
    </section>
  );
}
