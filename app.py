
from __future__ import annotations
import calendar as pycal, datetime as dt, hashlib, hmac, sqlite3, uuid
from typing import Any, Dict, Optional, Tuple
import pandas as pd
import streamlit as st
try:
    from supabase import create_client
except Exception:
    create_client = None

APP_NAME="Gestão Executiva EXECUTA Web"
APP_VERSION="MVP 10 usuários v2"
MAX_USERS=10
DATE_DB="%Y-%m-%d"
DATE_BR="%d/%m/%Y"

st.set_page_config(page_title=APP_NAME,page_icon="⚡",layout="wide",initial_sidebar_state="expanded")
st.markdown("""
<style>
.stApp{background:radial-gradient(circle at 20% 0%,rgba(0,209,255,.11),transparent 28%),radial-gradient(circle at 88% 12%,rgba(124,92,255,.13),transparent 26%),linear-gradient(180deg,#070A12 0%,#0B101B 100%);color:#EEF6FF}
[data-testid="stSidebar"]{background:linear-gradient(180deg,#0A0F1A 0%,#111827 100%);border-right:1px solid rgba(0,209,255,.18)}
.main-header{padding:20px 24px;border:1px solid rgba(0,209,255,.20);background:linear-gradient(135deg,rgba(16,23,37,.96),rgba(20,30,46,.80));border-radius:24px;margin-bottom:18px;box-shadow:0 0 35px rgba(0,209,255,.07)}
.main-title{font-size:31px;font-weight:850;color:#EEF6FF;margin:0}.main-subtitle{color:#8EA4BC;font-size:14px;margin-top:5px}
.metric-card{padding:18px;border-radius:20px;background:linear-gradient(145deg,rgba(16,23,37,.94),rgba(20,30,46,.82));border:1px solid rgba(255,255,255,.08);min-height:116px}
.metric-label{color:#8EA4BC;font-size:13px;margin-bottom:6px}.metric-value{color:#EEF6FF;font-size:25px;font-weight:820;margin-bottom:4px}.metric-status{color:#00D1FF;font-size:12px}
.user-pill{padding:10px 12px;border-radius:16px;background:rgba(0,209,255,.08);border:1px solid rgba(0,209,255,.18);margin-bottom:10px}
.stButton>button{border-radius:14px;border:1px solid rgba(0,209,255,.26);background:linear-gradient(135deg,rgba(0,209,255,.14),rgba(124,92,255,.10));color:#EEF6FF;font-weight:700}
.calendar-day{min-height:92px;padding:8px;border-radius:14px;background:rgba(16,23,37,.78);border:1px solid rgba(255,255,255,.08)}
.calendar-date{font-weight:800;color:#EEF6FF;margin-bottom:6px}.event-chip{display:inline-block;padding:3px 7px;border-radius:999px;margin:2px 3px 2px 0;font-size:11px;color:#06101A;font-weight:800}
</style>""",unsafe_allow_html=True)

EXECUTA_FRENTES=[("Diagnóstico executivo","Medir caixa, margem, estoque, canais, equipe, riscos e oportunidades antes de decidir."),("Validação de mercado","Testar demanda antes de investir pesado."),("Engenharia financeira","Controlar caixa, margem, capital de giro, preço e dívida."),("Sistema comercial","Transformar venda em processo previsível."),("Operação e escala","Padronizar atendimento, entrega, compras, estoque e treinamento."),("Tecnologia e dados","Reduzir erro, economizar tempo e integrar dados."),("Cultura e governança","Reduzir dependência do fundador e formar líderes.")]
PILARES=["Verdade financeira","Cliente no centro","Venda como sistema","Operação replicável","Tecnologia útil","Gente forte","Cultura com consequência","Escala com caixa","Marca com narrativa","Governança para durar"]

def secret(n,d=""):
    try:return st.secrets.get(n,d)
    except Exception:return d
def norm_url(u): return (u or "").strip().strip('"').strip("'").replace("/rest/v1/","").replace("/rest/v1","").rstrip("/")
def today_db(): return dt.date.today().strftime(DATE_DB)
def date_br(v):
    if not v:return ""
    if isinstance(v,dt.date):return v.strftime(DATE_BR)
    t=str(v).strip()
    for f in (DATE_DB,DATE_BR):
        try:return dt.datetime.strptime(t[:10],f).strftime(DATE_BR)
        except Exception:pass
    return t
def parse_money(v):
    if v is None:return 0.0
    if isinstance(v,(int,float)):return float(v)
    t=str(v).strip().replace("R$","").replace(" ","")
    if "," in t:t=t.replace(".","").replace(",",".")
    try:return float(t or 0)
    except Exception:return 0.0
def brl(v): return f"R$ {parse_money(v):,.2f}".replace(",","X").replace(".",",").replace("X",".")
def pct(v):
    try: return f"{float(v or 0):.0f}%"
    except Exception: return "0%"
def money_input(label,value=0,key=None):
    raw=st.text_input(label,value=("" if value in (None,"") else brl(value).replace("R$ ","")),key=key,placeholder="Ex.: 50.000,00")
    val=parse_money(raw)
    if raw: st.caption(f"Valor interpretado: {brl(val)}")
    return val
def header(t,s=""): st.markdown(f'<div class="main-header"><div class="main-title">{t}</div><div class="main-subtitle">{s}</div></div>',unsafe_allow_html=True)
def metric(l,v,s=""): st.markdown(f'<div class="metric-card"><div class="metric-label">{l}</div><div class="metric-value">{v}</div><div class="metric-status">{s}</div></div>',unsafe_allow_html=True)
def hpw(pw,s=None):
    s=s or uuid.uuid4().hex
    return s,hashlib.pbkdf2_hmac("sha256",pw.encode(),s.encode(),120000).hex()
