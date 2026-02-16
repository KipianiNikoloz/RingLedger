-- FightPurse MVP initial schema (PostgreSQL)
-- R-02, R-03, R-04, R-07, R-09 foundation

CREATE TYPE user_role AS ENUM ('promoter', 'fighter', 'management', 'admin');
CREATE TYPE bout_status AS ENUM (
  'draft',
  'ready_for_escrow',
  'escrows_created',
  'result_entered',
  'payouts_in_progress',
  'closed'
);
CREATE TYPE escrow_kind AS ENUM ('show_a', 'show_b', 'bonus_a', 'bonus_b');
CREATE TYPE escrow_status AS ENUM ('planned', 'created', 'finished', 'cancelled', 'failed');
CREATE TYPE bout_winner AS ENUM ('A', 'B');

CREATE TABLE users (
  id UUID PRIMARY KEY,
  email VARCHAR(320) NOT NULL UNIQUE,
  password_hash VARCHAR(512) NOT NULL,
  role user_role NOT NULL,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE fighter_profiles (
  id UUID PRIMARY KEY,
  user_id UUID NOT NULL UNIQUE REFERENCES users(id),
  display_name VARCHAR(120) NOT NULL,
  xrpl_address VARCHAR(64) NOT NULL UNIQUE,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE bouts (
  id UUID PRIMARY KEY,
  promoter_user_id UUID NOT NULL REFERENCES users(id),
  fighter_a_user_id UUID NOT NULL REFERENCES users(id),
  fighter_b_user_id UUID NOT NULL REFERENCES users(id),
  event_datetime_utc TIMESTAMPTZ NOT NULL,
  finish_after_utc TIMESTAMPTZ NOT NULL,
  cancel_after_utc TIMESTAMPTZ NOT NULL,
  show_a_drops BIGINT NOT NULL,
  show_b_drops BIGINT NOT NULL,
  bonus_a_drops BIGINT NOT NULL,
  bonus_b_drops BIGINT NOT NULL,
  status bout_status NOT NULL DEFAULT 'draft',
  winner bout_winner NULL,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  CHECK (show_a_drops >= 0),
  CHECK (show_b_drops >= 0),
  CHECK (bonus_a_drops >= 0),
  CHECK (bonus_b_drops >= 0),
  CHECK (fighter_a_user_id <> fighter_b_user_id)
);

CREATE TABLE escrows (
  id UUID PRIMARY KEY,
  bout_id UUID NOT NULL REFERENCES bouts(id),
  kind escrow_kind NOT NULL,
  status escrow_status NOT NULL DEFAULT 'planned',
  owner_address VARCHAR(64) NOT NULL,
  destination_address VARCHAR(64) NOT NULL,
  amount_drops BIGINT NOT NULL CHECK (amount_drops >= 0),
  finish_after_ripple INTEGER NOT NULL,
  cancel_after_ripple INTEGER NULL,
  condition_hex VARCHAR(1024) NULL,
  encrypted_preimage_hex VARCHAR(4096) NULL,
  offer_sequence INTEGER NULL,
  create_tx_hash VARCHAR(128) NULL,
  close_tx_hash VARCHAR(128) NULL,
  failure_code VARCHAR(64) NULL,
  failure_reason VARCHAR(1024) NULL,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  CONSTRAINT uq_escrow_bout_kind UNIQUE (bout_id, kind)
);

CREATE TABLE audit_log (
  id UUID PRIMARY KEY,
  actor_user_id UUID NULL REFERENCES users(id),
  action VARCHAR(64) NOT NULL,
  entity_type VARCHAR(64) NOT NULL,
  entity_id VARCHAR(128) NOT NULL,
  outcome VARCHAR(32) NOT NULL,
  details_json TEXT NULL,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE idempotency_keys (
  id UUID PRIMARY KEY,
  scope VARCHAR(120) NOT NULL,
  idempotency_key VARCHAR(128) NOT NULL,
  request_hash VARCHAR(128) NOT NULL,
  response_code INTEGER NOT NULL,
  response_body TEXT NOT NULL,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  CONSTRAINT uq_idempotency_scope_key UNIQUE (scope, idempotency_key)
);

CREATE INDEX idx_bouts_promoter_user_id ON bouts (promoter_user_id);
CREATE INDEX idx_bouts_event_datetime_utc ON bouts (event_datetime_utc);
CREATE INDEX idx_bouts_status ON bouts (status);
CREATE INDEX idx_escrows_bout_id ON escrows (bout_id);
CREATE INDEX idx_escrows_status ON escrows (status);
CREATE INDEX idx_escrows_owner_offer_sequence ON escrows (owner_address, offer_sequence);
CREATE INDEX idx_fighter_profiles_xrpl_address ON fighter_profiles (xrpl_address);
