
from __future__ import annotations
import uuid, hmac, hashlib, sqlite3, datetime as dt
from typing import Any, Dict, List, Tuple
import pandas as pd
import streamlit as st

try:
    from supabase import create_client
except Exception:
    create_client = None

APP_NAME = "Gestão Executiva EXECUTA Web"
APP_VERSION = "MVP 5 usuários v1"
MAX_USERS = 5
DATE_DB = "%Y-%m-%d"
DATE_BR = "%d/%m/%Y"

st.set_page_config(page_title=APP_NAME, page_icon="⚡", layout="wide", initial_sidebar_state="expanded")

st.markdown("""
<style>
.stApp {
  background: radial-gradient(circle at 20% 0%, rgba(0,209,255,.11), transparent 28%),
              radial-gradient(circle at 88% 12%, rgba(124,92,255,.13), transparent 26%),
              linear-gradient(180deg, #070A12 0%, #0B101B 100%);
  color: #EEF6FF;
}
[data-testid="stSidebar"] {
  background: linear-gradient(180deg, #0A0F1A 0%, #111827 100%);
  border-right: 1px solid rgba(0,209,255,.18);
}
.main-header {
  padding: 20px 24px; border: 1px solid rgba(0,209,255,.20);
  background: linear-gradient(135deg, rgba(16,23,37,.96), rgba(20,30,46,.80));
  border-radius: 24px; margin-bottom: 18px; box-shadow: 0 0 35px rgba(0,209,255,.07);
}
.main-title {font-size: 31px; font-weight: 850; color: #EEF6FF; margin:0;}
.main-subtitle {color:#8EA4BC; font-size:14px; margin-top:5px;}
.metric-card {
  padding: 18px; border-radius: 20px;
  background: linear-gradient(145deg, rgba(16,23,37,.94), rgba(20,30,46,.82));
  border: 1px solid rgba(255,255,255,.08); min-height:116px;
}
.metric-label {color:#8EA4BC; font-size:13px; margin-bottom:6px;}
.metric-value {color:#EEF6FF; font-size:25px; font-weight:820; margin-bottom:4px;}
.metric-status {color:#00D1FF; font-size:12px;}
.ok {color:#29E6A7; font-weight:800;} .warn {color:#FFCC66; font-weight:800;} .risk {color:#FF5C7A; font-weight:800;}
.user-pill {padding:10px 12px; border-radius:16px; background:rgba(0,209,255,.08); border:1px solid rgba(0,209,255,.18); margin-bottom:10px;}
.stButton > button {
  border-radius:14px; border:1px solid rgba(0,209,255,.26);
  background: linear-gradient(135deg, rgba(0,209,255,.14), rgba(124,92,255,.10));
  color:#EEF6FF; font-weight:700;
}
</style>
""", unsafe_allow_html=True)

EXECUTA_FRENTES = [
    ("Diagnóstico executivo", "Medir caixa, margem, estoque, canais, equipe, riscos e oportunidades antes de decidir."),
    ("Validação de mercado", "Testar demanda antes de investir pesado em produto, marketing, equipe ou expansão."),
    ("Engenharia financeira", "Controlar caixa, margem, capital de giro, ponto de equilíbrio, retirada, preço e dívida."),
    ("Sistema comercial", "Transformar venda em processo previsível: canais, conversão, recompra, CRM e proposta de valor."),
    ("Operação e escala", "Padronizar atendimento, entrega, compras, estoque, treinamento e processos antes de crescer."),
    ("Tecnologia e dados", "Usar tecnologia para reduzir erro, economizar tempo, integrar dados e melhorar decisões."),
    ("Cultura e governança", "Reduzir dependência do fundador, formar líderes, responsabilidades, rituais e indicadores."),
]
PILARES = ["Verdade financeira", "Cliente no centro", "Venda como sistema", "Operação replicável", "Tecnologia útil",
           "Gente forte", "Cultura com consequência", "Escala com caixa", "Marca com narrativa", "Governança para durar"]

def secret(name, default=""):
    try:
        return st.secrets.get(name, default)
    except Exception:
        return default

def today_db(): return dt.date.today().strftime(DATE_DB)
def date_br(v):
    if not v: return ""
    if isinstance(v, dt.date): return v.strftime(DATE_BR)
    for fmt in (DATE_DB, DATE_BR):
        try: return dt.datetime.strptime(str(v)[:10], fmt).strftime(DATE_BR)
        except Exception: pass
    return str(v)