def cpw(pw,s,d):
    _,x=hpw(pw,s)
    return hmac.compare_digest(x,d)
def month_add(d,months):
    m=d.month-1+months;y=d.year+m//12;m=m%12+1;day=min(d.day,pycal.monthrange(y,m)[1])
    return dt.date(y,m,day)

class DB:
    def __init__(self):
        self.mode="sqlite"; self.sb=None
        url,key=norm_url(secret("SUPABASE_URL")),secret("SUPABASE_ANON_KEY")
        if url and key and create_client:
            try:self.sb=create_client(url,key);self.mode="supabase"
            except Exception:self.sb=None;self.mode="sqlite"
        if self.mode=="sqlite":
            self.conn=sqlite3.connect("gestao_executiva_web_mvp_v2.db",check_same_thread=False);self.conn.row_factory=sqlite3.Row;self.ensure()
    def ensure(self):
        cur=self.conn.cursor()
        cur.execute("create table if not exists app_users(id text primary key,name text,email text unique,password_salt text,password_hash text,role text,active int default 1,created_at text default current_timestamp)")
        cur.execute("create table if not exists company_profile(id text primary key,company_name text,owner_name text,segment text,business_size text,monthly_revenue real default 0,fixed_costs real default 0,variable_costs real default 0,stock_value real default 0,initial_cash real default 0,notes text,updated_at text)")
        cur.execute("create table if not exists cash_flow(id text primary key,date text,type text,category text,description text,amount real default 0,channel text,created_by text,created_at text default current_timestamp)")
        cur.execute("create table if not exists accounts(id text primary key,due_date text,kind text,supplier_client text,description text,amount real default 0,status text default 'Aberto',paid_date text,created_by text,created_at text default current_timestamp)")
        cur.execute("create table if not exists action_plan(id text primary key,priority text,area text,action text,responsible text,due_date text,status text default 'Pendente',created_by text,created_at text default current_timestamp)")
        cur.execute("create table if not exists advisor_history(id text primary key,asked_at text,question text,answer text,created_by text)")
        cur.execute("create table if not exists dre_records(id text primary key,period_start text,period_end text,receita_bruta real default 0,deducoes_impostos real default 0,receita_liquida real default 0,custos_produtos_servicos real default 0,lucro_bruto real default 0,despesas_operacionais real default 0,resultados_financeiros real default 0,ebitda real default 0,lucro_operacional real default 0,lucro_liquido real default 0,notes text,created_by text,created_at text default current_timestamp)")
        cur.execute("create table if not exists calendar_events(id text primary key,event_date text,event_time text,title text,category text,level text,color text,notes text,created_by text,created_at text default current_timestamp)")
        self.conn.commit()
    def select(self,t,filters=None,order=None,desc=False,limit=None):
        filters=filters or {}
        if self.mode=="supabase":
            q=self.sb.table(t).select("*")
            for k,v in filters.items(): q=q.eq(k,v)
            if order:q=q.order(order,desc=desc)
            if limit:q=q.limit(limit)
            return list(q.execute().data or [])
        sql=f"select * from {t}";vals=[]
        if filters: sql+=" where "+" and ".join([f"{k}=?" for k in filters]); vals=list(filters.values())
        if order: sql+=f" order by {order} {'desc' if desc else 'asc'}"
        if limit: sql+=f" limit {int(limit)}"
        return [dict(r) for r in self.conn.execute(sql,vals).fetchall()]
    def insert(self,t,d):
        if self.mode=="supabase": return self.sb.table(t).insert(d).execute()
        ks=list(d.keys()); self.conn.execute(f"insert into {t} ({','.join(ks)}) values ({','.join(['?']*len(ks))})",[d[k] for k in ks]); self.conn.commit()
    def update(self,t,row_id,d):
        if self.mode=="supabase": return self.sb.table(t).update(d).eq("id",row_id).execute()
        ks=list(d.keys()); self.conn.execute(f"update {t} set {','.join([k+'=?' for k in ks])} where id=?",[d[k] for k in ks]+[row_id]); self.conn.commit()
    def delete(self,t,row_id):
        if self.mode=="supabase": return self.sb.table(t).delete().eq("id",row_id).execute()
        self.conn.execute(f"delete from {t} where id=?",(row_id,)); self.conn.commit()
    def count(self,t):
        if self.mode=="supabase": return len(self.sb.table(t).select("id").execute().data or [])
        return int(self.conn.execute(f"select count(*) from {t}").fetchone()[0])
@st.cache_resource
def get_db(): return DB()
db=get_db()

def role(): return st.session_state.get("user",{}).get("role","usuario")
def is_admin(): return role()=="administrador"
def can_edit(): return role() in ["administrador","usuario"]
def readonly_warning():
    if not can_edit(): st.info("Seu perfil é somente leitura. Você pode visualizar, mas não pode cadastrar, editar ou apagar.")
def user_name(): return st.session_state.get("user",{}).get("name","Usuário")

def create_user(name,email,pw,role_value="usuario"):
    if db.count("app_users")>=MAX_USERS:return False,f"Limite de {MAX_USERS} usuários atingido."
    email=email.strip().lower()
    if not name or not email or len(pw)<6:return False,"Preencha nome, e-mail e senha com no mínimo 6 caracteres."
    if db.select("app_users",{"email":email}):return False,"E-mail já cadastrado."
    s,d=hpw(pw);db.insert("app_users",dict(id=str(uuid.uuid4()),name=name,email=email,password_salt=s,password_hash=d,role=role_value,active=1))
    return True,"Usuário criado."
