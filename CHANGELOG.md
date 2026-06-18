# Changelog

## v6.3 BASE LIMPA

- Retorno controlado à base v6.1.
- Menu lateral reordenado oficialmente.
- Remoção de módulos extras da lateral.
- Painel passa a concentrar leitura de CEO e conselheiro.
- Relatórios concentra mapa de crescimento e relatório executivo.
- Botão superior: O que é o Método EXECUTA.
- Títulos de módulos e seções recebem ? visível com explicação.
- Campos nativos recebem ajuda automática com explicação técnica e exemplo.


## v6.3.1 — Correção dos códigos na tela

- Removido monkey-patch global das funções do Streamlit.
- Corrigido problema em que apareciam métodos/códigos do Streamlit na tela.
- Mantidos balõezinhos visíveis de interrogação nos títulos principais e seções relevantes.
- Versão baseada na v6.3 BASE LIMPA.


## v6.3.2 — Correção final dos códigos na tela

- Corrigido bloco indevido `main() DeltaGenerator` aparecendo no app.
- Alterada chamada final de `main()` para atribuição interna segura.
- Mantida a estrutura da v6.3 base limpa.
- Mantidos os balõezinhos visíveis de interrogação.


## v6.4 FINAL EXECUTIVA

- Refinamento de design e hierarquia visual.
- Painel transformado em briefing executivo.
- Conselheiro Executivo reescrito com linguagem mais forte, clara e prática.
- Método EXECUTA reescrito para orientar o uso real dentro dos módulos existentes.
- Relatórios reescritos para revisão executiva semanal/mensal.
- Mapa de Crescimento recalculado sem depender de módulos removidos.
- Textos e explicações melhorados sem alterar a estrutura oficial do menu.

## v7 MULTIEMPRESA

- Criada tabela `companies`.
- Adicionado `company_id` nas tabelas de dados.
- Implementado isolamento por empresa nas consultas e inserções.
- Usuários agora pertencem a uma empresa específica.
- Módulo Usuários permite criar nova empresa/cliente com administrador próprio.


## v7.1 PERMISSÕES

- Separado Dono do App de Administrador da Empresa.
- Removida criação de novas empresas da conta de administrador da empresa.
- Usuário comum agora vê apenas a própria conta.
- Usuário comum pode criar apenas 1 colaborador na própria empresa.
- Somente leitura não acessa criação de usuários.
- Corrigido menu para manter Contas a Receber nomeado corretamente.