def brl(v):
    try: val = float(v or 0)
    except Exception: val = 0
    return f"R$ {val:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
def pct(v):
    try: val = float(v or 0)
    except Exception: val = 0
    return f"{val:.1f}%".replace(".", ",")
def header(t, s=""):
    st.markdown(f'<div class="main-header"><div class="main-title">{t}</div><div class="main-subtitle">{s}</div></div>', unsafe_allow_html=True)
def metric(label, value, status=""):
    st.markdown(f'<div class="metric-card"><div class="metric-label">{label}</div><div class="metric-value">{value}</div><div class="metric-status">{status}</div></div>', unsafe_allow_html=True)
def hash_pw(pw, salt=None):
    salt = salt or uuid.uuid4().hex
    digest = hashlib.pbkdf2_hmac("sha256", pw.encode(), salt.encode(), 120000).hex()
    return salt, digest
def check_pw(pw, salt, digest):
    _, d = hash_pw(pw, salt)
    return hmac.compare_digest(d, digest)

class DB:
    def __init__(self):
        self.mode = "sqlite"
        self.sb = None
        url, key = secret("SUPABASE_URL"), secret("SUPABASE_ANON_KEY")
        if url and key and create_client:
            try:
                self.sb = create_client(url, key)
                self.mode = "supabase"
            except Exception:
                self.sb = None
        if self.mode == "sqlite":
            self.conn = sqlite3.connect("gestao_executiva_web_mvp.db", check_same_thread=False)
            self.conn.row_factory = sqlite3.Row
            self.ensure_sqlite()

    def ensure_sqlite(self):
        cur = self.conn.cursor()
        cur.execute("""create table if not exists app_users(
            id text primary key,name text,email text unique,password_salt text,password_hash text,role text,active int default 1,created_at text default current_timestamp)""")
        cur.execute("""create table if not exists company_profile(
            id text primary key,company_name text,owner_name text,segment text,business_size text,monthly_revenue real default 0,
            fixed_costs real default 0,variable_costs real default 0,stock_value real default 0,initial_cash real default 0,notes text,updated_at text)""")
        cur.execute("""create table if not exists cash_flow(
            id text primary key,date text,type text,category text,description text,amount real default 0,channel text,created_by text,created_at text default current_timestamp)""")
        cur.execute("""create table if not exists accounts(
            id text primary key,due_date text,kind text,supplier_client text,description text,amount real default 0,status text default 'Aberto',paid_date text,created_by text,created_at text default current_timestamp)""")
        cur.execute("""create table if not exists action_plan(
            id text primary key,priority text,area text,action text,responsible text,due_date text,status text default 'Pendente',created_by text,created_at text default current_timestamp)""")
        cur.execute("""create table if not exists advisor_history(id text primary key,asked_at text,question text,answer text,created_by text)""")
        cur.execute("create index if not exists idx_cash_date on cash_flow(date)")
        cur.execute("create index if not exists idx_acc_kind on accounts(kind,status)")
        cur.execute("create index if not exists idx_actions_status on action_plan(status)")
        self.conn.commit()

    def select(self, table, filters=None, order=None, desc=False, limit=None):
        filters = filters or {}
        if self.mode == "supabase":
            q = self.sb.table(table).select("*")
            for k, v in filters.items(): q = q.eq(k, v)
            if order: q = q.order(order, desc=desc)
            if limit: q = q.limit(limit)
            return list((q.execute().data) or [])
        sql = f"select * from {table}"
        vals = []
        if filters:
            sql += " where " + " and ".join([f"{k}=?" for k in filters.keys()])
            vals = list(filters.values())
        if order: sql += f" order by {order} {'desc' if desc else 'asc'}"
        if limit: sql += f" limit {int(limit)}"
        return [dict(r) for r in self.conn.execute(sql, vals).fetchall()]

    def insert(self, table, data):
        if self.mode == "supabase":
            return self.sb.table(table).insert(data).execute()
        keys = list(data.keys())
        self.conn.execute(f"insert into {table} ({','.join(keys)}) values ({','.join(['?']*len(keys))})", [data[k] for k in keys])
        self.conn.commit()

    def update(self, table, row_id, data):
        if self.mode == "supabase":
            return self.sb.table(table).update(data).eq("id", row_id).execute()
        keys = list(data.keys())
        self.conn.execute(f"update {table} set {','.join([k+'=?' for k in keys])} where id=?", [data[k] for k in keys] + [row_id])
        self.conn.commit()

    def count(self, table):
        if self.mode == "supabase":
            return len(self.sb.table(table).select("id").execute().data or [])
        return int(self.conn.execute(f"select count(*) from {table}").fetchone()[0])