def login_user(email,pw):
    us=db.select("app_users",{"email":email.strip().lower()})
    if not us:return None,"Usuário não encontrado."
    u=us[0]
    if int(u.get("active",1))!=1:return None,"Usuário inativo."
    if not cpw(pw,u["password_salt"],u["password_hash"]):return None,"Senha incorreta."
    return u,"OK"
def login_screen():
    header(APP_NAME,f"{APP_VERSION} • teste gratuito com até {MAX_USERS} usuários.")
    c1,c2=st.columns(2,gap="large")
    with c1:
        st.subheader("Entrar")
        with st.form("login"):
            email=st.text_input("E-mail");pw=st.text_input("Senha",type="password");ok=st.form_submit_button("Entrar")
        if ok:
            u,msg=login_user(email,pw)
            if u: st.session_state.user=u; st.rerun()
            else: st.error(msg)
        st.info(f"Banco atual: **{db.mode.upper()}**.")
    with c2:
        st.subheader("Criar usuário de teste")
        st.caption(f"Usuários: {db.count('app_users')}/{MAX_USERS}")
        with st.form("signup"):
            code=st.text_input("Código de criação",type="password");name=st.text_input("Nome");email2=st.text_input("E-mail");pw2=st.text_input("Senha",type="password");rv=st.selectbox("Perfil",["administrador","usuario","somente leitura"]);sub=st.form_submit_button("Criar usuário")
        if sub:
            if code!=secret("SETUP_CODE","executa2026"):st.error("Código de criação incorreto.")
            else:
                ok,msg=create_user(name,email2,pw2,rv); st.success(msg) if ok else st.error(msg)

def ensure_profile():
    r=db.select("company_profile",limit=1)
    if r:return r[0]
    row=dict(id="main",company_name="",owner_name="",segment="",business_size="Pequena",monthly_revenue=0,fixed_costs=0,variable_costs=0,stock_value=0,initial_cash=0,notes="",updated_at=today_db())
    db.insert("company_profile",row);return row
def df_table(t,order=None,desc=False): return pd.DataFrame(db.select(t,order=order,desc=desc))
def cash_df():
    df=df_table("cash_flow","date",True)
    if df.empty:return pd.DataFrame(columns=["id","date","type","category","description","amount","channel","created_by"])
    df["amount"]=pd.to_numeric(df["amount"],errors="coerce").fillna(0);return df
def accounts_df():
    df=df_table("accounts","due_date")
    if df.empty:return pd.DataFrame(columns=["id","due_date","kind","supplier_client","description","amount","status","paid_date","created_by"])
    df["amount"]=pd.to_numeric(df["amount"],errors="coerce").fillna(0);return df
def actions_df():
    df=df_table("action_plan","due_date")
    if df.empty:return pd.DataFrame(columns=["id","priority","area","action","responsible","due_date","status","created_by"])
    return df
def dre_df():
    df=df_table("dre_records","period_end",True)
    if df.empty:return pd.DataFrame(columns=["id","period_start","period_end","receita_bruta","deducoes_impostos","receita_liquida","custos_produtos_servicos","lucro_bruto","despesas_operacionais","resultados_financeiros","ebitda","lucro_operacional","lucro_liquido","notes","created_by"])
    for c in ["receita_bruta","deducoes_impostos","receita_liquida","custos_produtos_servicos","lucro_bruto","despesas_operacionais","resultados_financeiros","ebitda","lucro_operacional","lucro_liquido"]:
        df[c]=pd.to_numeric(df[c],errors="coerce").fillna(0)
    return df
def events_df():
    df=df_table("calendar_events","event_date")
    if df.empty:return pd.DataFrame(columns=["id","event_date","event_time","title","category","level","color","notes","created_by"])
    return df
def latest_dre():
    r=db.select("dre_records",order="period_end",desc=True,limit=1)
    return r[0] if r else {}
def calc():
    p=ensure_profile();cash=cash_df();acc=accounts_df()
    entradas=float(cash.loc[cash.type=="Entrada","amount"].sum()) if not cash.empty else 0
    saidas=float(cash.loc[cash.type=="Saída","amount"].sum()) if not cash.empty else 0
    pagar=float(acc.loc[(acc.kind=="Pagar")&(~acc.status.isin(["Pago"])),"amount"].sum()) if not acc.empty else 0
    receber=float(acc.loc[(acc.kind=="Receber")&(~acc.status.isin(["Recebido"])),"amount"].sum()) if not acc.empty else 0
    dre=latest_dre();receita=float(dre.get("receita_bruta") or p.get("monthly_revenue") or entradas or 0)
    lucro=float(dre.get("lucro_liquido") or 0);fix=float(p.get("fixed_costs") or 0);var=float(p.get("variable_costs") or 0);estoque=float(p.get("stock_value") or 0)
    caixa=float(p.get("initial_cash") or 0)+entradas-saidas;resultado=lucro if dre else receita-fix-var
    margem=resultado/receita*100 if receita else 0
    receita_liq=float(dre.get("receita_liquida") or receita);custos=float(dre.get("custos_produtos_servicos") or var);mc=((receita_liq-custos)/receita_liq) if receita_liq else 0
    ponto=fix/mc if mc>0 else 0;ncg=receber+estoque-pagar
    return dict(caixa=caixa,entradas=entradas,saidas=saidas,pagar=pagar,receber=receber,receita=receita,receita_liquida=receita_liq,fixed=fix,variable=var,estoque=estoque,resultado=resultado,margem=margem,ponto_equilibrio=ponto,ncg=ncg)
