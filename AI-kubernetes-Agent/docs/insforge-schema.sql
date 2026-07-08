create table if not exists public.investigations (
  id uuid primary key default gen_random_uuid(),
  user_id text not null default (auth.uid())::text,
  root_cause text not null,
  namespace text,
  confidence integer not null default 0 check (confidence >= 0 and confidence <= 100),
  status text not null default 'success',
  diagnosis jsonb not null default '{}'::jsonb,
  created_at timestamptz not null default now()
);

alter table public.investigations enable row level security;

drop policy if exists investigations_select_own on public.investigations;
create policy investigations_select_own
on public.investigations
for select
using (user_id = (auth.uid())::text);

drop policy if exists investigations_insert_own on public.investigations;
create policy investigations_insert_own
on public.investigations
for insert
with check (user_id = (auth.uid())::text);

drop policy if exists investigations_update_own on public.investigations;
create policy investigations_update_own
on public.investigations
for update
using (user_id = (auth.uid())::text)
with check (user_id = (auth.uid())::text);

create index if not exists investigations_user_created_idx
on public.investigations (user_id, created_at desc);

create table if not exists public.investigation_progress (
  id uuid primary key default gen_random_uuid(),
  user_id text not null default (auth.uid())::text,
  investigation_id uuid references public.investigations(id) on delete cascade,
  run_id text not null,
  step_id text not null,
  step_label text not null,
  status text not null check (status in ('pending', 'active', 'complete', 'error')),
  created_at timestamptz not null default now()
);

alter table public.investigation_progress enable row level security;

drop policy if exists investigation_progress_select_own on public.investigation_progress;
create policy investigation_progress_select_own
on public.investigation_progress
for select
using (user_id = (auth.uid())::text);

drop policy if exists investigation_progress_insert_own on public.investigation_progress;
create policy investigation_progress_insert_own
on public.investigation_progress
for insert
with check (user_id = (auth.uid())::text);

drop policy if exists investigation_progress_update_own on public.investigation_progress;
create policy investigation_progress_update_own
on public.investigation_progress
for update
using (user_id = (auth.uid())::text)
with check (user_id = (auth.uid())::text);

create index if not exists investigation_progress_user_run_idx
on public.investigation_progress (user_id, run_id, created_at);

create index if not exists investigation_progress_investigation_idx
on public.investigation_progress (investigation_id, created_at);