@st.cache_resource
def get_db(): return DB()
db = get_db()

def ensure_profile():
    rows = db.select("company_profile", limit=1)
    if rows: return rows[0]
    row = dict(id="main", company_name="", owner_name="", segment="", business_size="Pequena",
               monthly_revenue=0, fixed_costs=0, variable_costs=0, stock_value=0, initial_cash=0, notes="", updated_at=today_db())
    db.insert("company_profile", row)
    return row

def create_user(name, email, pw, role="usuario"):
    if db.count("app_users") >= MAX_USERS: return False, f"Limite de {MAX_USERS} usuários atingido."
    email = email.strip().lower()
    if not name or not email or len(pw) < 6: return False, "Preencha nome, e-mail e senha com no mínimo 6 caracteres."
    if db.select("app_users", {"email": email}): return False, "E-mail já cadastrado."
    salt, digest = hash_pw(pw)
    db.insert("app_users", dict(id=str(uuid.uuid4()), name=name, email=email, password_salt=salt, password_hash=digest, role=role, active=1))
    return True, "Usuário criado."

def login_user(email, pw):
    users = db.select("app_users", {"email": email.strip().lower()})
    if not users: return None, "Usuário não encontrado."
    u = users[0]
    if int(u.get("active", 1)) != 1: return None, "Usuário inativo."
    if not check_pw(pw, u["password_salt"], u["password_hash"]): return None, "Senha incorreta."
    return u, "OK"

def login_screen():
    header(APP_NAME, f"{APP_VERSION} • teste gratuito com até {MAX_USERS} usuários.")
    c1, c2 = st.columns(2, gap="large")
    with c1:
        st.subheader("Entrar")
        with st.form("login"):
            email = st.text_input("E-mail")
            pw = st.text_input("Senha", type="password")
            ok = st.form_submit_button("Entrar")
        if ok:
            user, msg = login_user(email, pw)
            if user:
                st.session_state.user = user
                st.rerun()
            else:
                st.error(msg)
        st.info(f"Banco atual: **{db.mode.upper()}**. Para uso compartilhado real no Streamlit Cloud, configure Supabase.")
    with c2:
        st.subheader("Criar usuário de teste")
        st.caption(f"Usuários: {db.count('app_users')}/{MAX_USERS}")
        with st.form("signup"):
            code = st.text_input("Código de criação", type="password")
            name = st.text_input("Nome")
            email2 = st.text_input("E-mail")
            pw2 = st.text_input("Senha", type="password")
            role = st.selectbox("Perfil", ["administrador", "usuario", "somente leitura"])
            signup = st.form_submit_button("Criar usuário")
        if signup:
            if code != secret("SETUP_CODE", "executa2026"):
                st.error("Código de criação incorreto.")
            else:
                ok, msg = create_user(name, email2, pw2, role)
                st.success(msg) if ok else st.error(msg)

def cash_df():
    df = pd.DataFrame(db.select("cash_flow", order="date", desc=True))
    if df.empty: return pd.DataFrame(columns=["id","date","type","category","description","amount","channel","created_by"])
    df["amount"] = pd.to_numeric(df["amount"], errors="coerce").fillna(0)
    return df

def accounts_df():
    df = pd.DataFrame(db.select("accounts", order="due_date"))
    if df.empty: return pd.DataFrame(columns=["id","due_date","kind","supplier_client","description","amount","status","paid_date","created_by"])
    df["amount"] = pd.to_numeric(df["amount"], errors="coerce").fillna(0)
    return df

def actions_df():
    return pd.DataFrame(db.select("action_plan", order="due_date"))

