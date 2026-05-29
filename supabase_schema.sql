-- Senebiclabs — Supabase schema
-- Run this in your Supabase project: SQL Editor → New query → paste → Run
-- Re-runnable: all statements use IF NOT EXISTS / OR REPLACE / DO NOTHING.

-- ── Expert applications ────────────────────────────────────────────────────────

create table if not exists expert_applications (
  id               uuid primary key default gen_random_uuid(),
  name             text not null,
  email            text not null,
  specialty        text not null,
  institution      text not null,
  country          text not null,
  license_number   text not null,
  years_experience text not null,
  note             text,
  status           text not null default 'pending', -- pending | approved | rejected
  lat              double precision,
  lng              double precision,
  created_at       timestamptz not null default now()
);

create index if not exists expert_applications_email_idx    on expert_applications (email);
create index if not exists expert_applications_status_idx   on expert_applications (status);
create index if not exists expert_applications_specialty_idx on expert_applications (specialty);

-- RLS: service key (backend) bypasses all policies.
-- Anon / authenticated keys have no access — data is admin-only.
alter table expert_applications enable row level security;

-- No public insert or select; all access goes through the FastAPI service key.
-- If you add an admin Supabase user later, create a policy scoped to their role here.


-- ── Waitlist ───────────────────────────────────────────────────────────────────

create table if not exists waitlist (
  id            uuid primary key default gen_random_uuid(),
  email         text not null,
  type          text not null check (type in ('patient', 'contributor', 'researcher', 'expert')),
  lat           double precision,
  lng           double precision,
  location_text text,
  created_at    timestamptz not null default now(),
  unique (email, type)
);

create index if not exists waitlist_type_idx  on waitlist (type);
create index if not exists waitlist_email_idx on waitlist (email);

-- RLS: same as above — service key only.
alter table waitlist enable row level security;


-- ── Useful admin views (run separately if wanted) ─────────────────────────────

-- Pending applications (for quick review)
-- create view pending_applications as
--   select id, name, email, specialty, institution, country, license_number,
--          years_experience, note, created_at
--   from expert_applications
--   where status = 'pending'
--   order by created_at asc;

-- Waitlist by type counts
-- create view waitlist_summary as
--   select type, count(*) as total
--   from waitlist
--   group by type
--   order by total desc;