def alertas():
    m=calc();s=100;als=[]
    if m["caixa"]<0:s-=25;als.append(("Crítico","Caixa negativo","Proteger caixa imediatamente, revisar pagamentos e acelerar recebíveis."))
    elif m["caixa"]<m["fixed"]*.5:s-=12;als.append(("Atenção","Caixa baixo em relação ao custo fixo","Evite novas despesas e revise contas a vencer."))
    if m["margem"]<0:s-=25;als.append(("Crítico","Resultado operacional negativo","Revisar preços, custos e despesas antes de crescer."))
    elif m["margem"]<10:s-=12;als.append(("Atenção","Margem líquida baixa","Analisar produtos/canais com baixa margem."))
    if m["pagar"]>m["receber"]+m["caixa"]:s-=18;als.append(("Crítico","Contas a pagar superam caixa + recebíveis","Renegociar prazos e priorizar pagamentos essenciais."))
    if m["ncg"]>max(1,m["receita"]):s-=12;als.append(("Atenção","Capital de giro necessário alto","Reduzir estoque parado e acelerar recebimentos."))
    if actions_df().empty:s-=8;als.append(("Atenção","Plano de ação ainda não estruturado","Criar 3 ações prioritárias com responsável e prazo."))
    return max(0,min(100,int(s))),als
def sidebar():
    u=st.session_state.user
    st.sidebar.markdown(f'<div class="user-pill">👤 <b>{u["name"]}</b><br>{u.get("role","usuario")}</div>',unsafe_allow_html=True)
    pages=["Minha Empresa","Painel","Alerta","Fluxo de Caixa","Contas a Pagar","Contas a Receber","DRE","Plano de Ação","Calendário","Método EXECUTA","Conselheiro EXECUTA"]
    if is_admin():pages.append("Usuários")
    page=st.sidebar.radio("Módulos",pages)
    st.sidebar.markdown("<br><br><br><br>",unsafe_allow_html=True)
    if st.sidebar.button("Sair"): st.session_state.clear(); st.rerun()
    return page
def select_record(df,lab,key):
    opts=[(lab(r),r.get("id")) for _,r in df.iterrows()]
    return st.selectbox("Selecionar registro",opts,format_func=lambda x:x[0],key=key) if opts else None

def page_minha_empresa():
    p=ensure_profile();header("Minha Empresa","Cadastro da empresa e leitura geral da saúde empresarial com base no DRE.");readonly_warning()
    if can_edit():
        with st.form("empresa_form"):
            c1,c2=st.columns(2)
            with c1:
                company=st.text_input("Nome da empresa",p.get("company_name",""));owner=st.text_input("Responsável",p.get("owner_name",""));segment=st.text_input("Segmento",p.get("segment",""));size=st.selectbox("Porte",["Pequena","Média","Grande","Hiperporte"],index=["Pequena","Média","Grande","Hiperporte"].index(p.get("business_size","Pequena")) if p.get("business_size","Pequena") in ["Pequena","Média","Grande","Hiperporte"] else 0)
            with c2:
                revenue=money_input("Faturamento mensal estimado",p.get("monthly_revenue"),"emp_revenue");fixed=money_input("Custos fixos mensais",p.get("fixed_costs"),"emp_fixed");variable=money_input("Custos variáveis mensais",p.get("variable_costs"),"emp_variable");stock=money_input("Valor em estoque",p.get("stock_value"),"emp_stock");initial=money_input("Caixa inicial",p.get("initial_cash"),"emp_initial")
            notes=st.text_area("Observações",p.get("notes",""))
            if st.form_submit_button("Salvar Minha Empresa"):
                db.update("company_profile","main",dict(company_name=company,owner_name=owner,segment=segment,business_size=size,monthly_revenue=revenue,fixed_costs=fixed,variable_costs=variable,stock_value=stock,initial_cash=initial,notes=notes,updated_at=today_db()));st.success("Minha Empresa salva.");st.rerun()
    st.subheader("Leitura rápida da saúde da empresa");m=calc();s,als=alertas();c=st.columns(4)
    with c[0]:metric("Score EXECUTA",f"{s}/100","Com base nos dados atuais")
    with c[1]:metric("Receita bruta",brl(m["receita"]),"DRE ou estimativa")
    with c[2]:metric("Lucro/resultado",brl(m["resultado"]),f"Margem {pct(m['margem'])}")
    with c[3]:metric("Caixa atual",brl(m["caixa"]),"Caixa inicial + movimentos")
    dre=latest_dre()
    st.info(f"Último DRE considerado: {date_br(dre.get('period_start'))} a {date_br(dre.get('period_end'))}.") if dre else st.warning("Ainda não há DRE lançado. A leitura usa estimativas do cadastro da empresa.")