def calc():
    p = ensure_profile()
    cash, acc = cash_df(), accounts_df()
    entradas = float(cash.loc[cash.type=="Entrada","amount"].sum()) if not cash.empty else 0
    saidas = float(cash.loc[cash.type=="Saída","amount"].sum()) if not cash.empty else 0
    pagar = float(acc.loc[(acc.kind=="Pagar") & (acc.status!="Pago"),"amount"].sum()) if not acc.empty else 0
    receber = float(acc.loc[(acc.kind=="Receber") & (acc.status!="Recebido"),"amount"].sum()) if not acc.empty else 0
    receita = float(p.get("monthly_revenue") or entradas or 0)
    fixo = float(p.get("fixed_costs") or 0); variavel = float(p.get("variable_costs") or 0); estoque = float(p.get("stock_value") or 0)
    caixa = float(p.get("initial_cash") or 0) + entradas - saidas
    resultado = receita - fixo - variavel
    margem = resultado / receita * 100 if receita else 0
    mc = (receita - variavel) / receita if receita else 0
    pe = fixo / mc if mc > 0 else 0
    ncg = receber + estoque - pagar
    return dict(caixa=caixa, entradas=entradas, saidas=saidas, pagar=pagar, receber=receber, receita=receita, fixo=fixo, variavel=variavel, estoque=estoque, resultado=resultado, margem=margem, ponto_equilibrio=pe, ncg=ncg)

def score():
    m = calc(); s = 100; alerts = []
    if m["caixa"] < 0: s -= 25; alerts.append("Caixa negativo.")
    elif m["caixa"] < m["fixo"] * .5: s -= 12; alerts.append("Caixa baixo em relação ao custo fixo.")
    if m["margem"] < 0: s -= 25; alerts.append("Resultado operacional negativo.")
    elif m["margem"] < 10: s -= 12; alerts.append("Margem baixa.")
    if m["pagar"] > m["receber"] + m["caixa"]: s -= 18; alerts.append("Contas a pagar superam caixa + recebíveis.")
    if m["ncg"] > max(1, m["receita"]): s -= 12; alerts.append("Capital de giro necessário alto.")
    if actions_df().empty: s -= 8; alerts.append("Plano de ação ainda não estruturado.")
    return max(0, min(100, int(s))), alerts

def user_name(): return st.session_state.user.get("name","Usuário")

def sidebar():
    u = st.session_state.user
    st.sidebar.markdown(f'<div class="user-pill">👤 <b>{u["name"]}</b><br>{u.get("role","usuario")}</div>', unsafe_allow_html=True)
    if st.sidebar.button("Sair"):
        st.session_state.clear(); st.rerun()
    return st.sidebar.radio("Módulos", ["Painel","Diagnóstico","Fluxo de Caixa","Contas a Pagar","Contas a Receber","DRE","Capital de Giro","Plano de Ação","Método EXECUTA","Conselheiro EXECUTA","Usuários"])

def page_painel():
    header("Painel Executivo", "Saúde da empresa, score EXECUTA e prioridades.")
    m = calc(); s, alerts = score()
    c = st.columns(4)
    with c[0]: metric("Score EXECUTA", f"{s}/100", "Saudável" if s>=75 else "Atenção" if s>=50 else "Risco")
    with c[1]: metric("Caixa atual", brl(m["caixa"]), "Entradas - saídas")
    with c[2]: metric("Resultado", brl(m["resultado"]), f"Margem {pct(m['margem'])}")
    with c[3]: metric("Capital de giro", brl(m["ncg"]), "Receber + estoque - pagar")
    st.subheader("Alertas")
    if alerts:
        for a in alerts: st.warning(a)
    else: st.success("Nenhum alerta crítico.")
    st.subheader("Movimento recente")
    df = cash_df()
    if not df.empty:
        show = df.head(10).copy(); show["date"] = show.date.apply(date_br); show["amount"] = show.amount.apply(brl)
        st.dataframe(show[["date","type","category","description","amount","channel","created_by"]], use_container_width=True, hide_index=True)
    else: st.info("Sem lançamentos.")

