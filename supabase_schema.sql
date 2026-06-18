-- Gestão Executiva EXECUTA — v7 MULTIEMPRESA
-- Rode este arquivo no SQL Editor do Supabase antes de publicar a v7.
-- Seguro para executar mais de uma vez. Não apaga dados existentes.

create table if not exists companies (
  id text primary key,
  name text not null,
  owner_name text,
  active int default 1,
  created_at timestamptz default now()
);

insert into companies (id, name, owner_name, active)
values ('default-company', 'Empresa Principal', 'Administrador', 1)
on conflict (id) do nothing;

create table if not exists app_users (
  id text primary key,
  company_id text,
  name text,
  email text unique,
  password_salt text,
  password_hash text,
  role text,
  active int default 1,
  created_at timestamptz default now()
);

alter table app_users add column if not exists company_id text;
update app_users set company_id = 'default-company' where company_id is null or company_id = '';

create table if not exists company_profile (
  id text primary key,
  company_id text,
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
alter table company_profile add column if not exists company_id text;
update company_profile set company_id = 'default-company' where company_id is null or company_id = '';
insert into company_profile (id, company_id, company_name, owner_name, segment, business_size, monthly_revenue, fixed_costs, variable_costs, stock_value, initial_cash, notes, updated_at)
values ('main', 'default-company', '', '', '', 'Pequena', 0, 0, 0, 0, 0, '', now()::text)
on conflict (id) do nothing;

create table if not exists cash_flow (id text primary key, company_id text, date text, type text, category text, description text, amount numeric default 0, channel text, created_by text, created_at timestamptz default now());
alter table cash_flow add column if not exists company_id text;
update cash_flow set company_id = 'default-company' where company_id is null or company_id = '';

create table if not exists accounts (id text primary key, company_id text, due_date text, kind text, supplier_client text, description text, amount numeric default 0, status text default 'Aberto', paid_date text, created_by text, created_at timestamptz default now());
alter table accounts add column if not exists company_id text;
update accounts set company_id = 'default-company' where company_id is null or company_id = '';

create table if not exists action_plan (id text primary key, company_id text, priority text, area text, action text, responsible text, due_date text, status text default 'Pendente', created_by text, created_at timestamptz default now());
alter table action_plan add column if not exists company_id text;
update action_plan set company_id = 'default-company' where company_id is null or company_id = '';

create table if not exists advisor_history (id text primary key, company_id text, asked_at text, question text, answer text, created_by text);
alter table advisor_history add column if not exists company_id text;
update advisor_history set company_id = 'default-company' where company_id is null or company_id = '';

create table if not exists dre_records (id text primary key, company_id text, period_start text, period_end text, receita_bruta numeric default 0, deducoes_impostos numeric default 0, receita_liquida numeric default 0, custos_produtos_servicos numeric default 0, lucro_bruto numeric default 0, despesas_operacionais numeric default 0, resultados_financeiros numeric default 0, ebitda numeric default 0, lucro_operacional numeric default 0, lucro_liquido numeric default 0, notes text, created_by text, created_at timestamptz default now());
alter table dre_records add column if not exists company_id text;
update dre_records set company_id = 'default-company' where company_id is null or company_id = '';

create table if not exists calendar_events (id text primary key, company_id text, event_date text, event_time text, title text, category text, level text, color text, notes text, created_by text, created_at timestamptz default now());
alter table calendar_events add column if not exists company_id text;
update calendar_events set company_id = 'default-company' where company_id is null or company_id = '';

create table if not exists mvp_feedback (id text primary key, company_id text, feedback_date text, person text, profile text, score int default 0, main_pain text, liked text, missing text, objection text, status text, created_by text, created_at timestamptz default now());
alter table mvp_feedback add column if not exists company_id text;
update mvp_feedback set company_id = 'default-company' where company_id is null or company_id = '';

create table if not exists executive_routines (id text primary key, company_id text, routine_date text, routine_type text, score int default 0, focus text, decisions text, risks text, next_actions text, created_by text, created_at timestamptz default now());
alter table executive_routines add column if not exists company_id text;
update executive_routines set company_id = 'default-company' where company_id is null or company_id = '';

create table if not exists decision_log (id text primary key, company_id text, decision_date text, area text, decision text, reason text, expected_result text, owner text, due_date text, status text, created_by text, created_at timestamptz default now());
alter table decision_log add column if not exists company_id text;
update decision_log set company_id = 'default-company' where company_id is null or company_id = '';

create table if not exists marketing_playbook (id text primary key, company_id text, created_at timestamptz default now(), segment text, ideal_customer text, main_pain text, promise text, offer text, proof text, objections text, channels text, next_test text, created_by text);
alter table marketing_playbook add column if not exists company_id text;
update marketing_playbook set company_id = 'default-company' where company_id is null or company_id = '';

create table if not exists unit_economics (id text primary key, company_id text, created_at timestamptz default now(), ticket_medio numeric default 0, margem_contribuicao numeric default 0, cac numeric default 0, compras_ano numeric default 1, retencao_meses numeric default 12, churn_mensal numeric default 0, created_by text);
alter table unit_economics add column if not exists company_id text;
update unit_economics set company_id = 'default-company' where company_id is null or company_id = '';

create table if not exists okr_records (id text primary key, company_id text, created_at timestamptz default now(), quarter text, objective text, key_result text, target text, current_value text, confidence int default 5, owner text, due_date text, status text, created_by text);
alter table okr_records add column if not exists company_id text;
update okr_records set company_id = 'default-company' where company_id is null or company_id = '';

create index if not exists idx_users_company on app_users(company_id);
create index if not exists idx_profile_company on company_profile(company_id);
create index if not exists idx_cash_company_date on cash_flow(company_id, date);
create index if not exists idx_acc_company_kind on accounts(company_id, kind, status);
create index if not exists idx_actions_company_status on action_plan(company_id, status);
create index if not exists idx_dre_company_period on dre_records(company_id, period_start, period_end);
create index if not exists idx_calendar_company_date on calendar_events(company_id, event_date);
create index if not exists idx_feedback_company_date on mvp_feedback(company_id, feedback_date);
create index if not exists idx_routine_company_date on executive_routines(company_id, routine_date);
create index if not exists idx_decision_company_date on decision_log(company_id, decision_date);
create index if not exists idx_marketing_company_created on marketing_playbook(company_id, created_at);
create index if not exists idx_unit_company_created on unit_economics(company_id, created_at);
create index if not exists idx_okr_company_due on okr_records(company_id, due_date, status);

-- v7.1 PERMISSÕES
-- Garante que exista pelo menos um Dono do App.
-- Se ainda não houver, o primeiro usuário criado vira Dono do App.
update app_users
set role = 'dono do app'
where id = (
  select id from app_users
  order by created_at asc
  limit 1
)
and not exists (
  select 1 from app_users where role in ('dono do app','super_admin')
);



-- v7.4 DONO DO APP CORRIGIDO
-- Promove automaticamente os e-mails principais do dono para Dono do App.
update app_users
set role = 'dono do app'
where lower(email) in (
  'miguel.asiqueirappma@gmail.com',
  'miguelangeloppma@gmail.com',
  'miguelangelo.ppma@gmail.com'
);

-- Caso ainda não exista dono do app, promove o primeiro usuário criado.
update app_users
set role = 'dono do app'
where id = (
  select id from app_users
  order by created_at asc
  limit 1
)
and not exists (
  select 1 from app_users where role in ('dono do app','super_admin')
);