def page_painel():
    header("Painel Executivo","Visão geral. Os alertas detalhados agora ficam no módulo Alerta.");m=calc();s,_=alertas();c=st.columns(4)
    with c[0]:metric("Score EXECUTA",f"{s}/100","Saúde geral")
    with c[1]:metric("Caixa atual",brl(m["caixa"]),"Entradas - saídas")
    with c[2]:metric("Capital de giro",brl(m["ncg"]),"Receber + estoque - pagar")
    with c[3]:metric("Resultado",brl(m["resultado"]),f"Margem {pct(m['margem'])}")
    st.subheader("Resumo financeiro");c1,c2=st.columns(2)
    with c1:metric("Contas a pagar em aberto",brl(m["pagar"]))
    with c2:metric("Contas a receber em aberto",brl(m["receber"]))
    st.subheader("Movimentos recentes");df=cash_df()
    if df.empty:st.info("Sem movimentos de caixa.")
    else:
        show=df.head(12).copy();show["date"]=show.date.apply(date_br);show["amount"]=show.amount.apply(brl);st.dataframe(show[["date","type","category","description","amount","channel","created_by"]],use_container_width=True,hide_index=True)
def page_alerta():
    header("Alerta","Riscos e prioridades que antes apareciam no Painel agora ficam centralizados aqui.");s,als=alertas();metric("Score EXECUTA",f"{s}/100","Quanto menor, maior a urgência")
    if not als:st.success("Nenhum alerta crítico identificado no momento.");return
    for n,t,a in als:
        (st.error if n=="Crítico" else st.warning)(f"**{n}: {t}** — {a}")
def page_fluxo():
    header("Fluxo de Caixa","Lançar entradas/saídas, parcelas e controlar histórico financeiro.");readonly_warning()
    if can_edit():
        with st.form("cash_form",clear_on_submit=True):
            st.subheader("Novo lançamento");c1,c2,c3=st.columns(3)
            with c1:date=st.date_input("Data inicial",value=dt.date.today(),format="DD/MM/YYYY");typ=st.selectbox("Tipo",["Entrada","Saída"]);mode=st.selectbox("Situação",["Realizado no caixa","Conta futura/agendada"])
            with c2:cat=st.text_input("Categoria");amount=money_input("Valor total",0,"fluxo_amount");parcelas=st.number_input("Parcelas",min_value=1,max_value=60,value=1,step=1)
            with c3:channel=st.text_input("Canal/Origem");desc=st.text_input("Descrição");split=st.checkbox("Dividir valor igualmente nas parcelas",value=True)
            if st.form_submit_button("Adicionar"):
                pv=amount/parcelas if split and parcelas else amount
                for i in range(int(parcelas)):
                    d=month_add(date,i);desc_i=f"{desc} ({i+1}/{parcelas})" if parcelas>1 else desc
                    if mode=="Realizado no caixa":db.insert("cash_flow",dict(id=str(uuid.uuid4()),date=d.strftime(DATE_DB),type=typ,category=cat,description=desc_i,amount=pv,channel=channel,created_by=user_name()))
                    else:db.insert("accounts",dict(id=str(uuid.uuid4()),due_date=d.strftime(DATE_DB),kind="Receber" if typ=="Entrada" else "Pagar",supplier_client=channel,description=desc_i,amount=pv,status="Aberto",paid_date="",created_by=user_name()))
                st.success("Lançamento adicionado e formulário limpo.");st.rerun()
    st.subheader("Entradas e saídas lançadas");df=cash_df()
    if df.empty:st.info("Sem lançamentos no caixa.")
    else:
        show=df.copy();show["date"]=show.date.apply(date_br);show["amount"]=show.amount.apply(brl);st.dataframe(show[["date","type","category","description","amount","channel","created_by"]],use_container_width=True,hide_index=True)
        if can_edit():
            st.subheader("Editar ou apagar lançamento");sel=select_record(df,lambda r:f"{date_br(r.get('date'))} | {r.get('type')} | {r.get('category')} | {brl(r.get('amount'))} | {r.get('description') or ''}","cash_edit")
            if sel:
                rec=df[df.id==sel[1]].iloc[0].to_dict()
                with st.form("edit_cash"):
                    c1,c2,c3=st.columns(3)
                    with c1:e_date=st.date_input("Data",value=dt.datetime.strptime(rec["date"][:10],DATE_DB).date(),format="DD/MM/YYYY");e_type=st.selectbox("Tipo",["Entrada","Saída"],index=0 if rec["type"]=="Entrada" else 1)
                    with c2:e_cat=st.text_input("Categoria",rec.get("category",""));e_amount=money_input("Valor",rec.get("amount",0),"edit_cash_amount")
                    with c3:e_channel=st.text_input("Canal/Origem",rec.get("channel",""));e_desc=st.text_input("Descrição",rec.get("description",""))
                    a,b=st.columns(2);save=a.form_submit_button("Salvar edição");delete=b.form_submit_button("Apagar lançamento")
                if save:db.update("cash_flow",rec["id"],dict(date=e_date.strftime(DATE_DB),type=e_type,category=e_cat,description=e_desc,amount=e_amount,channel=e_channel));st.success("Lançamento editado.");st.rerun()
                if delete:db.delete("cash_flow",rec["id"]);st.success("Lançamento apagado.");st.rerun()
    st.subheader("Histórico de contas pagas e recebidas");acc=accounts_df()
    if acc.empty:st.info("Sem contas baixadas ainda.")
    else:
        hist=acc[acc.status.isin(["Pago","Recebido"])].copy()
        if hist.empty:st.info("Ainda não há contas pagas ou recebidas.")
        else:
            hist["due_date"]=hist.due_date.apply(date_br);hist["paid_date"]=hist.paid_date.apply(date_br);hist["amount"]=hist.amount.apply(brl);st.dataframe(hist[["paid_date","kind","supplier_client","description","amount","status","created_by"]],use_container_width=True,hide_index=True)