def page_diagnostico():
    p = ensure_profile()
    header("Diagnóstico", "Cadastro inicial da empresa e baseline financeiro.")
    with st.form("diag"):
        c1, c2 = st.columns(2)
        with c1:
            company = st.text_input("Nome da empresa", p.get("company_name",""))
            owner = st.text_input("Responsável", p.get("owner_name",""))
            segment = st.text_input("Segmento", p.get("segment",""))
            size = st.selectbox("Porte", ["Pequena","Média","Grande","Hiperporte"], index=["Pequena","Média","Grande","Hiperporte"].index(p.get("business_size","Pequena")) if p.get("business_size","Pequena") in ["Pequena","Média","Grande","Hiperporte"] else 0)
        with c2:
            revenue = st.number_input("Faturamento mensal estimado", min_value=0.0, value=float(p.get("monthly_revenue") or 0), step=100.0)
            fixed = st.number_input("Custos fixos mensais", min_value=0.0, value=float(p.get("fixed_costs") or 0), step=100.0)
            variable = st.number_input("Custos variáveis mensais", min_value=0.0, value=float(p.get("variable_costs") or 0), step=100.0)
            stock = st.number_input("Valor em estoque", min_value=0.0, value=float(p.get("stock_value") or 0), step=100.0)
            initial = st.number_input("Caixa inicial", value=float(p.get("initial_cash") or 0), step=100.0)
        notes = st.text_area("Observações", p.get("notes",""))
        if st.form_submit_button("Salvar"):
            db.update("company_profile","main",dict(company_name=company,owner_name=owner,segment=segment,business_size=size,monthly_revenue=revenue,fixed_costs=fixed,variable_costs=variable,stock_value=stock,initial_cash=initial,notes=notes,updated_at=today_db()))
            st.success("Diagnóstico salvo."); st.rerun()

def page_fluxo():
    header("Fluxo de Caixa", "Entradas e saídas reais de dinheiro.")
    with st.form("cash"):
        c1,c2,c3=st.columns(3)
        with c1: date=st.date_input("Data", format="DD/MM/YYYY"); typ=st.selectbox("Tipo",["Entrada","Saída"])
        with c2: cat=st.text_input("Categoria"); amount=st.number_input("Valor", min_value=0.0, step=10.0)
        with c3: channel=st.text_input("Canal"); desc=st.text_input("Descrição")
        if st.form_submit_button("Adicionar"):
            db.insert("cash_flow",dict(id=str(uuid.uuid4()),date=date.strftime(DATE_DB),type=typ,category=cat,description=desc,amount=amount,channel=channel,created_by=user_name()))
            st.success("Lançado."); st.rerun()
    df=cash_df()
    if not df.empty:
        show=df.copy(); show["date"]=show.date.apply(date_br); show["amount"]=show.amount.apply(brl)
        st.dataframe(show[["date","type","category","description","amount","channel","created_by"]], use_container_width=True, hide_index=True)

def page_accounts(kind):
    header("Contas a Pagar" if kind=="Pagar" else "Contas a Receber", "Controle de compromissos e recebíveis.")
    with st.form(f"acc_{kind}"):
        c1,c2,c3=st.columns(3)
        with c1: due=st.date_input("Vencimento", format="DD/MM/YYYY"); person=st.text_input("Fornecedor/Cliente")
        with c2: desc=st.text_input("Descrição"); amount=st.number_input("Valor", min_value=0.0, step=10.0)
        with c3:
            opts=["Aberto","Pendente","Pago"] if kind=="Pagar" else ["Aberto","Pendente","Recebido"]
            status=st.selectbox("Status",opts)
            paid=st.date_input("Data de baixa", format="DD/MM/YYYY")
        if st.form_submit_button("Adicionar"):
            db.insert("accounts",dict(id=str(uuid.uuid4()),due_date=due.strftime(DATE_DB),kind=kind,supplier_client=person,description=desc,amount=amount,status=status,paid_date=paid.strftime(DATE_DB) if status in ["Pago","Recebido"] else "",created_by=user_name()))
            if status in ["Pago","Recebido"]:
                db.insert("cash_flow",dict(id=str(uuid.uuid4()),date=paid.strftime(DATE_DB),type="Saída" if kind=="Pagar" else "Entrada",category=f"Conta {kind}",description=desc,amount=amount,channel=person,created_by=user_name()))
            st.success("Conta salva."); st.rerun()
    df=accounts_df(); df=df[df.kind==kind] if not df.empty else df
    if not df.empty:
        show=df.copy(); show["due_date"]=show.due_date.apply(date_br); show["paid_date"]=show.paid_date.apply(date_br); show["amount"]=show.amount.apply(brl)
        st.dataframe(show[["due_date","supplier_client","description","amount","status","paid_date","created_by"]], use_container_width=True, hide_index=True)

