
from __future__ import annotations
import calendar as pycal, datetime as dt, hashlib, hmac, sqlite3, uuid, html as _html
from typing import Any, Dict, Optional, Tuple
import pandas as pd
import streamlit as st
try:
    from supabase import create_client
except Exception:
    create_client = None

APP_NAME="Gestão Executiva EXECUTA — Executive OS"
APP_VERSION="v7.1 MULTIEMPRESA PERMISSÕES"
MAX_USERS=10
DATE_DB="%Y-%m-%d"
DATE_BR="%d/%m/%Y"

DEFAULT_COMPANY_ID = "default-company"

TENANT_TABLES = {
    "company_profile",
    "cash_flow",
    "accounts",
    "action_plan",
    "advisor_history",
    "dre_records",
    "calendar_events",
    "mvp_feedback",
    "executive_routines",
    "decision_log",
    "marketing_playbook",
    "unit_economics",
    "okr_records",
}

def has_logged_user():
    return "user" in st.session_state and bool(st.session_state.get("user"))

def current_company_id():
    user = st.session_state.get("user", {}) if "st" in globals() else {}
    return user.get("company_id") or DEFAULT_COMPANY_ID

def current_company_name():
    user = st.session_state.get("user", {}) if "st" in globals() else {}
    return user.get("company_name") or "Empresa atual"

def is_company_table(table_name):
    return table_name in TENANT_TABLES


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