def page_accounts(kind):
    title="Contas a Pagar" if kind=="Pagar" else "Contas a Receber";closed="Pago" if kind=="Pagar" else "Recebido";header(title,"Visualizar, editar, apagar e baixar contas. Novos lançamentos são criados pelo Fluxo de Caixa.");readonly_warning()
    df=accounts_df();df=df[df.kind==kind] if not df.empty else df;open_df=df[~df.status.isin([closed])] if not df.empty else df;closed_df=df[df.status.isin([closed])] if not df.empty else df
    st.subheader("Em aberto")
    if open_df.empty:st.info("Nenhuma conta em aberto.")
    else:
        show=open_df.copy();show["due_date"]=show.due_date.apply(date_br);show["amount"]=show.amount.apply(brl);st.dataframe(show[["due_date","supplier_client","description","amount","status","created_by"]],use_container_width=True,hide_index=True)
    if can_edit() and not df.empty:
        st.subheader("Editar, apagar ou baixar conta");sel=select_record(df,lambda r:f"{date_br(r.get('due_date'))} | {r.get('supplier_client')} | {brl(r.get('amount'))} | {r.get('description') or ''}",f"acc_{kind}")
        if sel:
            rec=df[df.id==sel[1]].iloc[0].to_dict()
            with st.form(f"edit_acc_{kind}"):
                c1,c2,c3=st.columns(3)
                with c1:due=st.date_input("Vencimento",value=dt.datetime.strptime(rec["due_date"][:10],DATE_DB).date(),format="DD/MM/YYYY");person=st.text_input("Fornecedor/Cliente",rec.get("supplier_client",""))
                with c2:desc=st.text_input("Descrição",rec.get("description",""));amount=money_input("Valor",rec.get("amount",0),f"edit_amount_{kind}")
                with c3:opts=["Aberto","Pendente",closed];status=st.selectbox("Status",opts,index=opts.index(rec.get("status")) if rec.get("status") in opts else 0);paid=st.date_input("Data de baixa",value=dt.date.today(),format="DD/MM/YYYY")
                a,b,c=st.columns(3);save=a.form_submit_button("Salvar edição");delete=b.form_submit_button("Apagar conta");baixar=c.form_submit_button(f"Marcar como {closed}")
            if save:db.update("accounts",rec["id"],dict(due_date=due.strftime(DATE_DB),supplier_client=person,description=desc,amount=amount,status=status,paid_date=paid.strftime(DATE_DB) if status==closed else ""));st.success("Conta editada.");st.rerun()
            if delete:db.delete("accounts",rec["id"]);st.success("Conta apagada.");st.rerun()
            if baixar:
                db.update("accounts",rec["id"],dict(status=closed,paid_date=paid.strftime(DATE_DB)))
                db.insert("cash_flow",dict(id=str(uuid.uuid4()),date=paid.strftime(DATE_DB),type="Saída" if kind=="Pagar" else "Entrada",category=f"Conta {kind}",description=rec.get("description",""),amount=float(rec.get("amount") or 0),channel=rec.get("supplier_client",""),created_by=user_name()))
                st.success(f"Conta marcada como {closed} e lançada no Fluxo de Caixa.");st.rerun()
    st.subheader("Histórico: já pago/recebido")
    if closed_df.empty:st.info(f"Nenhum registro {closed.lower()} ainda.")
    else:
        show=closed_df.copy();show["due_date"]=show.due_date.apply(date_br);show["paid_date"]=show.paid_date.apply(date_br);show["amount"]=show.amount.apply(brl);st.dataframe(show[["paid_date","due_date","supplier_client","description","amount","status","created_by"]],use_container_width=True,hide_index=True)
def page_dre():
    header("DRE","Preencha e pesquise por período. Datas no padrão dd/mm/aaaa.");readonly_warning()
    if can_edit():
        with st.form("dre_form",clear_on_submit=True):
            st.subheader("Novo DRE");c0,c1,c2=st.columns(3)
            with c0:ps=st.date_input("Data inicial",value=dt.date.today().replace(day=1),format="DD/MM/YYYY");pe=st.date_input("Data final",value=dt.date.today(),format="DD/MM/YYYY")
            with c1:rb=money_input("Receita bruta",0,"dre_rb");ded=money_input("Deduções e impostos",0,"dre_ded");rl=money_input("Receita líquida",0,"dre_rl");cust=money_input("Custo dos produtos/serviços (CMV/CPV/CSP)",0,"dre_custos")
            with c2:lb=money_input("Lucro bruto",0,"dre_lb");desp=money_input("Despesas operacionais",0,"dre_desp");rf=money_input("Resultados financeiros",0,"dre_rf");eb=money_input("EBITDA",0,"dre_ebitda");lo=money_input("Lucro operacional",0,"dre_lo");ll=money_input("Lucro líquido",0,"dre_ll")
            notes=st.text_area("Observações")
            if st.form_submit_button("Salvar DRE"):
                if rl==0:rl=rb-ded
                if lb==0:lb=rl-cust
                if eb==0:eb=lb-desp
                if lo==0:lo=eb
                if ll==0:ll=lo+rf
                db.insert("dre_records",dict(id=str(uuid.uuid4()),period_start=ps.strftime(DATE_DB),period_end=pe.strftime(DATE_DB),receita_bruta=rb,deducoes_impostos=ded,receita_liquida=rl,custos_produtos_servicos=cust,lucro_bruto=lb,despesas_operacionais=desp,resultados_financeiros=rf,ebitda=eb,lucro_operacional=lo,lucro_liquido=ll,notes=notes,created_by=user_name()))
                st.success("DRE salvo.");st.rerun()
    st.subheader("Pesquisar por período");c1,c2=st.columns(2);start=c1.date_input("De",value=dt.date.today().replace(day=1),format="DD/MM/YYYY");end=c2.date_input("Até",value=dt.date.today(),format="DD/MM/YYYY")
    df=dre_df()
    if df.empty:st.info("Nenhum DRE lançado.");return
    filt=df[(df.period_start>=start.strftime(DATE_DB))&(df.period_end<=end.strftime(DATE_DB))].copy()
    if filt.empty:st.warning("Nenhum DRE encontrado no período selecionado.");filt=df.copy()
    cols=["receita_bruta","deducoes_impostos","receita_liquida","custos_produtos_servicos","lucro_bruto","despesas_operacionais","resultados_financeiros","ebitda","lucro_operacional","lucro_liquido"];tot=filt[cols].sum();c=st.columns(4)
    with c[0]:metric("Receita bruta",brl(tot["receita_bruta"]))
    with c[1]:metric("Receita líquida",brl(tot["receita_liquida"]))
    with c[2]:metric("EBITDA",brl(tot["ebitda"]))
    with c[3]:metric("Lucro líquido",brl(tot["lucro_liquido"]),f"Margem {pct((tot['lucro_liquido']/tot['receita_bruta']*100) if tot['receita_bruta'] else 0)}")
    show=filt.copy();show["period_start"]=show.period_start.apply(date_br);show["period_end"]=show.period_end.apply(date_br)
    for col in cols:show[col]=show[col].apply(brl)
    st.dataframe(show[["period_start","period_end"]+cols+["created_by"]],use_container_width=True,hide_index=True)
