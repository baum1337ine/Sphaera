-- SPHAERA waitlist signup fix
-- Run this in Supabase Dashboard → SQL Editor for project vizjbgtnfmmggpshtczo.
-- Purpose:
--   1) allow the website payload interest_type values used by index.html
--   2) allow anonymous/public INSERTs only for the waitlist form
--   3) keep public SELECT disabled/no email leak

begin;

-- Current site uses lead_magnet and lead_magnet_updates.
-- Existing DB check currently allows beta but rejects those values.
alter table public.waitlist_signups
  drop constraint if exists waitlist_signups_interest_type_check;

alter table public.waitlist_signups
  add constraint waitlist_signups_interest_type_check
  check (interest_type in ('beta', 'lead_magnet', 'lead_magnet_updates'));

-- RLS should stay enabled. Public users may insert signups, but not read rows.
alter table public.waitlist_signups enable row level security;

drop policy if exists "Allow public waitlist signup inserts" on public.waitlist_signups;

create policy "Allow public waitlist signup inserts"
  on public.waitlist_signups
  for insert
  to anon
  with check (
    email is not null
    and email ~* '^[^@\s]+@[^@\s]+\.[^@\s]+$'
    and interest_type in ('beta', 'lead_magnet', 'lead_magnet_updates')
    and language_code in ('de')
    and entry_source in ('rhythmus_kompass')
    and form_location in ('lead_magnet_cta')
    and page_path is not null
    and page_url is not null
  );

grant usage on schema public to anon;
grant insert on table public.waitlist_signups to anon;

-- If id is backed by a sequence, anon needs sequence usage for DEFAULT id insertion.
do $$
declare
  seq_name text;
begin
  select pg_get_serial_sequence('public.waitlist_signups', 'id') into seq_name;
  if seq_name is not null then
    execute format('grant usage on sequence %s to anon', seq_name);
  end if;
end $$;

commit;

-- Verification after running:
-- The website insert should return 201/200 via publishable key.
-- Anonymous SELECT may return [] or be denied; it must not expose email rows.
