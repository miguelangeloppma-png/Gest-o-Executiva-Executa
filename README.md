# Gestão Executiva EXECUTA Web — PRO v4 FINAL

Versão refinada para MVP real, combinando gestão financeira, execução, validação de mercado e rotina executiva.

## O que mudou na v4

- Painel executivo com leitura de decisão, não só números.
- Novo módulo **Indicadores** com score, margem, ponto de equilíbrio, execução e validação MVP.
- Novo módulo **Rotina Executiva** para reunião semanal, riscos, decisões e próximos passos.
- Novo módulo **Validação MVP** para registrar feedback real de usuários/testadores.
- Novo módulo **Decisões** para registrar motivo, dono, prazo e resultado esperado.
- Novo módulo **Relatórios** com relatório executivo pronto para baixar.
- **Método EXECUTA** continua fora da lateral e fica no topo.
- **Alerta** permanece na parte inferior da lateral.
- Lateral com módulos maiores e visual mais profissional.
- DRE com explicação em cada campo.
- App mais resistente: se uma tabela do Supabase ainda não existir, evita travar e orienta pelo SQL.

## Base conceitual

O app foi construído para um MVP de verdade: aprender rápido com usuários reais, controlar caixa/margem, e transformar diagnóstico em ação semanal. A lógica do produto segue o princípio do Método EXECUTA: crescer apenas quando há margem, caixa, processo, demanda, liderança e capacidade operacional.

## Atualização no Supabase

Execute `supabase_schema.sql` no SQL Editor. Ele usa `create table if not exists`, então pode ser rodado mais de uma vez.

## Atualização no GitHub/Streamlit

Substitua no repositório:

- `app.py`
- `requirements.txt`
- `supabase_schema.sql`
- `README.md`
- `CHANGELOG.md`

Depois reinicie o app no Streamlit Cloud.

## Observação crítica

Para MVP fechado com poucos usuários, a configuração atual é suficiente para teste. Para vender como SaaS público, é necessário evoluir segurança: RLS no Supabase, multiempresa por tenant, logs de auditoria completos, backup e permissões por registro.


## v5.1 HOTFIX

- Corrigido erro IndexError no Fluxo de Caixa quando a seleção antiga do Streamlit não encontrava mais o registro.
- Fluxo de Caixa agora permite clicar diretamente na linha da tabela e excluir toda a linha selecionada.
- Contas a Pagar/Receber agora permitem clicar diretamente na linha em aberto e excluir toda a linha selecionada.
- DRE, Plano de Ação e Calendário também ganharam seleção direta de linha para ações rápidas.


## EXECUTA Experience OS v6 FINAL

Esta versão foi refinada para melhorar a experiência do usuário e transformar o produto em um sistema de decisão executiva, não apenas em um cadastro financeiro.

### Melhorias de experiência

- Novo módulo **Jornada Guiada** com checklist de implantação do usuário.
- Novo módulo **Mapa de Crescimento** com leitura por frentes: Financeiro, Mercado, Execução, Operação e Liderança.
- Melhorias visuais no layout, cards, espaçamento, hierarquia e navegação.
- Mais explicações técnicas com balões/ajudas em DRE, Marketing e Oferta, Unidade Econômica e pontos críticos.
- Sala do CEO reforçada como central de comando do empreendedor.
- Mantida a base EXECUTA: verdade financeira, mercado, execução, liderança, governança e escala com caixa.

### Filosofia do produto

O app não deve ser percebido como “sistema para guardar dados”. Ele deve ser percebido como um conselheiro operacional: lê informações, aponta gargalos, força decisão, organiza plano e cria rotina de execução.


## v6.1 Refinada

- Reordenado menu lateral: Minha Empresa agora é o primeiro módulo.
- Removidos da lateral: Sala do CEO, Conselheiro CEO, Mapa de Crescimento e Validação MVP.
- Conteúdo de Sala do CEO e Conselheiro CEO foi incorporado ao Painel.
- Mapa de Crescimento foi unido ao módulo Relatórios.
- Alertas agora mostram o que fazer para corrigir cada ponto de atenção.
- Calendário mostra vencimentos de contas: verde para receber e vermelho para pagar.
- Login não mostra mais cadastro público nem quantidade de usuários; primeiro acesso cria administrador, depois só admin cria usuários.
- Ajustes de espaçamento para evitar conteúdo superior cortado.
