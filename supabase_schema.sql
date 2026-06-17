-- Gestão Executiva EXECUTA Web PRO v4 FINAL
-- Rode este arquivo no SQL Editor do Supabase.
-- Seguro para executar mais de uma vez.

create table if not exists app_users (id text primary key,name text,email text unique,password_salt text,password_hash text,role text,active int default 1,created_at timestamptz default now());
create table if not exists company_profile (id text primary key,company_name text,owner_name text,segment text,business_size text,monthly_revenue numeric default 0,fixed_costs numeric default 0,variable_costs numeric default 0,stock_value numeric default 0,initial_cash numeric default 0,notes text,updated_at text);
insert into company_profile (id, company_name, owner_name, segment, business_size, monthly_revenue, fixed_costs, variable_costs, stock_value, initial_cash, notes, updated_at) values ('main', '', '', '', 'Pequena', 0, 0, 0, 0, 0, '', now()::text) on conflict (id) do nothing;
create table if not exists cash_flow (id text primary key,date text,type text,category text,description text,amount numeric default 0,channel text,created_by text,created_at timestamptz default now());
create table if not exists accounts (id text primary key,due_date text,kind text,supplier_client text,description text,amount numeric default 0,status text default 'Aberto',paid_date text,created_by text,created_at timestamptz default now());
create table if not exists action_plan (id text primary key,priority text,area text,action text,responsible text,due_date text,status text default 'Pendente',created_by text,created_at timestamptz default now());
create table if not exists advisor_history (id text primary key,asked_at text,question text,answer text,created_by text);
create table if not exists dre_records (id text primary key,period_start text,period_end text,receita_bruta numeric default 0,deducoes_impostos numeric default 0,receita_liquida numeric default 0,custos_produtos_servicos numeric default 0,lucro_bruto numeric default 0,despesas_operacionais numeric default 0,resultados_financeiros numeric default 0,ebitda numeric default 0,lucro_operacional numeric default 0,lucro_liquido numeric default 0,notes text,created_by text,created_at timestamptz default now());
create table if not exists calendar_events (id text primary key,event_date text,event_time text,title text,category text,level text,color text,notes text,created_by text,created_at timestamptz default now());
create table if not exists mvp_feedback (id text primary key,feedback_date text,person text,profile text,score int default 0,main_pain text,liked text,missing text,objection text,status text,created_by text,created_at timestamptz default now());
create table if not exists executive_routines (id text primary key,routine_date text,routine_type text,score int default 0,focus text,decisions text,risks text,next_actions text,created_by text,created_at timestamptz default now());
create table if not exists decision_log (id text primary key,decision_date text,area text,decision text,reason text,expected_result text,owner text,due_date text,status text,created_by text,created_at timestamptz default now());

create index if not exists idx_cash_date on cash_flow(date);
create index if not exists idx_acc_kind on accounts(kind, status);
create index if not exists idx_acc_due on accounts(due_date);
create index if not exists idx_actions_status on action_plan(status);
create index if not exists idx_dre_period on dre_records(period_start, period_end);
create index if not exists idx_calendar_date on calendar_events(event_date);
create index if not exists idx_feedback_date on mvp_feedback(feedback_date);
create index if not exists idx_routine_date on executive_routines(routine_date);
create index if not exists idx_decision_date on decision_log(decision_date);

create table if not exists marketing_playbook (id text primary key,created_at timestamptz default now(),segment text,ideal_customer text,main_pain text,promise text,offer text,proof text,objections text,channels text,next_test text,created_by text);
create table if not exists unit_economics (id text primary key,created_at timestamptz default now(),ticket_medio numeric default 0,margem_contribuicao numeric default 0,cac numeric default 0,compras_ano numeric default 1,retencao_meses numeric default 12,churn_mensal numeric default 0,created_by text);
create table if not exists okr_records (id text primary key,created_at timestamptz default now(),quarter text,objective text,key_result text,target text,current_value text,confidence int default 5,owner text,due_date text,status text,created_by text);
create index if not exists idx_marketing_created on marketing_playbook(created_at);
create index if not exists idx_unit_created on unit_economics(created_at);
create index if not exists idx_okr_due on okr_records(due_date,status);
