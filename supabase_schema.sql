
create table if not exists app_users (
  id text primary key,
  name text,
  email text unique,
  password_salt text,
  password_hash text,
  role text,
  active int default 1,
  created_at timestamptz default now()
);

create table if not exists company_profile (
  id text primary key,
  company_name text,
  owner_name text,
  segment text,
  business_size text,
  monthly_revenue numeric default 0,
  fixed_costs numeric default 0,
  variable_costs numeric default 0,
  stock_value numeric default 0,
  initial_cash numeric default 0,
  notes text,
  updated_at text
);

insert into company_profile (
  id, company_name, owner_name, segment, business_size,
  monthly_revenue, fixed_costs, variable_costs, stock_value, initial_cash, notes, updated_at
)
values ('main', '', '', '', 'Pequena', 0, 0, 0, 0, 0, '', now()::text)
on conflict (id) do nothing;

create table if not exists cash_flow (
  id text primary key,
  date text,
  type text,
  category text,
  description text,
  amount numeric default 0,
  channel text,
  created_by text,
  created_at timestamptz default now()
);

create table if not exists accounts (
  id text primary key,
  due_date text,
  kind text,
  supplier_client text,
  description text,
  amount numeric default 0,
  status text default 'Aberto',
  paid_date text,
  created_by text,
  created_at timestamptz default now()
);

create table if not exists action_plan (
  id text primary key,
  priority text,
  area text,
  action text,
  responsible text,
  due_date text,
  status text default 'Pendente',
  created_by text,
  created_at timestamptz default now()
);

create table if not exists advisor_history (
  id text primary key,
  asked_at text,
  question text,
  answer text,
  created_by text
);

create index if not exists idx_cash_date on cash_flow(date);
create index if not exists idx_acc_kind on accounts(kind, status);
create index if not exists idx_actions_status on action_plan(status);

-- MVP de teste:
-- Para facilitar o teste gratuito, você pode deixar RLS desativado.
-- Para versão profissional/vendável, implemente RLS, políticas por empresa e autenticação reforçada.
