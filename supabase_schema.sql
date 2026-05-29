-- Senebia — Supabase schema
-- Run this in your Supabase project: SQL Editor → New query → paste → Run

-- Expert applications
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

create index if not exists expert_applications_email_idx on expert_applications (email);
create index if not exists expert_applications_status_idx on expert_applications (status);
create index if not exists expert_applications_specialty_idx on expert_applications (specialty);

-- Row-level security — service key bypasses, anon key cannot read
alter table expert_applications enable row level security;


-- Waitlist (patients, contributors, researchers)
create table if not exists waitlist (
  id            uuid primary key default gen_random_uuid(),
  email         text not null,
  type          text not null, -- patient | contributor | researcher | expert
  lat           double precision,
  lng           double precision,
  location_text text,
  created_at    timestamptz not null default now(),
  unique (email, type)
);

create index if not exists waitlist_type_idx on waitlist (type);
create index if not exists waitlist_email_idx on waitlist (email);

-- Row-level security
alter table waitlist enable row level security;
