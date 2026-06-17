# Gestão Executiva EXECUTA — Executive OS v5 FINAL

Esta versão muda a natureza do produto: o sistema deixa de ser apenas um lugar para armazenar dados da empresa e passa a funcionar como um **Conselheiro CEO / Chief of Staff digital** para o empreendedor.

## Posicionamento do produto

O produto não promete apenas controle financeiro. Ele ajuda o empresário a:

- enxergar a verdade do negócio;
- decidir com base em caixa, margem, demanda, operação e liderança;
- transformar diagnóstico em ação semanal;
- validar mercado e oferta;
- registrar decisões e aprender com elas;
- manter foco de 90 dias;
- construir rotina executiva.

## Principais módulos da v5

- **Sala do CEO**: comando central com próximo movimento recomendado, perguntas difíceis e ação rápida.
- **Minha Empresa**: base da realidade empresarial.
- **Painel Executivo**: visão financeira, execução, capital de giro e validação.
- **Indicadores**: score, margem, liquidez, execução, MVP e risco.
- **Marketing e Oferta**: ICP, dor, promessa, oferta, prova, objeções, canais e próximo teste.
- **Unidade Econômica**: ticket, margem, CAC, LTV, payback e leitura de escala.
- **OKRs e 90 Dias**: foco, resultados-chave, responsável, prazo e confiança.
- **Fluxo de Caixa / Contas / DRE**: base financeira.
- **Plano de Ação / Decisões / Rotina Executiva**: governança prática.
- **Validação MVP**: feedback real de usuários/testadores.
- **Conselheiro CEO**: orientação executiva com diagnóstico, decisão, perguntas difíceis e plano de 7 dias.
- **Relatórios**: relatório executivo para sócios/equipe.

## Observação crítica

Para MVP fechado, esta versão é adequada para testar proposta de valor e comportamento de uso. Para venda pública como SaaS, ainda será necessário evoluir: multiempresa por tenant, RLS no Supabase, logs de auditoria, backups, termos de uso, política de privacidade, domínio próprio e esteira de onboarding.

## Atualização no Supabase

Execute `supabase_schema.sql` no SQL Editor quando o Supabase estiver acessível.

## Atualização no GitHub/Streamlit

Substitua estes arquivos no repositório:

- `app.py`
- `requirements.txt`
- `supabase_schema.sql`
- `README.md`
- `CHANGELOG.md`

Depois faça Reboot no Streamlit Cloud.
