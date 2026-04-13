# Feature: Home

## Objetivo
Exibir a home da aplicação com menu de navegação, contexto do usuário autenticado e acesso rápido às áreas principais do sistema.

## Regras
- ao clicar em uma opção de menu, a área correspondente deve ser aberta sem perder o contexto da sessão
- o rodapé deve exibir a versão da aplicação quando essa informação existir
- o usuário autenticado deve conseguir acessar alteração de dados e redefinição de senha
- a home não deve depender de regra de negócio espalhada em múltiplos endpoints frágeis

## Tela
Formulário com:
- barra superior com título dinâmico
- menu lateral esquerdo com as opções do sistema
- acesso no canto superior direito para dados do usuário e senha
- rodapé com versão da aplicação

## Backend
Contratos esperados:
- endpoint para dados do usuário autenticado
- endpoint opcional para menu/permissões do usuário
- endpoint opcional para versão ou health da aplicação

Endpoints possíveis:
- `GET /api/accounts/me/`
- `GET /api/accounts/menu/`
- `POST /api/accounts/change-password/`
- `GET /api/health/`

Padrões esperados:
- autenticação obrigatória para dados do usuário
- permissões refletidas no payload do menu, quando aplicável
- mensagens de erro e acesso negado centralizadas
- serializers específicos para payload compacto da home

## Checklist
- a home depende apenas de endpoints estáveis?
- o backend retorna contexto mínimo para montar menu e cabeçalho?
- permissões do usuário são respeitadas?
- a versão ou health da aplicação pode ser exibida de forma confiável?