def page_actions():
    header("Plano de Ação","Decisão com responsável, prazo e execução.");readonly_warning()
    if can_edit():
        with st.form("action_form",clear_on_submit=True):
            c1,c2=st.columns(2)
            with c1:pr=st.selectbox("Prioridade",["Alta","Média","Baixa"]);area=st.selectbox("Área",["Financeiro","Comercial","Operação","Tecnologia","Pessoas","Governança","Cliente"]);resp=st.text_input("Responsável",user_name())
            with c2:due=st.date_input("Prazo",value=dt.date.today()+dt.timedelta(days=7),format="DD/MM/YYYY");status=st.selectbox("Status",["Pendente","Em andamento","Concluído"])
            action=st.text_area("Ação")
            if st.form_submit_button("Adicionar ação"):db.insert("action_plan",dict(id=str(uuid.uuid4()),priority=pr,area=area,action=action,responsible=resp,due_date=due.strftime(DATE_DB),status=status,created_by=user_name()));st.success("Ação criada.");st.rerun()
    df=actions_df()
    if df.empty:st.info("Nenhuma ação cadastrada.");return
    show=df.copy();show["due_date"]=show.due_date.apply(date_br);st.dataframe(show[["priority","area","action","responsible","due_date","status","created_by"]],use_container_width=True,hide_index=True)
def page_calendar():
    header("Calendário","Agenda com compromissos diários, categorias e níveis por cor.");readonly_warning();colors={"Baixa":"#29E6A7","Média":"#FFCC66","Alta":"#FF8A3D","Crítica":"#FF5C7A"}
    if can_edit():
        with st.form("event_form",clear_on_submit=True):
            c1,c2,c3=st.columns(3)
            with c1:ed=st.date_input("Data",value=dt.date.today(),format="DD/MM/YYYY");et=st.text_input("Horário",placeholder="Ex.: 14:30")
            with c2:title=st.text_input("Compromisso");cat=st.selectbox("Categoria",["Financeiro","Comercial","Operação","Reunião","Cliente","Pessoal","Outro"])
            with c3:level=st.selectbox("Nível",["Baixa","Média","Alta","Crítica"]);notes=st.text_input("Observações")
            if st.form_submit_button("Adicionar compromisso"):db.insert("calendar_events",dict(id=str(uuid.uuid4()),event_date=ed.strftime(DATE_DB),event_time=et,title=title,category=cat,level=level,color=colors[level],notes=notes,created_by=user_name()));st.success("Compromisso adicionado.");st.rerun()
    today=dt.date.today();c1,c2=st.columns(2);month=c1.selectbox("Mês",list(range(1,13)),index=today.month-1,format_func=lambda m:f"{m:02d}");year=c2.number_input("Ano",min_value=2020,max_value=2100,value=today.year,step=1)
    events=events_df();ms=dt.date(int(year),int(month),1);me=dt.date(int(year),int(month),pycal.monthrange(int(year),int(month))[1]);mev=events[(events.event_date>=ms.strftime(DATE_DB))&(events.event_date<=me.strftime(DATE_DB))] if not events.empty else events
    st.subheader("Calendário do mês");cal=pycal.Calendar(firstweekday=0)
    for week in cal.monthdatescalendar(int(year),int(month)):
        cols=st.columns(7)
        for i,d in enumerate(week):
            de=mev[mev.event_date==d.strftime(DATE_DB)] if not mev.empty else pd.DataFrame();mut="opacity:.35;" if d.month!=int(month) else "";chips=""
            if not de.empty:
                for _,ev in de.head(3).iterrows():chips+=f'<span class="event-chip" style="background:{ev.get("color") or "#00D1FF"}">{ev.get("event_time") or ""} {str(ev.get("title") or "")[:12]}</span>'
            cols[i].markdown(f'<div class="calendar-day" style="{mut}"><div class="calendar-date">{d.day}</div>{chips}</div>',unsafe_allow_html=True)
    st.subheader("Compromissos do mês")
    if mev.empty:st.info("Sem compromissos no mês.")
    else:
        show=mev.copy();show["event_date"]=show.event_date.apply(date_br);st.dataframe(show[["event_date","event_time","title","category","level","notes","created_by"]],use_container_width=True,hide_index=True)