/* Sidebar profissional */
[data-testid="stSidebar"] div[role="radiogroup"] label {
  min-height: 44px !important;
  padding: 8px 12px !important;
  border-radius: 14px !important;
  margin: 4px 0 !important;
  border: 1px solid rgba(255,255,255,.06);
  background: rgba(255,255,255,.025);
}
[data-testid="stSidebar"] div[role="radiogroup"] label:hover {
  border-color: rgba(0,209,255,.35);
  background: rgba(0,209,255,.08);
}
[data-testid="stSidebar"] div[role="radiogroup"] label p {
  font-size: 15px !important;
  font-weight: 760 !important;
}
.topbar {
  display:flex; align-items:center; justify-content:space-between; gap:12px;
  padding: 10px 14px; margin-bottom: 12px;
  border: 1px solid rgba(0,209,255,.16); border-radius: 18px;
  background: rgba(16,23,37,.62);
}
.topbar-title {color:#8EA4BC;font-size:13px;font-weight:700}
.pro-badge {color:#06101A;background:#00D1FF;padding:4px 9px;border-radius:999px;font-size:11px;font-weight:900}
.exec-note {padding: 14px 16px; border-radius: 18px; border: 1px solid rgba(0,209,255,.18); background: rgba(0,209,255,.07); margin-bottom: 10px;}


/* EXECUTA Pro v4 - refinamento de produto */
[data-testid="stSidebar"] section {overflow-y: visible !important;}
[data-testid="stSidebar"] div[role="radiogroup"] label {
  min-height: 52px !important;
  padding: 11px 14px !important;
  border-radius: 16px !important;
  margin: 6px 0 !important;
}
[data-testid="stSidebar"] div[role="radiogroup"] label p {font-size: 16px !important; letter-spacing:.1px;}
.insight-card{padding:16px 18px;border-radius:22px;background:linear-gradient(135deg,rgba(0,209,255,.08),rgba(124,92,255,.08));border:1px solid rgba(0,209,255,.18);margin-bottom:12px;}
.insight-title{font-size:16px;font-weight:850;color:#EEF6FF;margin-bottom:5px}.insight-text{font-size:13px;color:#AFC0D2;line-height:1.45}
.section-kicker{color:#00D1FF;font-size:12px;font-weight:900;letter-spacing:.12em;text-transform:uppercase;margin-bottom:6px}
.badge-ok{display:inline-block;padding:4px 9px;border-radius:999px;background:rgba(41,230,167,.13);color:#29E6A7;border:1px solid rgba(41,230,167,.22);font-weight:800;font-size:12px}
.badge-warn{display:inline-block;padding:4px 9px;border-radius:999px;background:rgba(255,204,102,.13);color:#FFCC66;border:1px solid rgba(255,204,102,.22);font-weight:800;font-size:12px}
.badge-risk{display:inline-block;padding:4px 9px;border-radius:999px;background:rgba(255,92,122,.13);color:#FF5C7A;border:1px solid rgba(255,92,122,.22);font-weight:800;font-size:12px}
.exec-table-note{font-size:12px;color:#8EA4BC;margin-top:-8px;margin-bottom:12px}


.ceo-grid-card{padding:18px 20px;border-radius:24px;background:linear-gradient(145deg,rgba(16,23,37,.96),rgba(9,15,25,.82));border:1px solid rgba(0,209,255,.16);min-height:150px;box-shadow:0 12px 32px rgba(0,0,0,.22)}
.ceo-card-title{font-size:15px;font-weight:900;color:#EEF6FF;margin-bottom:8px}.ceo-card-text{font-size:13px;color:#AFC0D2;line-height:1.45}
.ceo-question{padding:10px 12px;border-left:3px solid #00D1FF;background:rgba(0,209,255,.055);border-radius:10px;margin:7px 0;color:#DDEBFA}


/* Experience OS v6 — UX profissional e consultivo */
:root{
  --exec-bg:#070A12; --exec-surface:#101725; --exec-surface-2:#131B2B;
  --exec-primary:#00D1FF; --exec-violet:#7C5CFF; --exec-green:#29E6A7;
  --exec-yellow:#FFCC66; --exec-red:#FF5C7A; --exec-text:#EEF6FF; --exec-muted:#AFC0D2;
}
.block-container{padding-top:1.25rem; padding-bottom:2rem; max-width:1500px;}
.main-header{border-radius:28px!important; padding:24px 28px!important; background:linear-gradient(135deg,rgba(16,23,37,.98),rgba(10,15,25,.92))!important;}
.main-title{font-size:34px!important; letter-spacing:-.035em!important;}
.main-subtitle{font-size:15px!important; line-height:1.55!important; max-width:980px;}
[data-testid="stSidebar"]{min-width:310px!important;}
[data-testid="stSidebar"] div[role="radiogroup"] label{min-height:48px!important; padding:10px 14px!important; border-radius:17px!important; margin:5px 0!important;}
[data-testid="stSidebar"] div[role="radiogroup"] label p{font-size:15.5px!important; font-weight:760!important;}
.stTabs [data-baseweb="tab-list"]{gap:8px;background:rgba(16,23,37,.55);border:1px solid rgba(255,255,255,.07);border-radius:18px;padding:6px;}
.stTabs [data-baseweb="tab"]{border-radius:14px; padding:8px 12px; font-weight:800;}
.exec-hero{padding:22px 24px;border-radius:26px;border:1px solid rgba(0,209,255,.20);background:radial-gradient(circle at 5% 10%,rgba(0,209,255,.16),transparent 36%),linear-gradient(135deg,rgba(19,27,43,.96),rgba(10,15,25,.94));box-shadow:0 20px 50px rgba(0,0,0,.28);margin-bottom:16px;}
.exec-hero h3{margin:0;color:#EEF6FF;font-size:22px;letter-spacing:-.02em}.exec-hero p{color:#AFC0D2;margin:8px 0 0 0;line-height:1.5;font-size:14px;}
.ux-card{padding:18px 20px;border-radius:24px;background:linear-gradient(145deg,rgba(16,23,37,.96),rgba(11,17,29,.88));border:1px solid rgba(255,255,255,.08);box-shadow:0 14px 36px rgba(0,0,0,.22);margin-bottom:12px;min-height:132px;}
.ux-card-title{font-weight:900;font-size:16px;color:#EEF6FF;margin-bottom:8px}.ux-card-text{font-size:13px;color:#AFC0D2;line-height:1.48}.ux-card-action{font-size:12px;color:#00D1FF;font-weight:900;margin-top:10px;}
.help-badge{display:inline-flex;align-items:center;justify-content:center;width:18px;height:18px;border-radius:999px;background:rgba(0,209,255,.14);border:1px solid rgba(0,209,255,.32);color:#00D1FF;font-size:12px;font-weight:900;margin-right:6px;}
.tooltip-box{padding:12px 14px;border-radius:16px;background:rgba(0,209,255,.07);border:1px solid rgba(0,209,255,.16);color:#AFC0D2;font-size:13px;line-height:1.45;margin:8px 0 12px 0;}
.step-row{display:flex;gap:12px;align-items:flex-start;padding:13px 15px;border-radius:18px;background:rgba(255,255,255,.035);border:1px solid rgba(255,255,255,.07);margin:8px 0;}
.step-num{flex:0 0 auto;width:28px;height:28px;border-radius:999px;background:linear-gradient(135deg,#00D1FF,#7C5CFF);color:#07101B;font-weight:950;display:flex;align-items:center;justify-content:center;font-size:13px;}
.step-title{color:#EEF6FF;font-weight:900}.step-desc{color:#AFC0D2;font-size:13px;line-height:1.45;margin-top:3px}.step-status{margin-left:auto;font-size:12px;font-weight:900;padding:4px 8px;border-radius:999px;}
.status-done{background:rgba(41,230,167,.12);color:#29E6A7;border:1px solid rgba(41,230,167,.25)}.status-open{background:rgba(255,204,102,.11);color:#FFCC66;border:1px solid rgba(255,204,102,.25)}
.strategy-lane{padding:15px;border-radius:20px;border:1px solid rgba(255,255,255,.08);background:rgba(16,23,37,.82);margin-bottom:10px}.lane-head{display:flex;justify-content:space-between;gap:10px;align-items:center}.lane-title{font-size:15px;font-weight:900;color:#EEF6FF}.lane-score{font-size:13px;font-weight:950;color:#00D1FF}.lane-body{color:#AFC0D2;font-size:13px;line-height:1.45;margin-top:8px}.lane-action{color:#29E6A7;font-weight:850;font-size:12px;margin-top:8px}
.small-help{font-size:12px;color:#8EA4BC;line-height:1.4;margin-top:-2px;margin-bottom:8px}

/* v6.3 — interrogação visível e layout estável */
.visible-q{display:inline-flex;align-items:center;justify-content:center;width:18px;height:18px;line-height:18px;border-radius:999px;margin-left:7px;vertical-align:super;transform:translateY(-2px);background:rgba(0,209,255,.14);border:1px solid rgba(0,209,255,.34);color:#00D1FF;font-size:11px;font-weight:950;cursor:help;box-shadow:0 0 0 3px rgba(0,209,255,.04);}
.visible-q:hover{background:rgba(0,209,255,.24);border-color:rgba(0,209,255,.62);}
.help-subtitle{font-size:21px;font-weight:900;color:#EEF6FF;margin:22px 0 8px 0;letter-spacing:-.015em;}
.metric-label .visible-q{width:16px;height:16px;font-size:10px;margin-left:5px;}
.top-method-btn div[data-testid="stButton"] > button{min-height:34px!important;padding:6px 10px!important;border-radius:999px!important;font-size:12.5px!important;white-space:normal!important;line-height:1.15!important;background:linear-gradient(135deg,rgba(0,209,255,.20),rgba(124,92,255,.13))!important;}
.clean-note{padding:12px 14px;border-radius:16px;background:rgba(0,209,255,.06);border:1px solid rgba(0,209,255,.14);color:#AFC0D2;font-size:13px;line-height:1.45;margin-bottom:12px;}

</style>""",unsafe_allow_html=True)



# Refinamento v6.1 — menos topo cortado, menu mais limpo e hierarquia melhor
st.markdown("""
<style>
.block-container{padding-top:.45rem!important; padding-bottom:1.25rem!important;}
.main-header{padding:16px 20px!important; border-radius:22px!important; margin:0 0 12px 0!important;}
.main-title{font-size:28px!important; line-height:1.08!important;}
.main-subtitle{font-size:13.5px!important; line-height:1.35!important; max-height:none!important; overflow:visible!important;}
.topbar{padding:6px 8px!important; margin-bottom:8px!important; background:transparent!important; border:none!important; justify-content:flex-end!important;}
[data-testid="stSidebar"]{min-width:300px!important; overflow:visible!important;}
[data-testid="stSidebar"] section{overflow:visible!important;}
[data-testid="stSidebar"] div[role="radiogroup"]{gap:3px!important;}
[data-testid="stSidebar"] div[role="radiogroup"] label{min-height:42px!important; padding:8px 12px!important; margin:3px 0!important; border-radius:15px!important;}
[data-testid="stSidebar"] div[role="radiogroup"] label p{font-size:14.5px!important; font-weight:780!important;}
.solution-card{padding:14px 16px;border-radius:18px;background:rgba(41,230,167,.07);border:1px solid rgba(41,230,167,.18);margin:8px 0 14px 0;color:#DDEBFA;}
.solution-title{font-weight:900;color:#29E6A7;margin-bottom:6px}.solution-card li{margin-bottom:4px;}
.ceo-panel-card{padding:16px 18px;border-radius:22px;background:linear-gradient(135deg,rgba(0,209,255,.08),rgba(124,92,255,.08));border:1px solid rgba(0,209,255,.18);margin-bottom:12px;}
.calendar-dot{display:inline-block;width:9px;height:9px;border-radius:999px;margin-right:5px;vertical-align:middle;}
</style>
""", unsafe_allow_html=True)


# Refinamento final v6.4 — Executive OS
st.markdown("""
<style>
/* Base premium, mais limpa e menos carregada */
.block-container{padding-top:.65rem!important;max-width:1440px!important;}
.stApp{background:
  radial-gradient(circle at 14% 0%,rgba(0,209,255,.10),transparent 30%),
  radial-gradient(circle at 92% 8%,rgba(124,92,255,.12),transparent 26%),
  linear-gradient(180deg,#070A12 0%,#090E18 100%)!important;
}
.main-header{
  border:1px solid rgba(0,209,255,.18)!important;
  background:linear-gradient(135deg,rgba(18,27,43,.98),rgba(9,14,24,.96))!important;
  box-shadow:0 18px 48px rgba(0,0,0,.26), inset 0 1px 0 rgba(255,255,255,.04)!important;
}
.main-title{font-size:29px!important;letter-spacing:-.03em!important;}
.main-subtitle{color:#AFC0D2!important;max-width:1060px!important;}
.metric-card{
  min-height:124px!important;
  border-radius:24px!important;
  background:linear-gradient(145deg,rgba(17,25,39,.98),rgba(11,17,29,.94))!important;
  border:1px solid rgba(255,255,255,.075)!important;
  box-shadow:0 16px 42px rgba(0,0,0,.22)!important;
}
.metric-value{font-size:27px!important;letter-spacing:-.025em!important;}
.metric-status{font-size:12.5px!important;color:#59DFFF!important;}
[data-testid="stSidebar"]{
  background:linear-gradient(180deg,#090E18 0%,#0E1624 100%)!important;
  border-right:1px solid rgba(0,209,255,.16)!important;
}
[data-testid="stSidebar"] div[role="radiogroup"] label{
  min-height:45px!important;
  border-radius:16px!important;
  border:1px solid rgba(255,255,255,.065)!important;
  background:rgba(255,255,255,.025)!important;
}
[data-testid="stSidebar"] div[role="radiogroup"] label:hover{
  background:rgba(0,209,255,.08)!important;
  border-color:rgba(0,209,255,.35)!important;
}
.user-pill{
  border-radius:22px!important;
  padding:16px!important;
  background:linear-gradient(135deg,rgba(0,209,255,.10),rgba(124,92,255,.08))!important;
}
.top-method-btn div[data-testid="stButton"] > button{
  min-height:34px!important;
  border-radius:999px!important;
  font-size:12px!important;
  font-weight:900!important;
  letter-spacing:.01em!important;
}
.exec-briefing{
  padding:18px 20px;border-radius:24px;
  border:1px solid rgba(0,209,255,.18);
  background:linear-gradient(135deg,rgba(0,209,255,.075),rgba(124,92,255,.065));
  box-shadow:0 18px 45px rgba(0,0,0,.22);
  margin:12px 0 14px 0;
}
.exec-briefing-title{font-size:17px;font-weight:950;color:#EEF6FF;margin-bottom:6px;}
.exec-briefing-text{font-size:14px;line-height:1.52;color:#C6D6E8;}
.exec-decision-card{
  padding:17px 18px;border-radius:22px;margin-bottom:12px;
  border:1px solid rgba(255,255,255,.08);
  background:linear-gradient(145deg,rgba(17,25,39,.96),rgba(10,16,28,.92));
}
.exec-decision-title{font-size:14px;font-weight:950;color:#00D1FF;text-transform:uppercase;letter-spacing:.08em;margin-bottom:7px;}
.exec-decision-text{font-size:13.5px;line-height:1.5;color:#D8E6F5;}
.exec-principle{
  padding:14px 16px;border-radius:18px;margin:10px 0 14px 0;
  border:1px solid rgba(41,230,167,.18);
  background:rgba(41,230,167,.065);
  color:#DDEBFA;font-size:13.5px;line-height:1.52;
}
.exec-warning{
  padding:14px 16px;border-radius:18px;margin:10px 0 14px 0;
  border:1px solid rgba(255,204,102,.22);
  background:rgba(255,204,102,.075);
  color:#F4E8C8;font-size:13.5px;line-height:1.52;
}
.help-subtitle{
  margin-top:14px!important;
  margin-bottom:8px!important;
  font-size:18px!important;
  font-weight:950!important;
  color:#EEF6FF!important;
  letter-spacing:-.02em!important;
}
.visible-q{
  width:17px!important;height:17px!important;
  background:rgba(0,209,255,.16)!important;
  color:#4EE6FF!important;
}
.stDataFrame{border-radius:18px!important;overflow:hidden!important;}
div[data-testid="stForm"]{
  border:1px solid rgba(255,255,255,.075)!important;
  background:rgba(16,23,37,.38)!important;
  border-radius:22px!important;
  padding:14px!important;
}
</style>
""", unsafe_allow_html=True)

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
def money_input(label,value=0,key=None,help_text=""):
    raw=st.text_input(label,value=("" if value in (None,"") else brl(value).replace("R$ ","")),key=key,placeholder="Ex.: 50.000,00",help=help_text or None)
    val=parse_money(raw)
    if raw: st.caption(f"Valor interpretado: {brl(val)}")
    return val

HELP_TEXTS={
    "Minha Empresa":"Cadastro principal da empresa. Aqui entram os dados-base usados para interpretar caixa, custos, estoque, porte e saúde geral. Exemplo: preencha faturamento, custos fixos, custos variáveis, estoque e caixa inicial com valores reais ou estimados.",
    "Painel":"Sala de comando do empreendedor. Não é apenas um resumo: é a tela que interpreta os números, aponta risco, recomenda decisão e transforma gestão em ação.",
    "Fluxo de Caixa":"Registra dinheiro que entrou ou saiu. Use para acompanhar caixa real, lançamentos parcelados e histórico financeiro.",
    "Contas a Pagar":"Lista de compromissos financeiros futuros da empresa. Exemplo: fornecedores, aluguel, impostos, folha, cartão e parcelas.",
    "Contas a Receber":"Lista de valores que a empresa tem a receber. Exemplo: vendas a prazo, marketplaces, boletos, clientes e recebíveis futuros.",
    "DRE":"Demonstração do Resultado do Exercício. Mostra se a empresa está dando lucro ou prejuízo, separando receita, impostos, custos e despesas.",
    "Calendário":"Agenda executiva e financeira. Mostra compromissos e também vencimentos de contas a pagar e a receber.",
    "Relatórios":"Consolidação executiva para revisão semanal ou mensal. Une saúde financeira, mapa de crescimento, alertas, plano de ação e leitura do próximo movimento.",
    "Plano de Ação":"Transforma conselho em execução. Cada ação precisa ter prioridade, área, responsável, prazo e status; caso contrário, vira intenção sem resultado.",
    "Alertas":"Mostra riscos e pontos de atenção. Cada alerta vem acompanhado do que fazer para corrigir o problema.",
    "Usuários":"Área administrativa para controlar acessos. Deve ser usada apenas pelo administrador.",
    "Score EXECUTA":"Nota geral calculada a partir de caixa, margem, contas, execução e riscos. Quanto maior, mais saudável está a empresa.",
    "Caixa atual":"Estimativa do dinheiro disponível considerando caixa inicial, entradas e saídas registradas.",
    "Capital de giro":"Dinheiro necessário para manter a empresa funcionando entre pagar fornecedores, manter estoque e receber dos clientes.",
    "Resultado":"Diferença entre receitas, custos e despesas. Ajuda a ver se a empresa está gerando lucro ou consumindo caixa.",
    "Receita bruta":"Tudo que a empresa vendeu antes de descontar impostos, devoluções, taxas e custos. Exemplo: vendeu R$ 50.000,00 no mês, coloque 50.000,00.",
    "Deduções e impostos":"Descontos sobre a receita: impostos, devoluções, cancelamentos, taxas obrigatórias ou abatimentos.",
    "Receita líquida":"Receita que sobra depois das deduções e impostos. Fórmula comum: receita bruta menos deduções e impostos.",
    "Custo dos produtos/serviços (CMV/CPV/CSP)":"Custo direto para entregar o que foi vendido. Exemplo: mercadoria, embalagem, frete de compra, insumos ou custo direto do serviço.",
    "Lucro bruto":"Receita líquida menos custo direto. Mostra se o produto/serviço vendido tem margem antes das despesas da operação.",
    "Despesas operacionais":"Gastos para manter a empresa funcionando: aluguel, salários administrativos, marketing, sistemas, energia, contador e estrutura.",
    "EBITDA":"Resultado operacional antes de juros, impostos, depreciação e amortização. Ajuda a ver a força operacional do negócio.",
    "Lucro líquido":"Resultado final depois de receitas, custos, despesas e efeitos financeiros. É o lucro real do período.",
    "Nome da empresa":"Nome comercial ou razão social da empresa. Exemplo: Livraria Alfa Ltda.",
    "Responsável":"Pessoa principal que administra ou acompanha este sistema. Exemplo: proprietário, gerente ou diretor financeiro.",
    "Segmento":"Área de atuação da empresa. Exemplo: livros, comércio, serviços, alimentação, marketplace, indústria.",
    "Porte":"Tamanho operacional da empresa. Use pequena, média, grande ou hiperporte conforme faturamento, equipe e complexidade.",
    "Faturamento mensal estimado":"Quanto a empresa vende em média por mês antes dos descontos. Exemplo: 80.000,00.",
    "Custos fixos mensais":"Gastos que aparecem mesmo se vender pouco: aluguel, salários fixos, sistemas, contador, internet, energia mínima.",
    "Custos variáveis mensais":"Gastos que crescem quando a empresa vende mais: mercadoria, comissão, embalagem, taxas, frete, insumos.",
    "Valor em estoque":"Valor aproximado parado em produtos/mercadorias. Estoque alto demais pode consumir caixa.",
    "Caixa inicial":"Dinheiro disponível no início do controle. Exemplo: saldo bancário + dinheiro em caixa.",
    "Novo lançamento":"Use para registrar entrada ou saída de dinheiro. Se for conta futura, o sistema envia para contas a pagar ou receber.",
    "Entradas e saídas lançadas":"Histórico do que já entrou ou saiu do caixa. Clique na linha para editar ou excluir.",
    "Histórico de contas pagas e recebidas":"Mostra contas que já foram baixadas. Serve para conferir o que virou caixa de fato.",
    "Leitura executiva":"Interpretação dos números em linguagem de gestão. Ajuda a decidir o que fazer, não apenas ver dados.",
    "Próximo movimento recomendado":"Ação prioritária sugerida para melhorar caixa, margem, execução ou crescimento.",
    "Prioridades da semana":"Ações mais importantes para os próximos dias. Use para não perder foco.",
    "Movimentos recentes":"Últimos lançamentos de caixa registrados no sistema.",
    "Mapa de Crescimento":"Leitura por frentes: financeiro, mercado, execução, operação e liderança. Mostra onde agir primeiro.",
    "Relatório Executivo":"Texto consolidado para revisão da empresa, reunião semanal ou acompanhamento mensal.",
}

def _e(x): return _html.escape(str(x), quote=True)
def _help_for(label, fallback=""):
    txt=str(label or "").strip()
    if txt in HELP_TEXTS: return HELP_TEXTS[txt]
    low=txt.lower()
    for k,v in HELP_TEXTS.items():
        if k.lower() in low or low in k.lower(): return v
    return fallback or f"Explicação: {txt}. Use esta informação para interpretar, preencher corretamente e tomar decisão com menos dúvida."
def qmark(help_text): return f'<span class="visible-q" title="{_e(help_text)}">?</span>'
def header(t,s="",help_text=None):
    ht=help_text or _help_for(t,s)
    st.markdown(f'<div class="main-header"><div class="main-title">{_e(t)} {qmark(ht)}</div><div class="main-subtitle">{_e(s)}</div></div>',unsafe_allow_html=True)
def metric(l,v,s=""):
    ht=_help_for(l,s)
    st.markdown(f'<div class="metric-card"><div class="metric-label">{_e(l)} {qmark(ht)}</div><div class="metric-value">{_e(v)}</div><div class="metric-status">{_e(s)}</div></div>',unsafe_allow_html=True)

def help_title(text, help_text=None):
    ht=help_text or _help_for(text)
    st.markdown(f'<div class="help-subtitle">{_e(text)} {qmark(ht)}</div>', unsafe_allow_html=True)

# IMPORTANTE:
# Não alteramos mais funções internas do Streamlit com setattr/st.subheader.
# Isso causava a exibição indevida da documentação do Streamlit na tela do usuário.
# Para explicações, usamos apenas componentes visíveis próprios: header(), metric(), help_title() e help_note().

def ux_card(title, text, action=""):
    st.markdown(f"<div class='ux-card'><div class='ux-card-title'>{title}</div><div class='ux-card-text'>{text}</div>{f'<div class=\'ux-card-action\'>{action}</div>' if action else ''}</div>", unsafe_allow_html=True)

def help_note(title, technical, example=""):
    example_html = f"<br><b>Exemplo:</b> {example}" if example else ""
    st.markdown(f"<div class='tooltip-box'><span class='help-badge'>?</span><b>{title}</b><br>{technical}{example_html}</div>", unsafe_allow_html=True)

def progress_steps():
    p=ensure_profile(); cash=cash_df(); dre=dre_df(); acc=accounts_df(); acts=actions_df(); market=marketing_df(); unit=unit_df(); okrs=okr_df(); fb=feedback_df(); routines=routines_df(); dec=decisions_df()
    return [
        ("Minha Empresa", bool(p.get("company_name")), "Cadastrar realidade da empresa", "Nome, segmento, porte, caixa inicial, custos, estoque e observações."),
        ("Fluxo de Caixa", not cash.empty, "Lançar entradas e saídas", "Sem fluxo, o conselheiro não enxerga a sobrevivência financeira."),
        ("DRE", not dre.empty, "Separar lucro de caixa", "DRE mostra resultado econômico; fluxo mostra dinheiro entrando e saindo."),
        ("Contas", not acc.empty, "Mapear pagar e receber", "Vencimentos, baixas e histórico reduzem surpresa de caixa."),
        ("Marketing e Oferta", not market.empty, "Definir cliente, dor e promessa", "Sem oferta clara, vender vira tentativa solta."),
        ("Unidade Econômica", not unit.empty, "Medir venda saudável", "Ticket, margem, CAC e LTV indicam se escalar vale a pena."),
        ("OKRs e 90 Dias", not okrs.empty, "Focar execução", "Um objetivo e poucos resultados-chave evitam dispersão."),
        ("Plano de Ação", not acts.empty, "Transformar decisão em execução", "Toda ação precisa de responsável, prazo e status."),
        ("Feedback de Mercado", not fb.empty, "Ouvir mercado real", "Feedback, dor e objeção mostram o que melhora e o que vende."),
        ("Rotina Executiva", not routines.empty or not dec.empty, "Criar ritual de gestão", "Revisão semanal, decisões registradas e aprendizado acumulado."),
    ]

def completion_score():
    steps=progress_steps()
    return int(sum(1 for _,done,_,__ in steps if done)/len(steps)*100) if steps else 0
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
        cur.execute("create table if not exists companies(id text primary key,name text,owner_name text,active int default 1,created_at text default current_timestamp)")
        cur.execute("insert or ignore into companies(id,name,owner_name,active) values(?,?,?,1)", (DEFAULT_COMPANY_ID, "Empresa Principal", "Administrador"))
        cur.execute("create table if not exists app_users(id text primary key,company_id text,name text,email text unique,password_salt text,password_hash text,role text,active int default 1,created_at text default current_timestamp)")
        cur.execute("create table if not exists company_profile(id text primary key,company_id text,company_name text,owner_name text,segment text,business_size text,monthly_revenue real default 0,fixed_costs real default 0,variable_costs real default 0,stock_value real default 0,initial_cash real default 0,notes text,updated_at text)")
        cur.execute("create table if not exists cash_flow(id text primary key,company_id text,date text,type text,category text,description text,amount real default 0,channel text,created_by text,created_at text default current_timestamp)")
        cur.execute("create table if not exists accounts(id text primary key,company_id text,due_date text,kind text,supplier_client text,description text,amount real default 0,status text default 'Aberto',paid_date text,created_by text,created_at text default current_timestamp)")
        cur.execute("create table if not exists action_plan(id text primary key,company_id text,priority text,area text,action text,responsible text,due_date text,status text default 'Pendente',created_by text,created_at text default current_timestamp)")
        cur.execute("create table if not exists advisor_history(id text primary key,company_id text,asked_at text,question text,answer text,created_by text)")
        cur.execute("create table if not exists dre_records(id text primary key,company_id text,period_start text,period_end text,receita_bruta real default 0,deducoes_impostos real default 0,receita_liquida real default 0,custos_produtos_servicos real default 0,lucro_bruto real default 0,despesas_operacionais real default 0,resultados_financeiros real default 0,ebitda real default 0,lucro_operacional real default 0,lucro_liquido real default 0,notes text,created_by text,created_at text default current_timestamp)")
        cur.execute("create table if not exists calendar_events(id text primary key,company_id text,event_date text,event_time text,title text,category text,level text,color text,notes text,created_by text,created_at text default current_timestamp)")
        cur.execute("create table if not exists mvp_feedback(id text primary key,company_id text,feedback_date text,person text,profile text,score int default 0,main_pain text,liked text,missing text,objection text,status text,created_by text,created_at text default current_timestamp)")
        cur.execute("create table if not exists executive_routines(id text primary key,company_id text,routine_date text,routine_type text,score int default 0,focus text,decisions text,risks text,next_actions text,created_by text,created_at text default current_timestamp)")
        cur.execute("create table if not exists decision_log(id text primary key,company_id text,decision_date text,area text,decision text,reason text,expected_result text,owner text,due_date text,status text,created_by text,created_at text default current_timestamp)")
        cur.execute("create table if not exists marketing_playbook(id text primary key,company_id text,created_at text default current_timestamp,segment text,ideal_customer text,main_pain text,promise text,offer text,proof text,objections text,channels text,next_test text,created_by text)")
        cur.execute("create table if not exists unit_economics(id text primary key,company_id text,created_at text default current_timestamp,ticket_medio real default 0,margem_contribuicao real default 0,cac real default 0,compras_ano real default 1,retencao_meses real default 12,churn_mensal real default 0,created_by text)")
        cur.execute("create table if not exists okr_records(id text primary key,company_id text,created_at text default current_timestamp,quarter text,objective text,key_result text,target text,current_value text,confidence int default 5,owner text,due_date text,status text,created_by text)")
        self.conn.commit()

    def select(self,t,filters=None,order=None,desc=False,limit=None):
        filters=dict(filters or {})
        if has_logged_user():
            if is_company_table(t) and "company_id" not in filters:
                filters["company_id"]=current_company_id()
            if t=="app_users" and "company_id" not in filters:
                filters["company_id"]=current_company_id()
        if self.mode=="supabase":
            q=self.sb.table(t).select("*")
            for k,v in filters.items(): q=q.eq(k,v)
            if order:q=q.order(order,desc=desc)
            if limit:q=q.limit(limit)
            try:
                return list(q.execute().data or [])
            except Exception:
                return []
        sql=f"select * from {t}";vals=[]
        if filters:
            sql+=" where "+" and ".join([f"{k}=?" for k in filters])
            vals=list(filters.values())
        if order: sql+=f" order by {order} {'desc' if desc else 'asc'}"
        if limit: sql+=f" limit {int(limit)}"
        try:
            return [dict(r) for r in self.conn.execute(sql,vals).fetchall()]
        except Exception:
            return []

    def insert(self,t,d):
        d=dict(d or {})
        if is_company_table(t) and "company_id" not in d:
            d["company_id"]=current_company_id()
        if t=="app_users" and "company_id" not in d:
            d["company_id"]=current_company_id()
        if self.mode=="supabase":
            try: return self.sb.table(t).insert(d).execute()
            except Exception as e: st.error(f"Erro ao salvar em {t}: {e}"); return None
        ks=list(d.keys())
        self.conn.execute(f"insert into {t} ({','.join(ks)}) values ({','.join(['?']*len(ks))})",[d[k] for k in ks])
        self.conn.commit()

    def update(self,t,row_id,d):
        d=dict(d or {})
        if self.mode=="supabase":
            try:
                q=self.sb.table(t).update(d).eq("id",row_id)
                if has_logged_user() and (is_company_table(t) or t=="app_users"):
                    q=q.eq("company_id", current_company_id())
                return q.execute()
            except Exception as e: st.error(f"Erro ao editar em {t}: {e}"); return None
        ks=list(d.keys())
        self.conn.execute(f"update {t} set {','.join([k+'=?' for k in ks])} where id=?",[d[k] for k in ks]+[row_id])
        self.conn.commit()

    def delete(self,t,row_id):
        if self.mode=="supabase":
            try:
                q=self.sb.table(t).delete().eq("id",row_id)
                if has_logged_user() and (is_company_table(t) or t=="app_users"):
                    q=q.eq("company_id", current_company_id())
                return q.execute()
            except Exception as e: st.error(f"Erro ao apagar em {t}: {e}"); return None
        self.conn.execute(f"delete from {t} where id=?",(row_id,))
        self.conn.commit()

    def count(self,t):
        filters={}
        if has_logged_user():
            if is_company_table(t):
                filters["company_id"]=current_company_id()
            if t=="app_users":
                filters["company_id"]=current_company_id()
        if self.mode=="supabase":
            try:
                q=self.sb.table(t).select("id")
                for k,v in filters.items(): q=q.eq(k,v)
                return len(q.execute().data or [])
            except Exception: return 0
        sql=f"select count(*) from {t}"
        vals=[]
        if filters:
            sql+=" where "+" and ".join([f"{k}=?" for k in filters])
            vals=list(filters.values())
        return int(self.conn.execute(sql,vals).fetchone()[0])
def get_db(): return DB()
db=get_db()


def get_company(company_id=None):
    cid = company_id or current_company_id()
    rows = db.select("companies", {"id": cid}, limit=1)
    return rows[0] if rows else {"id": cid, "name": "Empresa atual", "owner_name": ""}

def create_company_record(name, owner_name=""):
    name = (name or "").strip() or "Nova empresa"
    company_id = str(uuid.uuid4())
    db.insert("companies", dict(id=company_id, name=name, owner_name=owner_name or "", active=1))
    return company_id

def first_company_id():
    rows = db.select("companies", order="created_at", limit=1)
    if rows:
        return rows[0].get("id") or DEFAULT_COMPANY_ID
    db.insert("companies", dict(id=DEFAULT_COMPANY_ID, name="Empresa Principal", owner_name="Administrador", active=1))
    return DEFAULT_COMPANY_ID

def attach_company_info(user):
    user = dict(user or {})
    cid = user.get("company_id") or first_company_id()
    user["company_id"] = cid
    comp = get_company(cid)
    user["company_name"] = comp.get("name") or "Empresa atual"
    return user


def role():
    return st.session_state.get("user",{}).get("role","usuario")

def is_owner():
    return role() in ["dono do app", "super_admin"]

def is_admin():
    return role() in ["dono do app", "super_admin", "administrador"]

def is_company_admin():
    return role() == "administrador"

def can_manage_users():
    return role() in ["dono do app", "super_admin", "administrador", "usuario"]

def can_create_company():
    return role() in ["dono do app", "super_admin"]

def can_edit():
    return role() in ["dono do app", "super_admin", "administrador", "usuario"]

def readonly_warning():
    if not can_edit():
        st.info("Seu perfil é somente leitura. Você pode visualizar, mas não pode cadastrar, editar ou apagar.")

def user_name():
    return st.session_state.get("user",{}).get("name","Usuário")


def create_user(name,email,pw,role_value="usuario",company_id=None,created_by_user_id=None):
    cid = company_id or current_company_id()
    if has_logged_user() and not is_owner() and db.count("app_users")>=MAX_USERS:
        return False,f"Limite de {MAX_USERS} usuários atingido nesta empresa."
    email=email.strip().lower()
    if not name or not email or len(pw)<6:
        return False,"Preencha nome, e-mail e senha com no mínimo 6 caracteres."
    if db.select("app_users",{"email":email}):
        return False,"E-mail já cadastrado."
    # segurança: usuário comum nunca cria administrador
    if role()=="usuario" and role_value not in ["usuario", "somente leitura"]:
        role_value="usuario"
    if role()=="administrador" and role_value in ["dono do app","super_admin"]:
        role_value="usuario"
    s,d=hpw(pw)
    data=dict(id=str(uuid.uuid4()),company_id=cid,name=name,email=email,password_salt=s,password_hash=d,role=role_value,active=1)
    # Se a tabela tiver created_by_user_id, o Supabase aceitará; se não tiver, removemos no erro? Para evitar erro, não gravaremos.
    db.insert("app_users",data)
    return True,"Usuário criado."
def login_user(email,pw):
    us=db.select("app_users",{"email":email.strip().lower()})
    if not us:return None,"Usuário não encontrado."
    u=us[0]
    if int(u.get("active",1))!=1:return None,"Usuário inativo."
    if not cpw(pw,u["password_salt"],u["password_hash"]):return None,"Senha incorreta."
    if not u.get("company_id"):
        cid = first_company_id()
        try:
            db.update("app_users", u["id"], {"company_id": cid})
            u["company_id"] = cid
        except Exception:
            u["company_id"] = cid
    return attach_company_info(u),"OK"


def login_screen():
    header(APP_NAME, "Acesso executivo multiempresa")

    total_users = db.count("app_users")
    if total_users == 0:
        st.warning("Primeiro acesso: crie a primeira empresa e o dono do app.")
        with st.form("first_admin"):
            code = st.text_input("Código de criação", type="password")
            company_name = st.text_input("Nome da empresa principal", placeholder="Ex.: Gestão Executiva")
            name = st.text_input("Nome do dono do app")
            email = st.text_input("E-mail")
            pw = st.text_input("Senha", type="password")
            sub = st.form_submit_button("Criar dono do app", use_container_width=True)
        if sub:
            if code != secret("SETUP_CODE", "executa2026"):
                st.error("Código de criação incorreto.")
            else:
                cid = create_company_record(company_name, name)
                ok, msg = create_user(name, email, pw, "dono do app", cid)
                st.success("Dono do app criado. Agora faça login.") if ok else st.error(msg)
        return

    c1, c2 = st.columns([1.15, .85], gap="large")
    with c1:
        st.subheader("Entrar")
        with st.form("login"):
            email = st.text_input("E-mail")
            pw = st.text_input("Senha", type="password")
            ok = st.form_submit_button("Entrar", use_container_width=True)
        if ok:
            u, msg = login_user(email, pw)
            if u:
                st.session_state.user = u
                st.rerun()
            else:
                st.error(msg)

    with c2:
        st.markdown("<div class='tooltip-box'><span class='help-badge'>?</span><b>Multiempresa ativo</b><br>Cada usuário entra apenas na empresa à qual pertence. Os dados de uma empresa não aparecem para outra.</div>", unsafe_allow_html=True)
        st.info(f"Banco atual: **{db.mode.upper()}**")
def ensure_profile():
    cid = current_company_id()
    r=db.select("company_profile",limit=1)
    if r:return r[0]
    comp = get_company(cid)
    row=dict(id=f"profile-{cid}",company_id=cid,company_name=comp.get("name",""),owner_name=comp.get("owner_name",""),segment="",business_size="Pequena",monthly_revenue=0,fixed_costs=0,variable_costs=0,stock_value=0,initial_cash=0,notes="",updated_at=today_db())
    db.insert("company_profile",row)
    return row
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

def feedback_df():
    df=df_table("mvp_feedback","feedback_date",True)
    if df.empty:return pd.DataFrame(columns=["id","feedback_date","person","profile","score","main_pain","liked","missing","objection","status","created_by"])
    df["score"]=pd.to_numeric(df.get("score",0),errors="coerce").fillna(0)
    return df

def routines_df():
    df=df_table("executive_routines","routine_date",True)
    if df.empty:return pd.DataFrame(columns=["id","routine_date","routine_type","score","focus","decisions","risks","next_actions","created_by"])
    df["score"]=pd.to_numeric(df.get("score",0),errors="coerce").fillna(0)
    return df

def decisions_df():
    df=df_table("decision_log","decision_date",True)
    if df.empty:return pd.DataFrame(columns=["id","decision_date","area","decision","reason","expected_result","owner","due_date","status","created_by"])
    return df

def marketing_df():
    df=df_table("marketing_playbook","created_at",True)
    if df.empty:return pd.DataFrame(columns=["id","created_at","segment","ideal_customer","main_pain","promise","offer","proof","objections","channels","next_test","created_by"])
    return df

def unit_df():
    df=df_table("unit_economics","created_at",True)
    if df.empty:return pd.DataFrame(columns=["id","created_at","ticket_medio","margem_contribuicao","cac","compras_ano","retencao_meses","churn_mensal","created_by"])
    for c in ["ticket_medio","margem_contribuicao","cac","compras_ano","retencao_meses","churn_mensal"]:
        df[c]=pd.to_numeric(df[c],errors="coerce").fillna(0)
    return df

def okr_df():
    df=df_table("okr_records","due_date")
    if df.empty:return pd.DataFrame(columns=["id","created_at","quarter","objective","key_result","target","current_value","confidence","owner","due_date","status","created_by"])
    return df

def status_badge(score):
    try: score=float(score or 0)
    except Exception: score=0
    if score>=75:return "<span class='badge-ok'>bom</span>"
    if score>=45:return "<span class='badge-warn'>atenção</span>"
    return "<span class='badge-risk'>risco</span>"


def exec_reading():
    m=calc();s,als=alertas();actions=actions_df();cash=cash_df();dre=dre_df();acc=accounts_df()
    frases=[]
    if s>=75:
        frases.append("A empresa está em zona administrável. O papel agora é manter cadência: revisar caixa, margem e plano de ação toda semana para não perder controle enquanto cresce.")
    elif s>=45:
        frases.append("A empresa está em zona de atenção. Ela provavelmente ainda funciona, mas existem sinais de fragilidade em caixa, margem, contas ou execução. O foco deve ser corrigir antes de acelerar.")
    else:
        frases.append("A empresa está em zona de risco. Antes de buscar crescimento, o empresário precisa proteger caixa, revisar margem, controlar vencimentos e reduzir decisões baseadas em achismo.")
    if cash.empty:
        frases.append("O fluxo de caixa ainda está vazio; sem registrar entradas e saídas, o sistema não consegue enxergar a realidade financeira.")
    if dre.empty:
        frases.append("Ainda não há DRE lançado; sem DRE, você vê dinheiro entrando e saindo, mas não sabe se a operação gera lucro de verdade.")
    if not acc.empty and m["pagar"] > m["receber"] + m["caixa"]:
        frases.append("As contas a pagar exigem atenção porque superam a soma de caixa e recebíveis em aberto.")
    if actions.empty:
        frases.append("O plano de ação está vazio; sem responsável e prazo, a empresa até entende o problema, mas não muda comportamento.")
    if als:
        frases.append("Alertas prioritários: " + "; ".join([a[1] for a in als[:3]]) + ".")
    return " ".join(frases)

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

def solution_steps(title, action):
    t = (title or "").lower()
    if "caixa" in t:
        return [
            "Liste todos os vencimentos dos próximos 30 dias e separe o que é essencial do que pode ser renegociado.",
            "Acelere recebíveis: cobre atrasados, antecipe entradas seguras e reduza prazo de novos recebimentos.",
            "Suspenda gastos que não gerem venda, margem, entrega ou retenção no curto prazo."
        ]
    if "margem" in t or "resultado" in t:
        return [
            "Revise preço por canal considerando imposto, taxa, frete, embalagem, desconto e custo real.",
            "Separe produtos/serviços por margem: mantenha, reajuste ou descontinue o que destrói resultado.",
            "Crie uma ação no Plano de Ação para corrigir o principal item de custo desta semana."
        ]
    if "pagar" in t or "recebíveis" in t:
        return [
            "Abra Contas a Pagar e Contas a Receber e confira vencimentos, atrasos e valores grandes.",
            "Negocie prazos de saída antes de assumir novas compras ou contratações.",
            "Transforme as 3 maiores contas em decisões: pagar, renegociar, parcelar ou cortar."
        ]
    if "capital" in t or "giro" in t:
        return [
            "Reduza dinheiro parado: estoque sem giro, contas longas para receber e compras antecipadas.",
            "Faça uma previsão de 30 dias no Fluxo de Caixa antes de escalar marketing ou equipe.",
            "Defina uma meta mínima de caixa e acompanhe no Painel semanalmente."
        ]
    if "plano" in t or "ação" in t:
        return [
            "Crie 3 ações: uma financeira, uma comercial e uma operacional.",
            "Cada ação precisa ter responsável, prazo e status; sem isso, é apenas intenção.",
            "Revise essas ações na Rotina Executiva semanal."
        ]
    return [action or "Transforme o alerta em uma ação com responsável e prazo.", "Registre a ação no Plano de Ação.", "Revise o resultado em até 7 dias."]


def growth_lanes():
    m=calc(); cash=cash_df(); dre=dre_df(); acts=actions_df(); acc=accounts_df(); events=events_df()
    financeiro = 15 + (25 if not cash.empty else 0) + (25 if not dre.empty else 0) + (20 if m['margem']>=10 else 0) + (15 if m['caixa']>=0 else 0)
    caixa = 20 + (25 if m['caixa']>=0 else 0) + (25 if m['pagar'] <= m['receber'] + m['caixa'] else 0) + (15 if not acc.empty else 0) + (15 if m['ncg'] <= max(1,m['receita']) else 0)
    execucao = 20 + min(45, len(acts)*9) + (20 if not acts.empty and "status" in acts and len(acts[acts.status=="Concluído"])>0 else 0) + (15 if not events.empty else 0)
    operacao = 25 + (25 if m['estoque'] <= max(1,m['receita']) else 0) + (25 if m['ncg'] <= max(1,m['receita']) else 0) + (25 if not acts.empty else 0)
    lideranca = 20 + (30 if not acts.empty else 0) + (25 if not dre.empty else 0) + (25 if not cash.empty else 0)
    return [
        ("Financeiro", min(100,financeiro), "DRE, margem, resultado e consistência dos números.", "Se estiver baixo: atualizar DRE, revisar preço/custo e separar lucro de caixa."),
        ("Caixa e liquidez", min(100,caixa), "Caixa atual, contas a pagar, recebíveis e capital de giro.", "Se estiver baixo: renegociar vencimentos, acelerar recebíveis e cortar gastos não essenciais."),
        ("Execução", min(100,execucao), "Plano de ação, responsáveis, prazos, calendário e conclusão.", "Se estiver baixo: criar poucas ações, com dono claro e revisão semanal."),
        ("Operação", min(100,operacao), "Estoque, giro, capacidade operacional e disciplina de processo.", "Se estiver baixo: reduzir estoque parado, padronizar rotina crítica e evitar crescimento desorganizado."),
        ("Liderança", min(100,lideranca), "Qualidade da decisão do empreendedor e ritmo de acompanhamento.", "Se estiver baixo: usar o Painel semanalmente, registrar ações e acompanhar indicadores.")
    ]

def render_growth_lanes():
    for title,score,body,action in growth_lanes():
        st.markdown(f"<div class='strategy-lane'><div class='lane-head'><div class='lane-title'>{title}</div><div class='lane-score'>{score}/100</div></div><div class='lane-body'>{body}</div><div class='lane-action'>{action}</div></div>", unsafe_allow_html=True)



def sidebar():
    u=st.session_state.user
    st.sidebar.markdown(f'<div class="user-pill">👤 <b>{_html.escape(str(u["name"]))}</b><br>{_html.escape(str(u.get("role","usuario")))}<br><span style="color:#8EA4BC;font-size:12px;">{_html.escape(str(current_company_name()))}</span></div>',unsafe_allow_html=True)
    st.sidebar.markdown("**Módulos**")
    pages=["Minha Empresa","Painel","Fluxo de Caixa","Contas a Pagar","Contas a Receber","DRE","Calendário","Relatórios","Plano de Ação","Alertas"]
    if can_manage_users() and role() != "somente leitura":
        pages.append("Usuários")
    page=st.sidebar.radio("Módulos",pages,label_visibility="collapsed")
    st.sidebar.markdown("<br>",unsafe_allow_html=True)
    if st.sidebar.button("Sair", use_container_width=True):
        st.session_state.clear()
        st.rerun()
    return page
def topbar():
    c1,c2=st.columns([6.8,1.9])
    with c1:
        st.empty()
    with c2:
        st.markdown('<div class="top-method-btn">', unsafe_allow_html=True)
        clicked=st.button("O que é o Método EXECUTA", use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)
        if clicked:
            return "Método EXECUTA"
    return None
def select_record(df,lab,key):
    # Mantido por compatibilidade, mas a v5.1 usa seleção direta na tabela.
    opts=[(lab(r),r.get("id")) for _,r in df.iterrows()]
    return st.selectbox("Selecionar registro",opts,format_func=lambda x:x[0],key=key) if opts else None

def selected_row_from_table(raw_df, display_df, columns, key, caption="Clique em uma linha da tabela para selecionar."):
    """Mostra uma tabela clicável e retorna a linha original selecionada.
    Evita IndexError quando o estado do Streamlit fica com uma seleção antiga.
    """
    if raw_df is None or raw_df.empty:
        return None
    raw = raw_df.reset_index(drop=True).copy()
    view = display_df.reset_index(drop=True).copy()
    st.caption(caption)
    try:
        event = st.dataframe(
            view[columns],
            use_container_width=True,
            hide_index=True,
            on_select="rerun",
            selection_mode="single-row",
            key=key,
        )
        try:
            rows = list(event.selection.rows)
        except Exception:
            rows = list((event or {}).get("selection", {}).get("rows", []))
        if rows:
            pos = int(rows[0])
            if 0 <= pos < len(raw):
                return raw.iloc[pos].to_dict()
    except TypeError:
        # Fallback para versões antigas do Streamlit: mostra a tabela normal e deixa selecionar pelo campo.
        st.dataframe(view[columns], use_container_width=True, hide_index=True, key=key)
        opts=[]
        for i, r in raw.iterrows():
            if "date" in raw.columns:
                label=f"{date_br(r.get('date'))} | {r.get('type','')} | {r.get('category','')} | {brl(r.get('amount',0))} | {r.get('description','')}"
            elif "due_date" in raw.columns:
                label=f"{date_br(r.get('due_date'))} | {r.get('supplier_client','')} | {brl(r.get('amount',0))} | {r.get('description','')}"
            else:
                label=" | ".join(str(r.get(c,'')) for c in raw.columns[:4])
            opts.append((label, i))
        chosen=st.selectbox("Selecionar linha", opts, format_func=lambda x:x[0], key=key+"_fallback")
        if chosen:
            return raw.iloc[int(chosen[1])].to_dict()
    return None


def ceo_next_move():
    m=calc(); s,als=alertas(); acts=actions_df(); cash=cash_df(); dre=dre_df(); acc=accounts_df()
    if cash.empty:
        return "Primeiro movimento: lançar entradas e saídas reais no Fluxo de Caixa. Sem caixa registrado, qualquer conselho vira chute."
    if dre.empty:
        return "Segundo movimento: lançar o DRE do período. O empreendedor precisa separar caixa de lucro para saber se a empresa realmente ganha dinheiro."
    if m["caixa"] < 0:
        return "Modo proteção: renegociar pagamentos, acelerar recebíveis, cortar gastos não essenciais e travar qualquer investimento que não gere retorno imediato."
    if m["pagar"] > m["receber"] + m["caixa"]:
        return "Modo liquidez: revisar próximos vencimentos, priorizar contas críticas e negociar prazo antes de assumir novas compras."
    if m["margem"] < 10:
        return "Modo margem: revisar preço, custo direto, impostos, taxas, frete e mix de produtos. Crescer com margem fraca aumenta faturamento e também o problema."
    if acts.empty:
        return "Modo execução: criar 3 ações no Plano de Ação: uma para caixa, uma para margem e uma para venda/cliente, todas com responsável e prazo."
    return "Modo crescimento controlado: manter rotina semanal, acompanhar margem por canal, proteger caixa e investir apenas no que provar retorno."


def ceo_questions():
    m=calc(); acts=actions_df(); cash=cash_df(); dre=dre_df()
    qs=[]
    if cash.empty: qs.append("Quais entradas e saídas reais ainda não foram lançadas no fluxo de caixa?")
    if dre.empty: qs.append("A empresa está lucrando de verdade ou apenas movimentando dinheiro?")
    if m["pagar"] > m["receber"] + m["caixa"]: qs.append("Quais pagamentos podem ser renegociados sem quebrar a operação?")
    if m["margem"] < 10: qs.append("Qual produto, serviço ou canal vende, mas destrói margem?")
    if acts.empty: qs.append("Quais 3 ações com responsável e prazo mudariam a empresa nos próximos 7 dias?")
    qs += [
        "Qual decisão você está adiando porque os números podem mostrar uma verdade desconfortável?",
        "O que precisa ser parado para liberar caixa, tempo e foco?",
        "Qual métrica provaria que a empresa está pronta para crescer com segurança?"
    ]
    return qs[:6]

def page_jornada_guiada():
    header("Jornada Guiada", "Onboarding executivo para o usuário não se perder: primeiro realidade, depois leitura, decisão, execução e revisão.")
    score=completion_score(); steps=progress_steps()
    st.markdown(f"<div class='exec-hero'><h3>Seu avanço de estruturação: {score}%</h3><p>O objetivo não é preencher tudo por preencher. O objetivo é criar uma rotina que ajude a empresa a faturar mais com caixa, margem, foco e execução.</p></div>", unsafe_allow_html=True)
    c=st.columns(3)
    with c[0]: ux_card("1. Verdade", "Cadastre a empresa, fluxo, contas e DRE. O app precisa de realidade para aconselhar.", "Evite achismo")
    with c[1]: ux_card("2. Decisão", "Use Indicadores, Alerta, Unidade Econômica e Conselheiro Executivo para escolher o próximo movimento.", "Menos opinião, mais evidência")
    with c[2]: ux_card("3. Execução", "Transforme decisão em Plano de Ação, OKRs, Rotina Executiva e Decisões registradas.", "Dono + prazo + revisão")
    st.subheader("Checklist de maturidade do uso")
    for i,(name,done,title,desc) in enumerate(steps,1):
        status='Concluído' if done else 'Aberto'
        cls='status-done' if done else 'status-open'
        st.markdown(f"<div class='step-row'><div class='step-num'>{i}</div><div><div class='step-title'>{name} — {title}</div><div class='step-desc'>{desc}</div></div><div class='step-status {cls}'>{status}</div></div>", unsafe_allow_html=True)
    st.info("Experiência recomendada para novos usuários: preencher Minha Empresa → lançar Fluxo/DRE → abrir Sala do CEO → registrar uma decisão → criar 3 ações → fazer Rotina Executiva semanal.")

def page_mapa_crescimento():
    header("Mapa de Crescimento", "Leitura estratégica por frentes: financeiro, mercado, execução, operação e liderança. Serve para mostrar onde a empresa deve atuar primeiro.")
    m=calc(); cash=cash_df(); dre=dre_df(); acts=actions_df(); market=marketing_df(); unit=unit_df(); okrs=okr_df(); fb=feedback_df(); routines=routines_df(); dec=decisions_df()
    financeiro = 20 + (20 if not cash.empty else 0) + (20 if not dre.empty else 0) + (20 if m['margem']>=10 else 0) + (20 if m['caixa']>=0 else 0)
    mercado = 15 + (25 if not market.empty else 0) + (20 if not fb.empty else 0) + (20 if not unit.empty else 0) + (20 if m['margem']>=10 else 0)
    execucao = 15 + min(35, len(acts)*7) + (25 if not okrs.empty else 0) + (25 if not routines.empty else 0)
    operacao = 25 + (20 if m['estoque'] <= max(1,m['receita']) else 0) + (20 if m['ncg'] <= max(1,m['receita']) else 0) + (20 if not dec.empty else 0) + (15 if not acts.empty else 0)
    lideranca = 20 + (25 if not okrs.empty else 0) + (25 if not routines.empty else 0) + (20 if not dec.empty else 0) + (10 if not acts.empty else 0)
    lanes=[
        ("Financeiro", min(100,financeiro), "Caixa, DRE, margem, contas e capital de giro.", "Se estiver baixo: atualizar DRE, renegociar contas e revisar preço/custo."),
        ("Mercado e Oferta", min(100,mercado), "Cliente ideal, dor, promessa, prova, CAC, LTV e feedback real.", "Se estiver baixo: fazer 10 entrevistas e testar uma oferta simples."),
        ("Execução", min(100,execucao), "Plano, OKRs, responsáveis, prazos e rotina semanal.", "Se estiver baixo: criar 3 ações prioritárias para 7 dias."),
        ("Operação", min(100,operacao), "Processo, estoque, giro, decisões e capacidade operacional.", "Se estiver baixo: padronizar a rotina crítica antes de escalar."),
        ("Liderança", min(100,lideranca), "Dono, decisão, governança, reunião e cadência de gestão.", "Se estiver baixo: registrar decisões e criar ritual semanal de liderança."),
    ]
    for title,score,body,action in lanes:
        st.markdown(f"<div class='strategy-lane'><div class='lane-head'><div class='lane-title'>{title}</div><div class='lane-score'>{score}/100</div></div><div class='lane-body'>{body}</div><div class='lane-action'>{action}</div></div>", unsafe_allow_html=True)
    st.warning("Regra executiva: não acelerar marketing ou contratação se Financeiro, Mercado e Execução estiverem fracos. Primeiro corrija a base, depois escale.")

def page_sala_ceo():
    header("Sala do CEO", "O app não é um depósito de dados: é uma sala de comando para ler a empresa, decidir, executar e revisar.")
    st.markdown("<div class='exec-hero'><h3>O que o usuário deve sentir aqui</h3><p>Em menos de 2 minutos, o empreendedor precisa entender: estou saudável? Qual gargalo está travando crescimento? O que faço esta semana?</p></div>", unsafe_allow_html=True)
    m=calc(); s,als=alertas(); fb=feedback_df(); acts=actions_df(); dec=decisions_df(); okrs=okr_df()
    c=st.columns(5)
    with c[0]: metric("Score", f"{s}/100", "saúde geral")
    with c[1]: metric("Caixa", brl(m["caixa"]), "poder de sobrevivência")
    with c[2]: metric("Margem", pct(m["margem"]), "qualidade do resultado")
    with c[3]: metric("Execução", str(len(acts)), "ações registradas")
    with c[4]: metric("Decisões", str(len(dec)), "memória executiva")
    st.markdown("<div class='section-kicker'>próximo movimento recomendado</div>", unsafe_allow_html=True)
    st.markdown(f"<div class='insight-card'><div class='insight-title'>Decisão do Conselheiro Executivo</div><div class='insight-text'>{ceo_next_move()}</div></div>", unsafe_allow_html=True)
    c1,c2,c3=st.columns(3)
    with c1:
        st.markdown("<div class='ceo-grid-card'><div class='ceo-card-title'>1. Realidade</div><div class='ceo-card-text'>Números antes de opinião. Fluxo, DRE, contas e margem dizem onde dói.</div></div>", unsafe_allow_html=True)
    with c2:
        st.markdown("<div class='ceo-grid-card'><div class='ceo-card-title'>2. Decisão</div><div class='ceo-card-text'>Toda decisão importante precisa de motivo, dono, prazo e métrica de sucesso.</div></div>", unsafe_allow_html=True)
    with c3:
        st.markdown("<div class='ceo-grid-card'><div class='ceo-card-title'>3. Execução</div><div class='ceo-card-text'>A empresa melhora por rituais semanais, não por cadastro bonito e abandonado.</div></div>", unsafe_allow_html=True)
    st.subheader("Perguntas difíceis do CEO")
    for q in ceo_questions(): st.markdown(f"<div class='ceo-question'>{q}</div>", unsafe_allow_html=True)
    if can_edit():
        st.subheader("Criar ação rápida a partir da decisão")
        with st.form("ceo_quick_action", clear_on_submit=True):
            action=st.text_area("Ação executiva", value=ceo_next_move())
            owner=st.text_input("Responsável", user_name())
            due=st.date_input("Prazo", value=dt.date.today()+dt.timedelta(days=7), format="DD/MM/YYYY")
            if st.form_submit_button("Enviar para Plano de Ação"):
                db.insert("action_plan",dict(id=str(uuid.uuid4()),priority="Alta",area="Governança",action=action,responsible=owner,due_date=due.strftime(DATE_DB),status="Pendente",created_by=user_name()))
                st.success("Ação enviada para o Plano de Ação."); st.rerun()

def page_marketing_oferta():
    header("Marketing e Oferta", "Transforme o sistema em conselheiro comercial: cliente, dor, promessa, prova, objeção, canal e próximo teste.")
    help_note("Como pensar oferta", "Uma boa oferta une cliente específico, dor cara, promessa clara, prova confiável e próximo passo simples. O erro comum é descrever o produto, não o resultado que o cliente compra.", "Para lojistas que perdem tempo com notas fiscais, reduzir 80% do trabalho manual em 7 dias.")
    readonly_warning()
    if can_edit():
        with st.form("marketing_form", clear_on_submit=True):
            c1,c2=st.columns(2)
            with c1:
                segment=st.text_input("Segmento/Nicho")
                ideal=st.text_area("Cliente ideal / ICP", placeholder="Quem sente a dor, decide e paga?")
                pain=st.text_area("Dor principal", placeholder="Qual problema caro, frequente e urgente você resolve?")
                promise=st.text_area("Promessa da oferta", placeholder="Resultado específico que o cliente entende e deseja.")
            with c2:
                offer=st.text_area("Oferta", placeholder="O que será entregue, prazo, bônus, garantia, condição.")
                proof=st.text_area("Provas", placeholder="Cases, números, antes/depois, demonstração, autoridade.")
                objections=st.text_area("Objeções", placeholder="Preço, confiança, tempo, prioridade, concorrência.")
                channels=st.text_area("Canais", placeholder="Google, Instagram, marketplace, indicação, WhatsApp, outbound etc.")
            test=st.text_area("Próximo teste de mercado", placeholder="Teste pequeno, barato e mensurável para os próximos 7 dias.")
            if st.form_submit_button("Salvar playbook de marketing"):
                db.insert("marketing_playbook",dict(id=str(uuid.uuid4()),segment=segment,ideal_customer=ideal,main_pain=pain,promise=promise,offer=offer,proof=proof,objections=objections,channels=channels,next_test=test,created_by=user_name()))
                st.success("Playbook salvo."); st.rerun()
    df=marketing_df()
    if df.empty:
        st.info("Nenhum playbook salvo ainda. Comece registrando a hipótese de cliente, dor e oferta.")
        return
    rec=df.iloc[0].to_dict()
    st.subheader("Mensagem comercial sugerida")
    msg=f"Para {rec.get('ideal_customer') or 'seu cliente ideal'}, que sofre com {rec.get('main_pain') or 'uma dor relevante'}, nossa solução entrega {rec.get('promise') or 'um resultado mensurável'}, por meio de {rec.get('offer') or 'uma oferta clara'}, com prova em {rec.get('proof') or 'evidências reais'}."
    st.text_area("Copie e ajuste", msg, height=120)
    show=df.copy(); st.dataframe(show[["created_at","segment","ideal_customer","main_pain","promise","offer","proof","objections","channels","next_test","created_by"]], use_container_width=True, hide_index=True)

def page_unit_economics():
    header("Unidade Econômica", "O crescimento só é saudável quando cada venda gera margem suficiente para pagar aquisição, operação e caixa.")
    help_note("Como usar unidade econômica", "Preencha ticket médio, margem de contribuição e CAC para saber se vender mais realmente cria valor. Se o CAC for alto e a margem baixa, crescer pode destruir caixa.", "Ticket R$ 300, margem 40%, CAC R$ 60: a primeira venda gera R$ 120 de margem e paga aquisição.")
    readonly_warning()
    if can_edit():
        with st.form("unit_form", clear_on_submit=True):
            c1,c2,c3=st.columns(3)
            with c1:
                ticket=money_input("Ticket médio",0,"unit_ticket")
                mc=st.slider("Margem de contribuição",0,100,40,help="Percentual que sobra após custos variáveis diretos.")
            with c2:
                cac=money_input("CAC / custo de aquisição",0,"unit_cac")
                compras=st.number_input("Compras por cliente ao ano",min_value=1.0,value=1.0,step=0.5)
            with c3:
                ret=st.number_input("Retenção média em meses",min_value=1.0,value=12.0,step=1.0)
                churn=st.slider("Churn mensal estimado",0,100,0)
            if st.form_submit_button("Salvar unidade econômica"):
                db.insert("unit_economics",dict(id=str(uuid.uuid4()),ticket_medio=ticket,margem_contribuicao=mc,cac=cac,compras_ano=compras,retencao_meses=ret,churn_mensal=churn,created_by=user_name()))
                st.success("Unidade econômica salva."); st.rerun()
    df=unit_df()
    if df.empty: st.info("Cadastre ticket, margem e CAC para o conselheiro avaliar se crescer faz sentido."); return
    r=df.iloc[0]
    lucro_por_compra=float(r.ticket_medio)*float(r.margem_contribuicao)/100
    ltv=lucro_por_compra*float(r.compras_ano)*(float(r.retencao_meses)/12)
    cac=float(r.cac)
    payback=(cac/lucro_por_compra) if lucro_por_compra>0 else 0
    ratio=(ltv/cac) if cac>0 else 0
    c=st.columns(4)
    with c[0]: metric("Lucro por compra", brl(lucro_por_compra), f"margem {pct(r.margem_contribuicao)}")
    with c[1]: metric("LTV estimado", brl(ltv), "valor econômico do cliente")
    with c[2]: metric("LTV/CAC", f"{ratio:.1f}x" if cac else "sem CAC", "acima de 3x tende a ser bom")
    with c[3]: metric("Payback", f"{payback:.1f} compras" if lucro_por_compra else "sem margem", "tempo para recuperar CAC")
    if cac and ratio<1: st.error("Alerta: a aquisição parece destruir valor. Antes de investir em tráfego, ajuste oferta, margem ou conversão.")
    elif cac and ratio<3: st.warning("Atenção: há potencial, mas ainda não está robusto para escalar agressivamente.")
    else: st.success("Sinal positivo: unidade econômica parece saudável para testes controlados de crescimento.")

def page_okrs_90():
    header("OKRs e 90 Dias", "Foco executivo: um objetivo claro, poucos resultados-chave e revisão semanal.")
    readonly_warning()
    if can_edit():
        with st.form("okr_form", clear_on_submit=True):
            c1,c2=st.columns(2)
            with c1:
                q=st.text_input("Ciclo", value=f"{dt.date.today().year} - Próximos 90 dias")
                obj=st.text_area("Objetivo", placeholder="Ex.: Tornar o negócio financeiramente previsível")
                owner=st.text_input("Responsável", user_name())
            with c2:
                kr=st.text_area("Resultado-chave", placeholder="Ex.: Manter margem líquida acima de 15% por 3 meses")
                target=st.text_input("Meta")
                current=st.text_input("Valor atual")
                conf=st.slider("Confiança",0,10,5)
                due=st.date_input("Prazo", value=dt.date.today()+dt.timedelta(days=90), format="DD/MM/YYYY")
                status=st.selectbox("Status",["Planejado","Em andamento","Em risco","Concluído"])
            if st.form_submit_button("Salvar OKR"):
                db.insert("okr_records",dict(id=str(uuid.uuid4()),quarter=q,objective=obj,key_result=kr,target=target,current_value=current,confidence=conf,owner=owner,due_date=due.strftime(DATE_DB),status=status,created_by=user_name()))
                st.success("OKR salvo."); st.rerun()
    df=okr_df()
    if df.empty:
        st.info("Nenhum OKR salvo. Recomendo começar com 1 objetivo e até 3 resultados-chave.")
        return
    show=df.copy(); show["due_date"]=show.due_date.apply(date_br)
    st.dataframe(show[["quarter","objective","key_result","target","current_value","confidence","owner","due_date","status","created_by"]], use_container_width=True, hide_index=True)


def page_minha_empresa():
    p=ensure_profile();header("Minha Empresa","A verdade inicial da empresa: perfil, custos, caixa, estoque e base para o aconselhamento executivo.");readonly_warning()
    st.markdown("<div class='exec-principle'><b>Como pensar esta tela:</b> aqui não é apenas cadastro. Estes dados formam a base do diagnóstico. Quanto mais realistas forem os números, melhor será a leitura executiva no Painel, Alertas e Relatórios.</div>", unsafe_allow_html=True)
    if can_edit():
        with st.form("empresa_form"):
            c1,c2=st.columns(2)
            with c1:
                company=st.text_input("Nome da empresa",p.get("company_name",""), help=_help_for("Nome da empresa"))
                owner=st.text_input("Responsável",p.get("owner_name",""), help=_help_for("Responsável"))
                segment=st.text_input("Segmento",p.get("segment",""), help=_help_for("Segmento"))
                size=st.selectbox("Porte",["Pequena","Média","Grande","Hiperporte"],index=["Pequena","Média","Grande","Hiperporte"].index(p.get("business_size","Pequena")) if p.get("business_size","Pequena") in ["Pequena","Média","Grande","Hiperporte"] else 0, help=_help_for("Porte"))
            with c2:
                revenue=money_input("Faturamento mensal estimado",p.get("monthly_revenue"),"emp_revenue",_help_for("Faturamento mensal estimado"))
                fixed=money_input("Custos fixos mensais",p.get("fixed_costs"),"emp_fixed",_help_for("Custos fixos mensais"))
                variable=money_input("Custos variáveis mensais",p.get("variable_costs"),"emp_variable",_help_for("Custos variáveis mensais"))
                stock=money_input("Valor em estoque",p.get("stock_value"),"emp_stock",_help_for("Valor em estoque"))
                initial=money_input("Caixa inicial",p.get("initial_cash"),"emp_initial",_help_for("Caixa inicial"))
            notes=st.text_area("Observações",p.get("notes",""), help="Anote contexto que os números não explicam sozinhos: sazonalidade, dívida, estoque parado, mudança de canal, contrato grande ou problema operacional.")
            if st.form_submit_button("Salvar Minha Empresa"):
                db.update("company_profile","main",dict(company_name=company,owner_name=owner,segment=segment,business_size=size,monthly_revenue=revenue,fixed_costs=fixed,variable_costs=variable,stock_value=stock,initial_cash=initial,notes=notes,updated_at=today_db()))
                st.success("Minha Empresa salva.")
                st.rerun()
    help_title("Leitura rápida da saúde da empresa","Primeira leitura executiva usando cadastro, DRE e fluxo de caixa.")
    m=calc();s,als=alertas();c=st.columns(4)
    with c[0]:metric("Score EXECUTA",f"{s}/100","Com base nos dados atuais")
    with c[1]:metric("Receita bruta",brl(m["receita"]),"DRE ou estimativa")
    with c[2]:metric("Lucro/resultado",brl(m["resultado"]),f"Margem {pct(m['margem'])}")
    with c[3]:metric("Caixa atual",brl(m["caixa"]),"Caixa inicial + movimentos")
    dre=latest_dre()
    st.info(f"Último DRE considerado: {date_br(dre.get('period_start'))} a {date_br(dre.get('period_end'))}.") if dre else st.warning("Ainda não há DRE lançado. A leitura usa estimativas do cadastro da empresa.")

def page_painel():
    header("Painel Executivo","A sala de comando da empresa: números essenciais, leitura de CEO, decisão recomendada e execução da semana.")
    m=calc();s,als=alertas()
    c=st.columns(4)
    with c[0]:metric("Score EXECUTA",f"{s}/100","Saúde geral")
    with c[1]:metric("Caixa atual",brl(m["caixa"]),"Entradas - saídas")
    with c[2]:metric("Capital de giro",brl(m["ncg"]),"Receber + estoque - pagar")
    with c[3]:metric("Resultado",brl(m["resultado"]),f"Margem {pct(m['margem'])}")

    status = "Empresa em controle" if s>=75 else "Empresa em atenção" if s>=45 else "Empresa em risco"
    st.markdown(f"""
    <div class='exec-briefing'>
      <div class='exec-briefing-title'>Briefing executivo da semana</div>
      <div class='exec-briefing-text'><b>{status}.</b> {exec_reading()}</div>
    </div>
    """, unsafe_allow_html=True)

    colA,colB=st.columns(2)
    with colA:
        st.markdown(f"<div class='exec-decision-card'><div class='exec-decision-title'>Decisão recomendada</div><div class='exec-decision-text'>{ceo_next_move()}</div></div>", unsafe_allow_html=True)
    with colB:
        pergunta = ceo_questions()[0] if ceo_questions() else "Qual decisão precisa ser tomada esta semana?"
        st.markdown(f"<div class='exec-decision-card'><div class='exec-decision-title'>Pergunta de CEO</div><div class='exec-decision-text'>{pergunta}</div></div>", unsafe_allow_html=True)

    c1,c2=st.columns(2)
    with c1:metric("Contas a pagar",brl(m["pagar"]),"em aberto")
    with c2:metric("Contas a receber",brl(m["receber"]),"em aberto")

    with st.expander("Conselheiro Executivo — fazer uma pergunta", expanded=False):
        help_title("Pergunte ao Conselheiro Executivo","Use este espaço para receber uma orientação objetiva com base nos dados já lançados.")
        q=st.text_area("Digite sua dúvida executiva",placeholder="Ex.: Devo priorizar caixa, preço ou vendas esta semana?",height=105,key="painel_advisor_q")
        if st.button("Gerar orientação executiva", key="painel_advisor_btn"):
            if not q.strip():
                st.error("Digite uma pergunta.")
            else:
                ans=advisor_answer(q)
                st.session_state.painel_answer=ans
                db.insert("advisor_history",dict(id=str(uuid.uuid4()),asked_at=dt.datetime.now().isoformat(timespec="seconds"),question=q,answer=ans,created_by=user_name()))
        if st.session_state.get("painel_answer"):
            st.markdown(st.session_state.painel_answer)

    help_title("Prioridades da semana","Lista as ações mais próximas ou críticas. Um executivo não gerencia só pelo que sente; gerencia por prioridade, dono e prazo.")
    acts=actions_df()
    if acts.empty:
        st.warning("Crie pelo menos 3 ações no Plano de Ação: uma de caixa, uma de margem e uma de venda/cliente.")
    else:
        show=acts.head(5).copy(); show["due_date"]=show.due_date.apply(date_br)
        st.dataframe(show[["priority","area","action","responsible","due_date","status"]],use_container_width=True,hide_index=True)

    help_title("Movimentos recentes","Últimas entradas e saídas lançadas. Use para conferir se o caixa real está sendo alimentado.")
    df=cash_df()
    if df.empty:
        st.info("Sem movimentos de caixa.")
    else:
        show=df.head(12).copy();show["date"]=show.date.apply(date_br);show["amount"]=show.amount.apply(brl)
        st.dataframe(show[["date","type","category","description","amount","channel","created_by"]],use_container_width=True,hide_index=True)

def page_alerta():
    header("Alertas","Riscos, pontos de atenção e plano prático para corrigir cada problema.")
    s,als=alertas();metric("Score EXECUTA",f"{s}/100","Quanto menor, maior a urgência")
    if not als:
        st.success("Nenhum alerta crítico identificado no momento.")
        return
    for n,t,a in als:
        (st.error if n=="Crítico" else st.warning)(f"**{n}: {t}** — {a}")
        steps=solution_steps(t,a)
        st.markdown("<div class='solution-card'><div class='solution-title'>O que fazer para solucionar</div><ol>" + "".join([f"<li>{x}</li>" for x in steps]) + "</ol></div>", unsafe_allow_html=True)
def page_fluxo():
    header("Fluxo de Caixa","Lançar entradas/saídas, parcelas e controlar histórico financeiro.");readonly_warning()
    if can_edit():
        with st.form("cash_form",clear_on_submit=True):
            help_title("Novo lançamento");c1,c2,c3=st.columns(3)
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
    help_title("Entradas e saídas lançadas");df=cash_df()
    if df.empty:st.info("Sem lançamentos no caixa.")
    else:
        raw=df.reset_index(drop=True).copy()
        show=raw.copy();show["date"]=show.date.apply(date_br);show["amount"]=show.amount.apply(brl)
        rec=selected_row_from_table(raw,show,["date","type","category","description","amount","channel","created_by"],"cash_table_select","Clique em uma linha para editar ou apagar o lançamento selecionado.")
        if can_edit() and rec:
            st.success(f"Linha selecionada: {date_br(rec.get('date'))} • {rec.get('type')} • {brl(rec.get('amount'))}")
            with st.form("edit_cash"):
                c1,c2,c3=st.columns(3)
                with c1:e_date=st.date_input("Data",value=dt.datetime.strptime(str(rec["date"])[:10],DATE_DB).date(),format="DD/MM/YYYY");e_type=st.selectbox("Tipo",["Entrada","Saída"],index=0 if rec.get("type")=="Entrada" else 1)
                with c2:e_cat=st.text_input("Categoria",rec.get("category","") or "");e_amount=money_input("Valor",rec.get("amount",0),"edit_cash_amount")
                with c3:e_channel=st.text_input("Canal/Origem",rec.get("channel","") or "");e_desc=st.text_input("Descrição",rec.get("description","") or "")
                a,b=st.columns(2);save=a.form_submit_button("Salvar edição da linha selecionada");delete=b.form_submit_button("Excluir toda a linha selecionada")
            if save:
                db.update("cash_flow",rec["id"],dict(date=e_date.strftime(DATE_DB),type=e_type,category=e_cat,description=e_desc,amount=e_amount,channel=e_channel));st.success("Lançamento editado.");st.rerun()
            if delete:
                db.delete("cash_flow",rec["id"]);st.success("Linha excluída com sucesso.");st.rerun()
        elif can_edit():
            st.info("Para editar ou excluir, clique em uma linha da tabela acima.")
    help_title("Histórico de contas pagas e recebidas");acc=accounts_df()
    if acc.empty:st.info("Sem contas baixadas ainda.")
    else:
        hist=acc[acc.status.isin(["Pago","Recebido"])].copy()
        if hist.empty:st.info("Ainda não há contas pagas ou recebidas.")
        else:
            hist["due_date"]=hist.due_date.apply(date_br);hist["paid_date"]=hist.paid_date.apply(date_br);hist["amount"]=hist.amount.apply(brl);st.dataframe(hist[["paid_date","kind","supplier_client","description","amount","status","created_by"]],use_container_width=True,hide_index=True)

def page_accounts(kind):
    title="Contas a Pagar" if kind=="Pagar" else "Contas a Receber";closed="Pago" if kind=="Pagar" else "Recebido";header(title,"Visualizar, editar, apagar e baixar contas. Novos lançamentos são criados pelo Fluxo de Caixa.");readonly_warning()
    df=accounts_df();df=df[df.kind==kind].reset_index(drop=True) if not df.empty else df;open_df=df[~df.status.isin([closed])].reset_index(drop=True) if not df.empty else df;closed_df=df[df.status.isin([closed])].reset_index(drop=True) if not df.empty else df
    help_title("Em aberto")
    selected_open=None
    if open_df.empty:st.info("Nenhuma conta em aberto.")
    else:
        show=open_df.copy();show["due_date"]=show.due_date.apply(date_br);show["amount"]=show.amount.apply(brl)
        selected_open=selected_row_from_table(open_df,show,["due_date","supplier_client","description","amount","status","created_by"],f"acc_open_{kind}","Clique em uma linha para editar, baixar ou excluir a conta selecionada.")
    if can_edit() and not df.empty:
        rec=selected_open
        if rec is None:
            st.info("Para editar, baixar ou excluir, clique em uma linha da tabela em aberto acima. Se a conta já foi baixada, use o histórico abaixo apenas para consulta.")
        else:
            st.success(f"Linha selecionada: {date_br(rec.get('due_date'))} • {rec.get('supplier_client')} • {brl(rec.get('amount'))}")
            with st.form(f"edit_acc_{kind}"):
                c1,c2,c3=st.columns(3)
                with c1:due=st.date_input("Vencimento",value=dt.datetime.strptime(str(rec["due_date"])[:10],DATE_DB).date(),format="DD/MM/YYYY");person=st.text_input("Fornecedor/Cliente",rec.get("supplier_client","") or "")
                with c2:desc=st.text_input("Descrição",rec.get("description","") or "");amount=money_input("Valor",rec.get("amount",0),f"edit_amount_{kind}")
                with c3:opts=["Aberto","Pendente",closed];status=st.selectbox("Status",opts,index=opts.index(rec.get("status")) if rec.get("status") in opts else 0);paid=st.date_input("Data de baixa",value=dt.date.today(),format="DD/MM/YYYY")
                a,b,c=st.columns(3);save=a.form_submit_button("Salvar edição");delete=b.form_submit_button("Excluir toda a linha selecionada");baixar=c.form_submit_button(f"Marcar como {closed}")
            if save:
                db.update("accounts",rec["id"],dict(due_date=due.strftime(DATE_DB),supplier_client=person,description=desc,amount=amount,status=status,paid_date=paid.strftime(DATE_DB) if status==closed else ""));st.success("Conta editada.");st.rerun()
            if delete:
                db.delete("accounts",rec["id"]);st.success("Linha excluída com sucesso.");st.rerun()
            if baixar:
                db.update("accounts",rec["id"],dict(status=closed,paid_date=paid.strftime(DATE_DB)))
                db.insert("cash_flow",dict(id=str(uuid.uuid4()),date=paid.strftime(DATE_DB),type="Saída" if kind=="Pagar" else "Entrada",category=f"Conta {kind}",description=rec.get("description","") or "",amount=float(rec.get("amount") or 0),channel=rec.get("supplier_client","") or "",created_by=user_name()))
                st.success(f"Conta marcada como {closed} e lançada no Fluxo de Caixa.");st.rerun()
    help_title("Histórico: já pago/recebido")
    if closed_df.empty:st.info(f"Nenhum registro {closed.lower()} ainda.")
    else:
        show=closed_df.copy();show["due_date"]=show.due_date.apply(date_br);show["paid_date"]=show.paid_date.apply(date_br);show["amount"]=show.amount.apply(brl);st.dataframe(show[["paid_date","due_date","supplier_client","description","amount","status","created_by"]],use_container_width=True,hide_index=True)

def page_dre():
    header("DRE","Preencha e pesquise por período. Datas no padrão dd/mm/aaaa.");readonly_warning()
    help_note("Como preencher o DRE", "Use valores do período escolhido. Se não souber algum resultado calculado, deixe zero: o sistema estima receita líquida, lucro bruto, EBITDA, lucro operacional e lucro líquido.", "Receita bruta 100.000,00; impostos 12.000,00; CMV 45.000,00; despesas 25.000,00.")
    if can_edit():
        with st.form("dre_form",clear_on_submit=True):
            st.subheader("Novo DRE");c0,c1,c2=st.columns(3)
            with c0:ps=st.date_input("Data inicial",value=dt.date.today().replace(day=1),format="DD/MM/YYYY");pe=st.date_input("Data final",value=dt.date.today(),format="DD/MM/YYYY")
            with c1:rb=money_input("Receita bruta",0,"dre_rb","Total vendido/faturado antes de impostos, devoluções e deduções.");ded=money_input("Deduções e impostos",0,"dre_ded","Impostos, devoluções, descontos e abatimentos que reduzem a receita bruta.");rl=money_input("Receita líquida",0,"dre_rl","Receita bruta menos deduções e impostos. Se deixar zero, o sistema calcula automaticamente.");cust=money_input("Custo dos produtos/serviços (CMV/CPV/CSP)",0,"dre_custos","Custo direto do que foi vendido ou entregue: mercadoria, produção ou prestação do serviço.")
            with c2:lb=money_input("Lucro bruto",0,"dre_lb","Receita líquida menos custos diretos. Se deixar zero, o sistema calcula automaticamente.");desp=money_input("Despesas operacionais",0,"dre_desp","Gastos para a empresa funcionar: aluguel, salários, sistemas, marketing, administrativo etc.");rf=money_input("Resultados financeiros",0,"dre_rf","Juros, tarifas, rendimentos, despesas bancárias e efeitos financeiros fora da operação principal.");eb=money_input("EBITDA",0,"dre_ebitda","Resultado operacional antes de juros, impostos, depreciação e amortização. Se deixar zero, o sistema estima.");lo=money_input("Lucro operacional",0,"dre_lo","Resultado da operação antes do lucro líquido final. Se deixar zero, o sistema estima.");ll=money_input("Lucro líquido",0,"dre_ll","Resultado final depois de custos, despesas, impostos e efeitos financeiros. Se deixar zero, o sistema calcula.")
            notes=st.text_area("Observações")
            if st.form_submit_button("Salvar DRE"):
                if rl==0:rl=rb-ded
                if lb==0:lb=rl-cust
                if eb==0:eb=lb-desp
                if lo==0:lo=eb
                if ll==0:ll=lo+rf
                db.insert("dre_records",dict(id=str(uuid.uuid4()),period_start=ps.strftime(DATE_DB),period_end=pe.strftime(DATE_DB),receita_bruta=rb,deducoes_impostos=ded,receita_liquida=rl,custos_produtos_servicos=cust,lucro_bruto=lb,despesas_operacionais=desp,resultados_financeiros=rf,ebitda=eb,lucro_operacional=lo,lucro_liquido=ll,notes=notes,created_by=user_name()))
                st.success("DRE salvo.");st.rerun()
    help_title("Pesquisar por período");c1,c2=st.columns(2);start=c1.date_input("De",value=dt.date.today().replace(day=1),format="DD/MM/YYYY");end=c2.date_input("Até",value=dt.date.today(),format="DD/MM/YYYY")
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
    selected_dre=selected_row_from_table(filt.reset_index(drop=True),show.reset_index(drop=True),["period_start","period_end"]+cols+["created_by"],"dre_table_select","Clique em uma linha para selecionar um DRE lançado.")
    if can_edit() and selected_dre:
        st.success(f"DRE selecionado: {date_br(selected_dre.get('period_start'))} a {date_br(selected_dre.get('period_end'))}")
        if st.button("Excluir DRE selecionado", key="delete_dre_selected"):
            db.delete("dre_records", selected_dre["id"]); st.success("DRE excluído com sucesso."); st.rerun()
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
    raw=df.reset_index(drop=True).copy(); show=raw.copy();show["due_date"]=show.due_date.apply(date_br)
    rec=selected_row_from_table(raw,show,["priority","area","action","responsible","due_date","status","created_by"],"actions_table_select","Clique em uma linha para selecionar uma ação.")
    if can_edit() and rec:
        st.success(f"Ação selecionada: {rec.get('priority')} • {rec.get('area')}")
        c1,c2=st.columns(2)
        new_status=c1.selectbox("Alterar status da ação selecionada",["Pendente","Em andamento","Concluído"],index=["Pendente","Em andamento","Concluído"].index(rec.get("status")) if rec.get("status") in ["Pendente","Em andamento","Concluído"] else 0,key="action_status_selected")
        if c1.button("Salvar status",key="save_action_status"):
            db.update("action_plan",rec["id"],dict(status=new_status)); st.success("Status atualizado."); st.rerun()
        if c2.button("Excluir toda a linha selecionada",key="delete_action_selected"):
            db.delete("action_plan",rec["id"]); st.success("Linha excluída com sucesso."); st.rerun()
def page_calendar():
    header("Calendário","Agenda com compromissos e vencimentos: verde para contas a receber, vermelho para contas a pagar.")
    readonly_warning();colors={"Baixa":"#29E6A7","Média":"#FFCC66","Alta":"#FF8A3D","Crítica":"#FF5C7A"}
    if can_edit():
        with st.form("event_form",clear_on_submit=True):
            c1,c2,c3=st.columns(3)
            with c1:ed=st.date_input("Data",value=dt.date.today(),format="DD/MM/YYYY");et=st.text_input("Horário",placeholder="Ex.: 14:30")
            with c2:title=st.text_input("Compromisso");cat=st.selectbox("Categoria",["Financeiro","Comercial","Operação","Reunião","Cliente","Pessoal","Outro"])
            with c3:level=st.selectbox("Nível",["Baixa","Média","Alta","Crítica"]);notes=st.text_input("Observações")
            if st.form_submit_button("Adicionar compromisso"):
                db.insert("calendar_events",dict(id=str(uuid.uuid4()),event_date=ed.strftime(DATE_DB),event_time=et,title=title,category=cat,level=level,color=colors[level],notes=notes,created_by=user_name()))
                st.success("Compromisso adicionado.");st.rerun()
    st.markdown("<div class='tooltip-box'><span class='help-badge'>?</span><b>Como ler o calendário</b><br><span class='calendar-dot' style='background:#29E6A7'></span> verde = conta a receber. <span class='calendar-dot' style='background:#FF5C7A'></span> vermelho = conta a pagar. Os compromissos aparecem com a cor do nível escolhido.</div>", unsafe_allow_html=True)
    today=dt.date.today();c1,c2=st.columns(2);month=c1.selectbox("Mês",list(range(1,13)),index=today.month-1,format_func=lambda m:f"{m:02d}");year=c2.number_input("Ano",min_value=2020,max_value=2100,value=today.year,step=1)
    events=events_df();acc=accounts_df();ms=dt.date(int(year),int(month),1);me=dt.date(int(year),int(month),pycal.monthrange(int(year),int(month))[1])
    mev=events[(events.event_date>=ms.strftime(DATE_DB))&(events.event_date<=me.strftime(DATE_DB))] if not events.empty else events
    month_acc=acc[(acc.due_date>=ms.strftime(DATE_DB))&(acc.due_date<=me.strftime(DATE_DB))&(~acc.status.isin(["Pago","Recebido"]))] if not acc.empty else acc
    help_title("Calendário do mês");cal=pycal.Calendar(firstweekday=0)
    for week in cal.monthdatescalendar(int(year),int(month)):
        cols=st.columns(7)
        for i,d in enumerate(week):
            day=d.strftime(DATE_DB)
            de=mev[mev.event_date==day] if not mev.empty else pd.DataFrame()
            da=month_acc[month_acc.due_date==day] if not month_acc.empty else pd.DataFrame()
            mut="opacity:.35;" if d.month!=int(month) else "";chips=""
            if not da.empty:
                rec_count=len(da[da.kind=="Receber"]); pay_count=len(da[da.kind=="Pagar"])
                if rec_count: chips+=f'<span class="event-chip" style="background:#29E6A7">● Receber {rec_count}</span>'
                if pay_count: chips+=f'<span class="event-chip" style="background:#FF5C7A;color:#fff">● Pagar {pay_count}</span>'
            if not de.empty:
                for _,ev in de.head(3).iterrows():chips+=f'<span class="event-chip" style="background:{ev.get("color") or "#00D1FF"}">{ev.get("event_time") or ""} {str(ev.get("title") or "")[:12]}</span>'
            cols[i].markdown(f'<div class="calendar-day" style="{mut}"><div class="calendar-date">{d.day}</div>{chips}</div>',unsafe_allow_html=True)
    help_title("Compromissos do mês")
    if mev.empty:st.info("Sem compromissos no mês.")
    else:
        raw=mev.reset_index(drop=True).copy();show=raw.copy();show["event_date"]=show.event_date.apply(date_br)
        rec=selected_row_from_table(raw,show,["event_date","event_time","title","category","level","notes","created_by"],"calendar_table_select","Clique em uma linha para selecionar um compromisso.")
        if can_edit() and rec:
            st.success(f"Compromisso selecionado: {date_br(rec.get('event_date'))} • {rec.get('event_time')} • {rec.get('title')}")
            if st.button("Excluir compromisso selecionado", key="delete_calendar_selected"):
                db.delete("calendar_events", rec["id"]); st.success("Compromisso excluído com sucesso."); st.rerun()
    st.subheader("Vencimentos do mês")
    if month_acc.empty: st.info("Nenhuma conta a pagar ou receber no mês.")
    else:
        show=month_acc.copy();show["due_date"]=show.due_date.apply(date_br);show["amount"]=show.amount.apply(brl)
        st.dataframe(show[["due_date","kind","supplier_client","description","amount","status"]],use_container_width=True,hide_index=True)
def page_indicadores():
    header("Indicadores","KPIs essenciais para decisão: margem, liquidez, execução, validação e risco.")
    m=calc();s,als=alertas();fb=feedback_df();acts=actions_df();acc=accounts_df()
    concl=float((acts.status=="Concluído").mean()*100) if not acts.empty and "status" in acts else 0
    atrasadas=0
    if not acc.empty:
        hoje=today_db(); atrasadas=len(acc[(acc.due_date<hoje)&(~acc.status.isin(["Pago","Recebido"]))])
    avgfb=float(fb.score.mean()) if not fb.empty else 0
    c=st.columns(5)
    with c[0]:metric("Score",f"{s}/100","")
    with c[1]:metric("Margem",pct(m["margem"]),"lucro/receita")
    with c[2]:metric("Ponto de equilíbrio",brl(m["ponto_equilibrio"]),"mínimo estimado")
    with c[3]:metric("Execução",pct(concl),"ações concluídas")
    with c[4]:metric("MVP",f"{avgfb:.1f}/10" if avgfb else "sem dados","nota média")
    st.subheader("Interpretação")
    linhas=[]
    linhas.append(["Margem",pct(m["margem"]),"Boa" if m["margem"]>=15 else "Atenção" if m["margem"]>=5 else "Crítica","Margem baixa limita crescimento e aumenta dependência de caixa."])
    linhas.append(["Capital de giro",brl(m["ncg"]),"Atenção" if m["ncg"]>m["receita"] else "Boa","Quanto maior a necessidade de giro, mais cuidado antes de crescer."])
    linhas.append(["Contas atrasadas",str(atrasadas),"Crítica" if atrasadas else "Boa","Atraso financeiro corrói confiança e previsibilidade."])
    linhas.append(["Execução",pct(concl),"Boa" if concl>=70 else "Atenção","Sem dono, prazo e rotina, plano não vira resultado."])
    st.dataframe(pd.DataFrame(linhas,columns=["Indicador","Valor","Status","Leitura executiva"]),use_container_width=True,hide_index=True)

def page_rotina_executiva():
    header("Rotina Executiva","Reunião semanal, foco, riscos e próximos passos. O sistema precisa virar hábito, não apenas cadastro.")
    readonly_warning()
    if can_edit():
        with st.form("routine_form",clear_on_submit=True):
            c1,c2=st.columns(2)
            with c1:
                d=st.date_input("Data da rotina",value=dt.date.today(),format="DD/MM/YYYY")
                rtype=st.selectbox("Tipo",["Reunião semanal EXECUTA","Revisão financeira","Revisão comercial","Revisão operacional","Revisão de produto/MVP"])
                score=st.slider("Nota da semana",0,100,60,help="0 = semana fora de controle; 100 = operação saudável e com execução forte.")
            with c2:
                focus=st.text_input("Foco principal da semana",placeholder="Ex.: recuperar caixa, vender mais, reduzir atrasos")
                risks=st.text_area("Riscos percebidos")
            decisions=st.text_area("Decisões tomadas")
            next_actions=st.text_area("Próximas ações com dono e prazo")
            if st.form_submit_button("Salvar rotina"):
                db.insert("executive_routines",dict(id=str(uuid.uuid4()),routine_date=d.strftime(DATE_DB),routine_type=rtype,score=score,focus=focus,decisions=decisions,risks=risks,next_actions=next_actions,created_by=user_name()))
                st.success("Rotina registrada.");st.rerun()
    df=routines_df()
    if df.empty: st.info("Nenhuma rotina registrada ainda."); return
    show=df.copy(); show["routine_date"]=show.routine_date.apply(date_br)
    st.dataframe(show[["routine_date","routine_type","score","focus","decisions","risks","next_actions","created_by"]],use_container_width=True,hide_index=True)

def page_validacao_mvp():
    header("Feedback de Mercado","Coleta de feedback real: problema, valor percebido, objeções e melhorias prioritárias.")
    readonly_warning()
    if can_edit():
        with st.form("mvp_feedback_form",clear_on_submit=True):
            c1,c2=st.columns(2)
            with c1:
                d=st.date_input("Data",value=dt.date.today(),format="DD/MM/YYYY")
                person=st.text_input("Pessoa/empresa entrevistada")
                profile=st.text_input("Perfil",placeholder="Ex.: pequeno varejo, prestador, e-commerce, gestor financeiro")
                score=st.slider("Nota de valor percebido",0,10,7,help="Quanto essa pessoa percebe valor real no produto?")
            with c2:
                status=st.selectbox("Status",["Novo","Entrevistado","Priorizar","Implementado","Descartado"])
                main_pain=st.text_area("Principal dor/problema")
            liked=st.text_area("O que a pessoa mais gostou")
            missing=st.text_area("O que faltou / melhoria pedida")
            objection=st.text_area("Objeção para usar/pagar")
            if st.form_submit_button("Salvar feedback"):
                db.insert("mvp_feedback",dict(id=str(uuid.uuid4()),feedback_date=d.strftime(DATE_DB),person=person,profile=profile,score=score,main_pain=main_pain,liked=liked,missing=missing,objection=objection,status=status,created_by=user_name()))
                st.success("Feedback salvo."); st.rerun()
    df=feedback_df()
    if df.empty: st.info("Nenhum feedback de MVP registrado ainda."); return
    avg=float(df.score.mean()); high=len(df[df.score>=8]); low=len(df[df.score<=5])
    c=st.columns(3)
    with c[0]:metric("Nota média",f"{avg:.1f}/10","valor percebido")
    with c[1]:metric("Promotores",str(high),"notas 8 a 10")
    with c[2]:metric("Riscos",str(low),"notas 0 a 5")
    show=df.copy(); show["feedback_date"]=show.feedback_date.apply(date_br)
    st.dataframe(show[["feedback_date","person","profile","score","main_pain","liked","missing","objection","status","created_by"]],use_container_width=True,hide_index=True)

def page_decisoes():
    header("Decisões","Registro executivo para evitar decisões soltas. Toda decisão importante precisa ter motivo, dono, prazo e resultado esperado.")
    readonly_warning()
    if can_edit():
        with st.form("decision_form",clear_on_submit=True):
            c1,c2=st.columns(2)
            with c1:
                dd=st.date_input("Data da decisão",value=dt.date.today(),format="DD/MM/YYYY")
                area=st.selectbox("Área",["Financeiro","Comercial","Operação","Produto/MVP","Pessoas","Tecnologia","Governança"])
                owner=st.text_input("Responsável",user_name())
            with c2:
                due=st.date_input("Prazo de revisão",value=dt.date.today()+dt.timedelta(days=14),format="DD/MM/YYYY")
                status=st.selectbox("Status",["Aberta","Em teste","Concluída","Cancelada"])
            decision=st.text_area("Decisão")
            reason=st.text_area("Por que essa decisão foi tomada?")
            expected=st.text_area("Resultado esperado / métrica de sucesso")
            if st.form_submit_button("Registrar decisão"):
                db.insert("decision_log",dict(id=str(uuid.uuid4()),decision_date=dd.strftime(DATE_DB),area=area,decision=decision,reason=reason,expected_result=expected,owner=owner,due_date=due.strftime(DATE_DB),status=status,created_by=user_name()))
                st.success("Decisão registrada."); st.rerun()
    df=decisions_df()
    if df.empty: st.info("Nenhuma decisão registrada ainda."); return
    show=df.copy(); show["decision_date"]=show.decision_date.apply(date_br); show["due_date"]=show.due_date.apply(date_br)
    st.dataframe(show[["decision_date","area","decision","reason","expected_result","owner","due_date","status","created_by"]],use_container_width=True,hide_index=True)


def page_relatorios():
    header("Relatórios","Mapa de crescimento e relatório executivo para revisão semanal ou mensal.")
    help_title("Mapa de Crescimento","Mostra onde a empresa está mais forte ou frágil: financeiro, caixa, execução, operação e liderança.")
    st.caption("Use esta leitura para escolher o que corrigir primeiro. Crescimento sem base aumenta o problema.")
    render_growth_lanes()
    st.markdown("<div class='exec-warning'><b>Regra executiva:</b> não acelere contratação, estoque ou marketing quando caixa, margem e execução ainda estão frágeis. Primeiro corrija a base; depois escale.</div>", unsafe_allow_html=True)

    help_title("Relatório Executivo","Texto consolidado para reunião de gestão, revisão semanal ou acompanhamento mensal.")
    m=calc();s,als=alertas();acts=actions_df()
    report = "# Relatório Executivo EXECUTA\n\n"
    report += f"Data: {date_br(dt.date.today())}\n\n"
    report += "## 1. Saúde geral\n"
    report += f"Score EXECUTA: {s}/100\nCaixa atual: {brl(m['caixa'])}\nCapital de giro: {brl(m['ncg'])}\nResultado: {brl(m['resultado'])}\nMargem: {pct(m['margem'])}\n\n"
    report += "## 2. Leitura executiva\n" + exec_reading() + "\n\n"
    report += "## 3. Decisão recomendada\n" + ceo_next_move() + "\n\n"
    report += "## 4. Mapa de crescimento\n"
    for title,score,body,action in growth_lanes():
        report += f"- {title}: {score}/100 — {body} Ação recomendada: {action}\n"
    report += "\n## 5. Alertas e correções\n"
    if als:
        for n,t,a in als:
            report += f"- {n}: {t} — {a}\n"
            for step in solution_steps(t,a):
                report += f"  - Fazer: {step}\n"
    else:
        report += "Nenhum alerta crítico identificado.\n"
    report += "\n## 6. Plano de ação\n"
    if acts.empty:
        report += "Nenhuma ação cadastrada. Recomendação: criar 3 ações com responsável e prazo.\n"
    else:
        for _,r in acts.head(10).iterrows():
            report += f"- [{r.get('status')}] {r.get('area')} — {r.get('action')} | Responsável: {r.get('responsible')} | Prazo: {date_br(r.get('due_date'))}\n"
    st.text_area("Relatório gerado",report,height=460)
    st.download_button("Baixar relatório .md",report,file_name=f"relatorio_executa_{today_db()}.md",mime="text/markdown")


def page_metodo():
    header("O que é o Método EXECUTA","Um método prático para transformar dados em decisão e decisão em execução.")
    st.markdown('<div class="exec-note"><b>Princípio executivo:</b> a empresa só deve crescer quando prova ter caixa, margem, demanda, processo e capacidade de execução. Crescer sem isso não resolve o problema; apenas aumenta o tamanho dele.</div>', unsafe_allow_html=True)
    help_title("Como usar o método dentro do app","O usuário não precisa decorar teoria. Ele segue a rotina: cadastrar realidade, ler painel, decidir, executar e revisar.")
    st.dataframe(pd.DataFrame([
        ["1. Minha Empresa", "Definir a realidade inicial", "Dados-base: segmento, porte, caixa, custos, estoque e observações."],
        ["2. Fluxo + Contas", "Controlar sobrevivência", "Entradas, saídas, vencimentos, recebíveis e pressão de caixa."],
        ["3. DRE", "Separar lucro de caixa", "Mostra se a operação gera resultado econômico real."],
        ["4. Painel + Alertas", "Ler como executivo", "O sistema aponta risco, interpretação e decisão recomendada."],
        ["5. Plano de Ação", "Executar", "Toda melhoria precisa de responsável, prazo e status."],
        ["6. Relatórios", "Revisar", "Consolida crescimento, gargalos, alertas e próximas decisões."],
    ],columns=["Etapa","Função","Como aplicar"]),use_container_width=True,hide_index=True)
    help_title("Sete frentes do EXECUTA","As frentes que ajudam o empresário a estruturar a empresa sem olhar apenas para dinheiro.")
    for i,(t,d) in enumerate(EXECUTA_FRENTES,1):
        st.markdown(f"**{i}. {t}** — {d}")
    help_title("10 pilares","Princípios usados para interpretar a empresa.")
    st.write(", ".join(PILARES))
    help_title("Critério de crescimento","Quando a empresa pode começar a acelerar com menos risco.")
    st.warning("Antes de contratar, comprar mais estoque, abrir novo canal ou investir pesado em marketing, confirme: margem positiva, caixa suficiente, operação repetível, contas controladas e ação com dono claro.")


def advisor_answer(q):
    m=calc(); s,als=alertas(); ql=q.lower(); acts=actions_df(); cash=cash_df(); dre=dre_df(); acc=accounts_df()
    temas=[]
    if any(x in ql for x in ["caixa","dinheiro","capital","giro","pagar","receber"]):temas.append("caixa")
    if any(x in ql for x in ["margem","lucro","preço","markup","dre","custo"]):temas.append("margem")
    if any(x in ql for x in ["venda","cliente","canal","comercial","marketing","oferta"]):temas.append("comercial")
    if any(x in ql for x in ["processo","estoque","operação","retrabalho","escala"]):temas.append("operacao")
    if any(x in ql for x in ["dono","equipe","liderança","delegar","gestor"]):temas.append("lideranca")
    if not temas:temas=["geral"]

    out=[]
    out.append(f"# Conselho Executivo EXECUTA\n\n**Pergunta:** {q}\n\n## 1. Diagnóstico sem rodeio\nScore atual: **{s}/100**. Caixa: **{brl(m['caixa'])}**. Resultado: **{brl(m['resultado'])}**. Margem: **{pct(m['margem'])}**. Capital de giro: **{brl(m['ncg'])}**.")
    if cash.empty:
        out.append("**Ponto crítico:** o fluxo de caixa ainda está vazio. Antes de qualquer decisão sofisticada, registre entradas e saídas reais.")
    if dre.empty:
        out.append("**Ponto crítico:** ainda não há DRE. Sem DRE, você pode confundir faturamento com lucro.")
    if als:
        out.append("## 2. Alertas que eu não ignoraria\n"+"\n".join(f"- **{n}: {t}** — {a}" for n,t,a in als))
    else:
        out.append("## 2. Alertas\nNenhum alerta crítico apareceu, mas continue revisando caixa, margem e execução semanalmente.")

    out.append("## 3. Decisão recomendada\n"+ceo_next_move())

    bloco=[]
    if "caixa" in temas: bloco.append("**Caixa:** priorize liquidez. Veja vencimentos, cobre recebíveis, renegocie saídas e corte gasto que não gere venda, margem ou operação essencial.")
    if "margem" in temas: bloco.append("**Margem:** revise preço, custo direto, imposto, taxa, frete e desconto. Vender mais com margem ruim acelera prejuízo.")
    if "comercial" in temas: bloco.append("**Venda:** não busque apenas volume. Priorize canal, produto ou cliente que gere margem, recorrência e previsibilidade.")
    if "operacao" in temas: bloco.append("**Operação:** padronize a rotina crítica antes de escalar. Processo fraco cresce como gargalo.")
    if "lideranca" in temas: bloco.append("**Liderança:** decisão sem responsável e prazo não é decisão; é intenção.")
    if "geral" in temas: bloco.append("Comece pela verdade: caixa, DRE, contas, margem e plano de ação. O resto vem depois.")
    out.append("## 4. Leitura por tema\n"+"\n".join(f"- {b}" for b in bloco))

    out.append("## 5. Perguntas de CEO\n"+"\n".join(f"- {x}" for x in ceo_questions()[:5]))

    out.append("## 6. Plano prático de 7 dias\n1. Atualizar Fluxo de Caixa.\n2. Conferir Contas a Pagar e Contas a Receber.\n3. Lançar ou revisar o DRE.\n4. Criar 3 ações com responsável e prazo.\n5. Revisar Alertas e transformar cada alerta crítico em ação.\n6. Abrir Relatórios e verificar o Mapa de Crescimento.\n7. Voltar ao Painel e decidir o próximo movimento da semana.")

    if acts.empty:
        out.append("\n**Observação crítica:** ainda não há plano de ação. Sem execução registrada, o sistema vira análise sem consequência.")
    return "\n\n".join(out)

def page_advisor():
    header("Conselheiro Executivo","Um conselheiro executivo interno: interpreta números, aponta riscos, faz perguntas difíceis e transforma diagnóstico em ação.");q=st.text_area("Digite sua dúvida executiva",placeholder="Ex.: Devo investir em tráfego agora ou corrigir margem primeiro?",height=130)
    if st.button("Gerar orientação"):
        if not q.strip():st.error("Digite uma pergunta.")
        else:
            ans=advisor_answer(q);st.session_state.last_answer=ans;db.insert("advisor_history",dict(id=str(uuid.uuid4()),asked_at=dt.datetime.now().isoformat(timespec="seconds"),question=q,answer=ans,created_by=user_name()))
    if st.session_state.get("last_answer"):st.markdown(st.session_state.last_answer)


def collaborator_count_for_user():
    # Nesta versão simples, contamos usuários da empresa com mesmo perfil normal.
    # O limite de colaborador para usuário comum é controlado por quantidade total criada por ele de forma operacional.
    # Como ainda não temos created_by_user_id no banco antigo, aplicamos regra prática: usuário comum só cria se a empresa tiver até 2 usuários.
    users = db.select("app_users")
    return max(0, len(users)-1)

def page_users():
    header("Usuários","Controle de acesso da empresa.")
    if role()=="somente leitura":
        st.error("Você não tem permissão para acessar este módulo.")
        return

    current_user = st.session_state.get("user", {})

    # DONO DO APP: visão geral completa
    if is_owner():
        st.markdown("<div class='exec-principle'><b>Você está como Dono do App.</b><br>Você pode criar empresas, criar administradores para clientes e visualizar a estrutura geral do sistema.</div>", unsafe_allow_html=True)

        help_title("Empresas cadastradas","Aqui aparecem todas as empresas/clientes do sistema. Somente o dono do app deve enxergar esta área.")
        comps=db.select("companies", order="created_at")
        if comps:
            st.dataframe(pd.DataFrame(comps)[["name","owner_name","active","created_at"]], use_container_width=True, hide_index=True)
        else:
            st.info("Nenhuma empresa encontrada.")

        help_title("Criar nova empresa / cliente","Crie uma empresa separada com administrador próprio. Os dados dela não aparecem para outras empresas.")
        with st.expander("Criar nova empresa com administrador próprio", expanded=False):
            with st.form("new_company_form"):
                code=st.text_input("Código de criação",type="password", key="new_company_code")
                company_name=st.text_input("Nome da nova empresa", placeholder="Ex.: Empresa do Cliente", key="new_company_name")
                admin_name=st.text_input("Nome do administrador da nova empresa", key="new_company_admin")
                admin_email=st.text_input("E-mail do administrador", key="new_company_email")
                admin_pw=st.text_input("Senha inicial", type="password", key="new_company_pw")
                if st.form_submit_button("Criar nova empresa e administrador"):
                    if code!=secret("SETUP_CODE","executa2026"):
                        st.error("Código incorreto.")
                    else:
                        cid = create_company_record(company_name, admin_name)
                        ok,msg = create_user(admin_name, admin_email, admin_pw, "administrador", cid)
                        if ok:
                            st.success("Nova empresa criada com administrador próprio. Os dados dela ficarão separados.")
                        else:
                            st.error(msg)

        help_title("Todos os usuários da empresa atual","Aqui você vê e cria usuários para a empresa selecionada/logada.")
        users=db.select("app_users",order="created_at")
        if users:
            st.dataframe(pd.DataFrame(users)[["name","email","role","active","created_at"]],use_container_width=True,hide_index=True)
        else:
            st.info("Nenhum usuário nesta empresa.")

        with st.expander("Criar usuário na empresa atual", expanded=False):
            with st.form("owner_create_user_current_company"):
                code=st.text_input("Código de criação",type="password", key="owner_code")
                name=st.text_input("Nome", key="owner_user_name")
                email=st.text_input("E-mail", key="owner_user_email")
                pw=st.text_input("Senha",type="password", key="owner_user_pw")
                rv=st.selectbox("Perfil",["administrador","usuario","somente leitura"], key="owner_user_role")
                if st.form_submit_button("Criar usuário"):
                    if code!=secret("SETUP_CODE","executa2026"):
                        st.error("Código incorreto.")
                    else:
                        ok,msg=create_user(name,email,pw,rv,current_company_id())
                        st.success(msg) if ok else st.error(msg)
        return

    # ADMINISTRADOR DA EMPRESA: só própria empresa
    if is_company_admin():
        st.markdown(f"<div class='exec-principle'><b>Empresa atual:</b> {_html.escape(str(current_company_name()))}<br>Você é administrador desta empresa. Pode criar usuários apenas para esta empresa.</div>", unsafe_allow_html=True)
        users=db.select("app_users",order="created_at")
        if users:
            st.dataframe(pd.DataFrame(users)[["name","email","role","active","created_at"]],use_container_width=True,hide_index=True)
        else:
            st.info("Nenhum usuário nesta empresa.")

        with st.expander("Criar usuário para esta empresa", expanded=False):
            with st.form("company_admin_create_user"):
                code=st.text_input("Código de criação",type="password", key="admin_code")
                name=st.text_input("Nome", key="admin_user_name")
                email=st.text_input("E-mail", key="admin_user_email")
                pw=st.text_input("Senha",type="password", key="admin_user_pw")
                rv=st.selectbox("Perfil",["usuario","somente leitura"], key="admin_user_role")
                if st.form_submit_button("Criar usuário"):
                    if code!=secret("SETUP_CODE","executa2026"):
                        st.error("Código incorreto.")
                    else:
                        ok,msg=create_user(name,email,pw,rv,current_company_id())
                        st.success(msg) if ok else st.error(msg)
        return

    # USUÁRIO COMUM: vê apenas a própria conta e pode criar 1 colaborador
    if role()=="usuario":
        st.markdown(f"<div class='exec-principle'><b>Sua conta</b><br>Você está vinculado à empresa: {_html.escape(str(current_company_name()))}. Você não vê outras empresas nem cria novas empresas.</div>", unsafe_allow_html=True)
        own = pd.DataFrame([{
            "name": current_user.get("name",""),
            "email": current_user.get("email",""),
            "role": current_user.get("role",""),
            "empresa": current_company_name()
        }])
        st.dataframe(own,use_container_width=True,hide_index=True)

        users_company = db.select("app_users")
        if len(users_company) >= 2:
            st.info("Esta empresa já possui colaborador cadastrado. Para criar mais acessos, peça ao administrador da empresa.")
            return

        with st.expander("Criar 1 colaborador para esta empresa", expanded=False):
            with st.form("normal_user_create_one_collaborator"):
                name=st.text_input("Nome do colaborador")
                email=st.text_input("E-mail do colaborador")
                pw=st.text_input("Senha inicial",type="password")
                rv=st.selectbox("Perfil do colaborador",["usuario","somente leitura"])
                if st.form_submit_button("Criar colaborador"):
                    ok,msg=create_user(name,email,pw,rv,current_company_id())
                    st.success(msg) if ok else st.error(msg)
        return
def main():
    if "user" not in st.session_state:login_screen();return
    page=sidebar()
    override=topbar()
    if override:
        page=override
    if page=="Minha Empresa":page_minha_empresa()
    elif page=="Painel":page_painel()
    elif page=="Fluxo de Caixa":page_fluxo()
    elif page=="Contas a Pagar":page_accounts("Pagar")
    elif page=="Contas a Receber":page_accounts("Receber")
    elif page=="DRE":page_dre()
    elif page=="Calendário":page_calendar()
    elif page=="Relatórios":page_relatorios()
    elif page=="Plano de Ação":page_actions()
    elif page=="Alertas":page_alerta()
    elif page=="Método EXECUTA":page_metodo()
    elif page=="Usuários":page_users()
    return None
_EXECUTA_APP_RESULT = main()