def page_dre():
    header("DRE Gerencial", "Resultado econômico simplificado.")
    m=calc()
    c=st.columns(3)
    with c[0]: metric("Receita", brl(m["receita"]), "Base mensal")
    with c[1]: metric("Resultado", brl(m["resultado"]), f"Margem {pct(m['margem'])}")
    with c[2]: metric("Ponto de equilíbrio", brl(m["ponto_equilibrio"]), "Faturamento mínimo")
    df=pd.DataFrame([["Receita",m["receita"]],["(-) Custos variáveis",-m["variavel"]],["(-) Custos fixos",-m["fixo"]],["Resultado operacional",m["resultado"]],["Margem líquida %",m["margem"]]], columns=["Linha","Valor"])
    df["Valor"]=df.apply(lambda r: pct(r["Valor"]) if "%" in r["Linha"] else brl(r["Valor"]), axis=1)
    st.dataframe(df, use_container_width=True, hide_index=True)

def page_capital():
    header("Capital de Giro", "Receber + estoque - pagar.")
    m=calc()
    c=st.columns(4)
    with c[0]: metric("A receber", brl(m["receber"]))
    with c[1]: metric("Estoque", brl(m["estoque"]))
    with c[2]: metric("A pagar", brl(m["pagar"]))
    with c[3]: metric("NCG", brl(m["ncg"]))
    st.latex(r"NCG = Contas\ a\ Receber + Estoque - Contas\ a\ Pagar")
    if m["ncg"] > m["receita"] and m["receita"]>0: st.error("Capital de giro alto. Crescer agora pode consumir caixa.")
    elif m["ncg"] > m["caixa"]: st.warning("NCG maior que o caixa atual.")
    else: st.success("Capital de giro parece controlado.")

def page_actions():
    header("Plano de Ação", "Decisão com responsável, prazo e execução.")
    with st.form("act"):
        c1,c2=st.columns(2)
        with c1: pr=st.selectbox("Prioridade",["Alta","Média","Baixa"]); area=st.selectbox("Área",["Financeiro","Comercial","Operação","Tecnologia","Pessoas","Governança","Cliente"]); resp=st.text_input("Responsável", user_name())
        with c2: due=st.date_input("Prazo", value=dt.date.today()+dt.timedelta(days=7), format="DD/MM/YYYY"); status=st.selectbox("Status",["Pendente","Em andamento","Concluído"])
        action=st.text_area("Ação")
        if st.form_submit_button("Adicionar"):
            db.insert("action_plan",dict(id=str(uuid.uuid4()),priority=pr,area=area,action=action,responsible=resp,due_date=due.strftime(DATE_DB),status=status,created_by=user_name()))
            st.success("Ação criada."); st.rerun()
    df=actions_df()
    if not df.empty:
        show=df.copy(); show["due_date"]=show.due_date.apply(date_br)
        st.dataframe(show[["priority","area","action","responsible","due_date","status","created_by"]], use_container_width=True, hide_index=True)

def page_metodo():
    header("Método EXECUTA", "Diagnóstico, decisão, execução, controle e melhoria contínua.")
    st.info("Princípio: a empresa só deve crescer quando prova ter margem, caixa, processo, demanda, liderança e capacidade operacional.")
    st.subheader("Sete frentes")
    for i,(t,d) in enumerate(EXECUTA_FRENTES,1): st.markdown(f"**{i}. {t}** — {d}")
    st.subheader("10 pilares")
    st.write(", ".join(PILARES))
    st.subheader("Roadmap")
    st.dataframe(pd.DataFrame([
        ["1. Diagnóstico","Entender realidade","Caixa, margem, canais, estoque, equipe e gargalos"],
        ["2. Correção","Eliminar perdas","Preço, desperdícios, prazos, estoque e processos"],
        ["3. Estruturação","Criar base","DRE, fluxo, CRM, indicadores, reuniões e processos"],
        ["4. Crescimento","Escalar o que funciona","Ofertas, canais, ROI, recompras e automação"],
        ["5. Governança","Preparar para durar","Líderes, rituais, cultura, riscos e sucessão"],
    ], columns=["Fase","Objetivo","Ações"]), use_container_width=True, hide_index=True)

