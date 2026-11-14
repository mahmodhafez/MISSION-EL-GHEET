-- Three tables, one scenario revision counter (backend design §4, D2), plus a usage counter for the
-- public deployment's daily ceilings (§10a): counts only, no addresses.
CREATE TABLE IF NOT EXISTS scenarios (
  id TEXT PRIMARY KEY,
  revision INTEGER NOT NULL,
  data_release TEXT NOT NULL,
  input_json TEXT NOT NULL,          -- {snapshot, exploration, confirm_exploration}
  created_at TEXT NOT NULL,
  updated_at TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS results (
  id TEXT PRIMARY KEY,
  scenario_id TEXT NOT NULL REFERENCES scenarios(id),
  revision INTEGER NOT NULL,
  kind TEXT NOT NULL,                -- promise_test
  data_release TEXT NOT NULL,
  payload_json TEXT NOT NULL,
  created_at TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS evidence_cards (
  id TEXT PRIMARY KEY,
  scenario_id TEXT NOT NULL REFERENCES scenarios(id),
  revision INTEGER NOT NULL,
  result_id TEXT NOT NULL REFERENCES results(id),
  payload_json TEXT NOT NULL,
  created_at TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS usage (
  day TEXT NOT NULL,                 -- UTC date
  kind TEXT NOT NULL,                -- e.g. speech
  count INTEGER NOT NULL,
  PRIMARY KEY (day, kind)
);
