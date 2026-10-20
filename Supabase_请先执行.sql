-- 在 Supabase SQL Editor 执行。每位用户只能读写自己的出生档案。
create table if not exists public.profiles (
 id uuid primary key references auth.users(id) on delete cascade,
 name text not null check (char_length(name) between 1 and 100),
 gender text not null check (gender in ('男','女')),
 calendar text not null default 'solar' check (calendar in ('solar','lunar')),
 year integer not null check (year between 1900 and 2200),
 month integer not null check (month between 1 and 12),
 day integer not null check (day between 1 and 31),
 hour integer not null check (hour between 0 and 2359),
 minute integer not null default 0 check (minute between 0 and 59),
 updated_at timestamptz not null default now()
);
alter table public.profiles enable row level security;
revoke all on public.profiles from anon;
grant select,insert,update on public.profiles to authenticated;
drop policy if exists "profile_select_self" on public.profiles;
drop policy if exists "profile_insert_self" on public.profiles;
drop policy if exists "profile_update_self" on public.profiles;
create policy "profile_select_self" on public.profiles for select to authenticated using ((select auth.uid()) = id);
create policy "profile_insert_self" on public.profiles for insert to authenticated with check ((select auth.uid()) = id);
create policy "profile_update_self" on public.profiles for update to authenticated using ((select auth.uid()) = id) with check ((select auth.uid()) = id);