def advisor_answer(q):
    m=calc(); s, alerts=score(); q=q.lower()
    temas=[]
    if any(x in q for x in ["caixa","dinheiro","capital","giro","pagar"]): temas.append("caixa")
    if any(x in q for x in ["margem","lucro","preço","markup"]): temas.append("margem")
    if any(x in q for x in ["venda","cliente","marketplace","canal","comercial"]): temas.append("comercial")
    if any(x in q for x in ["processo","estoque","operação","retrabalho"]): temas.append("operacao")
    if any(x in q for x in ["dono","equipe","liderança","delegar"]): temas.append("lideranca")
    if not temas: temas=["geral"]
    out=[f"## Diagnóstico EXECUTA\nScore atual: **{s}/100**.\n\nCaixa: **{brl(m['caixa'])}** | Resultado: **{brl(m['resultado'])}** | Margem: **{pct(m['margem'])}** | NCG: **{brl(m['ncg'])}**"]
    if alerts: out.append("### Alertas\n" + "\n".join(f"- {a}" for a in alerts))
    out.append("## Decisão recomendada")
    if "caixa" in temas: out.append("- Proteger caixa: acelerar recebíveis, revisar contas a pagar, reduzir compras não essenciais, negociar prazos e controlar estoque parado.")
    if "margem" in temas: out.append("- Revisar margem: calcular custo real, taxas, impostos, frete, embalagem e aplicar markup por canal.")
    if "comercial" in temas: out.append("- Criar venda como sistema: medir canal por margem, criar base própria de clientes, follow-up e recompra.")
    if "operacao" in temas: out.append("- Padronizar operação: checklist, responsáveis, prazos, indicadores de erro, atraso e retrabalho.")
    if "lideranca" in temas: out.append("- Reduzir dependência do dono: responsáveis por área, indicadores, reunião semanal e delegação com acompanhamento.")
    if "geral" in temas: out.append("- Começar pelo diagnóstico: margem, caixa, processo, demanda, liderança e capacidade operacional.")
    out.append("## Plano de 7 dias\n1. Atualizar fluxo de caixa.\n2. Revisar contas a pagar/receber.\n3. Conferir DRE e capital de giro.\n4. Criar 3 ações com responsável e prazo.\n5. Fazer uma reunião EXECUTA curta.")
    return "\n\n".join(out)

def page_advisor():
    header("Conselheiro EXECUTA", "Sem API: resposta por lógica interna com base no método e dados cadastrados.")
    q=st.text_area("Digite sua dúvida", placeholder="Ex.: Como aumentar meu caixa?", height=110)
    if st.button("Gerar orientação"):
        if not q.strip(): st.error("Digite uma pergunta.")
        else:
            ans=advisor_answer(q)
            st.session_state.last_answer=ans
            db.insert("advisor_history",dict(id=str(uuid.uuid4()),asked_at=dt.datetime.now().isoformat(timespec="seconds"),question=q,answer=ans,created_by=user_name()))
    if st.session_state.get("last_answer"): st.markdown(st.session_state.last_answer)

def page_users():
    header("Usuários", f"Limite de {MAX_USERS} usuários para teste.")
    users=db.select("app_users", order="created_at")
    st.write(f"Usuários cadastrados: **{len(users)}/{MAX_USERS}**")
    if users: st.dataframe(pd.DataFrame(users)[["name","email","role","active","created_at"]], use_container_width=True, hide_index=True)
    with st.form("newuser"):
        code=st.text_input("Código de criação", type="password"); name=st.text_input("Nome"); email=st.text_input("E-mail"); pw=st.text_input("Senha", type="password"); role=st.selectbox("Perfil",["administrador","usuario","somente leitura"])
        if st.form_submit_button("Criar usuário"):
            if code != secret("SETUP_CODE","executa2026"): st.error("Código incorreto.")
            else:
                ok,msg=create_user(name,email,pw,role); st.success(msg) if ok else st.error(msg)

def main():
    if "user" not in st.session_state:
        login_screen(); return
    page=sidebar()
    if page=="Painel": page_painel()
    elif page=="Diagnóstico": page_diagnostico()
    elif page=="Fluxo de Caixa": page_fluxo()
    elif page=="Contas a Pagar": page_accounts("Pagar")
    elif page=="Contas a Receber": page_accounts("Receber")
    elif page=="DRE": page_dre()
    elif page=="Capital de Giro": page_capital()
    elif page=="Plano de Ação": page_actions()
    elif page=="Método EXECUTA": page_metodo()
    elif page=="Conselheiro EXECUTA": page_advisor()
    elif page=="Usuários": page_users()

main()