def page_metodo():
    header("Método EXECUTA","Diagnóstico, decisão, execução, controle e melhoria contínua.");st.info("Princípio: a empresa só deve crescer quando prova ter margem, caixa, processo, demanda, liderança e capacidade operacional.")
    st.subheader("Sete frentes")
    for i,(t,d) in enumerate(EXECUTA_FRENTES,1):st.markdown(f"**{i}. {t}** — {d}")
    st.subheader("10 pilares");st.write(", ".join(PILARES))
def advisor_answer(q):
    m=calc();s,als=alertas();q=q.lower();temas=[]
    if any(x in q for x in ["caixa","dinheiro","capital","giro","pagar"]):temas.append("caixa")
    if any(x in q for x in ["margem","lucro","preço","markup"]):temas.append("margem")
    if any(x in q for x in ["venda","cliente","marketplace","canal","comercial"]):temas.append("comercial")
    if any(x in q for x in ["processo","estoque","operação","retrabalho"]):temas.append("operacao")
    if any(x in q for x in ["dono","equipe","liderança","delegar"]):temas.append("lideranca")
    if not temas:temas=["geral"]
    out=[f"## Diagnóstico EXECUTA\nScore atual: **{s}/100**.\n\nCaixa: **{brl(m['caixa'])}** | Resultado: **{brl(m['resultado'])}** | Margem: **{pct(m['margem'])}** | Capital de giro: **{brl(m['ncg'])}**"]
    if als:out.append("### Alertas\n"+"\n".join(f"- **{n}: {t}** — {a}" for n,t,a in als))
    out.append("## Decisão recomendada")
    if "caixa" in temas:out.append("- Proteger caixa: acelerar recebíveis, revisar contas a pagar, reduzir compras não essenciais, negociar prazos e controlar estoque parado.")
    if "margem" in temas:out.append("- Revisar margem: calcular custo real, taxas, impostos, frete, embalagem e aplicar markup por canal.")
    if "comercial" in temas:out.append("- Criar venda como sistema: medir canal por margem, criar base própria de clientes, follow-up e recompra.")
    if "operacao" in temas:out.append("- Padronizar operação: checklist, responsáveis, prazos, indicadores de erro, atraso e retrabalho.")
    if "lideranca" in temas:out.append("- Reduzir dependência do dono: responsáveis por área, indicadores, reunião semanal e delegação com acompanhamento.")
    if "geral" in temas:out.append("- Começar pelo diagnóstico: margem, caixa, processo, demanda, liderança e capacidade operacional.")
    out.append("## Plano de 7 dias\n1. Atualizar fluxo de caixa.\n2. Revisar contas a pagar/receber.\n3. Conferir DRE e capital de giro.\n4. Criar 3 ações com responsável e prazo.\n5. Fazer uma reunião EXECUTA curta.")
    return "\n\n".join(out)
def page_advisor():
    header("Conselheiro EXECUTA","Sem API: resposta por lógica interna com base no método e dados cadastrados.");q=st.text_area("Digite sua dúvida",placeholder="Ex.: Como aumentar meu caixa?",height=110)
    if st.button("Gerar orientação"):
        if not q.strip():st.error("Digite uma pergunta.")
        else:
            ans=advisor_answer(q);st.session_state.last_answer=ans;db.insert("advisor_history",dict(id=str(uuid.uuid4()),asked_at=dt.datetime.now().isoformat(timespec="seconds"),question=q,answer=ans,created_by=user_name()))
    if st.session_state.get("last_answer"):st.markdown(st.session_state.last_answer)
def page_users():
    header("Usuários",f"Somente administrador. Limite de {MAX_USERS} usuários.")
    if not is_admin():st.error("Você não tem permissão para acessar este módulo.");return
    users=db.select("app_users",order="created_at");st.write(f"Usuários cadastrados: **{len(users)}/{MAX_USERS}**")
    if users:st.dataframe(pd.DataFrame(users)[["name","email","role","active","created_at"]],use_container_width=True,hide_index=True)
    with st.form("newuser"):
        code=st.text_input("Código de criação",type="password");name=st.text_input("Nome");email=st.text_input("E-mail");pw=st.text_input("Senha",type="password");rv=st.selectbox("Perfil",["administrador","usuario","somente leitura"])
        if st.form_submit_button("Criar usuário"):
            if code!=secret("SETUP_CODE","executa2026"):st.error("Código incorreto.")
            else:
                ok,msg=create_user(name,email,pw,rv);st.success(msg) if ok else st.error(msg)
def main():
    if "user" not in st.session_state:login_screen();return
    page=sidebar()
    if page=="Minha Empresa":page_minha_empresa()
    elif page=="Painel":page_painel()
    elif page=="Alerta":page_alerta()
    elif page=="Fluxo de Caixa":page_fluxo()
    elif page=="Contas a Pagar":page_accounts("Pagar")
    elif page=="Contas a Receber":page_accounts("Receber")
    elif page=="DRE":page_dre()
    elif page=="Plano de Ação":page_actions()
    elif page=="Calendário":page_calendar()
    elif page=="Método EXECUTA":page_metodo()
    elif page=="Conselheiro EXECUTA":page_advisor()
    elif page=="Usuários":page_users()
main()
