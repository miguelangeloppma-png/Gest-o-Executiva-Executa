# Gestão Executiva EXECUTA Web — MVP 10 usuários v2

## Mudanças principais

- Limite aumentado para 10 usuários.
- Permissões por perfil:
  - Administrador vê Usuários, cria usuários e pode editar/apagar dados.
  - Usuário lança, edita e apaga dados, mas não cria usuários.
  - Somente leitura só visualiza.
- Diagnóstico virou Minha Empresa e ficou na primeira posição.
- Capital de Giro saiu do menu e aparece no Painel.
- Alertas agora ficam no módulo Alerta.
- Fluxo de Caixa tem parcelas, edição e exclusão.
- Contas a Pagar/Receber são visualização, edição, baixa e exclusão.
- DRE completo com pesquisa por período.
- Calendário/Agenda com categorias e cores.
- Valores aceitam padrão brasileiro, como 50.000,00.

## Atualizar no Supabase

Execute `supabase_schema.sql` no SQL Editor.

## Atualizar no Streamlit

Substitua no GitHub:
- app.py
- requirements.txt
- supabase_schema.sql
- README.md
- CHANGELOG.md

Depois faça Reboot no Streamlit.
