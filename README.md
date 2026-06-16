
# Gestão Executiva EXECUTA Web — MVP 5 usuários v1

Versão web simples para teste gratuito com até 5 usuários.

## Módulos inclusos

- Painel
- Diagnóstico
- Fluxo de Caixa
- Contas a Pagar
- Contas a Receber
- DRE
- Capital de Giro
- Plano de Ação
- Método EXECUTA
- Conselheiro EXECUTA simples sem API
- Usuários

## Como rodar localmente

```bash
pip install -r requirements.txt
streamlit run app.py
```

Sem Supabase configurado, o app usa SQLite local. Para uso compartilhado real no Streamlit Cloud, configure Supabase.

## Como subir no Streamlit Cloud

1. Crie um projeto no Supabase.
2. Vá em SQL Editor e execute o arquivo `supabase_schema.sql`.
3. Crie um repositório no GitHub com estes arquivos.
4. No Streamlit Cloud, crie um app apontando para `app.py`.
5. Em App > Settings > Secrets, cole:

```toml
SUPABASE_URL = "https://SEU-PROJETO.supabase.co"
SUPABASE_ANON_KEY = "SUA-ANON-KEY"
SETUP_CODE = "executa2026"
```

## Login

O sistema permite criar até 5 usuários usando o código definido em `SETUP_CODE`.

Código padrão de teste: `executa2026`

Troque esse código antes de compartilhar.

## Importante

Esta é uma versão MVP gratuita. Para vender como produto, o ideal depois é reforçar:

- segurança;
- RLS no Supabase;
- permissões por empresa;
- recuperação de senha;
- auditoria;
- backup automático;
- multiempresa;
- assinatura/pagamentos.
