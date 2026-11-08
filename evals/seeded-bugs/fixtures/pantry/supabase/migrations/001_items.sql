create table items (
  id uuid primary key default gen_random_uuid(),
  owner_id uuid references auth.users not null,
  name text not null,
  quantity integer,
  status text
);

alter table items enable row level security;
create policy "items are readable" on items for select using (true);
create policy "owners write items" on items for all using (auth.uid() = owner_id);

create table profiles (
  id uuid primary key references auth.users,
  scan_credits integer not null default 0
);
