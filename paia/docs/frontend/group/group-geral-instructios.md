# Guia Geral do Módulo Group

**Descrição**: Este documento organiza as instruções especializadas do módulo `group` e define o mapa funcional da feature para programação assistida por IA.

## Objetivo

Este diretorio agrega instrucoes para programacao assistida por IA no modulo [`src/app/components/group`](/mnt/c/Users/estevao.silva/WebstormProjects/flake-front/src/app/components/group).

## Arquivos documentados

- [group.component.md](/mnt/c/Users/estevao.silva/PycharmProjects/paia/docs/frontend/group/group.component.md)
- [configurations-group.md](/mnt/c/Users/estevao.silva/PycharmProjects/paia/docs/frontend/group/configurations-group.md)
- [group-item.component.md](/mnt/c/Users/estevao.silva/PycharmProjects/paia/docs/frontend/group/group-item.component.md)
- [menu-permission.component.md](/mnt/c/Users/estevao.silva/PycharmProjects/paia/docs/frontend/group/menu-permission.component.md)
- [group-user.component.md](/mnt/c/Users/estevao.silva/PycharmProjects/paia/docs/frontend/group/group-user.component.md)
- [group-user-configurations.md](/mnt/c/Users/estevao.silva/PycharmProjects/paia/docs/frontend/group/group-user-configurations.md)
- [group-user-dialog.component.md](/mnt/c/Users/estevao.silva/PycharmProjects/paia/docs/frontend/group/group-user-dialog.component.md)
- [group-user-dialog-configurations.md](/mnt/c/Users/estevao.silva/PycharmProjects/paia/docs/frontend/group/group-user-dialog-configurations.md)

## Mapa funcional do modulo

- `GroupComponent`: listagem principal de grupos.
- `GroupItemComponent`: detalhe e edicao do grupo.
- `MenuPermissionComponent`: permissao de menus por grupo.
- `GroupUserComponent`: usuarios associados ao grupo.
- `GroupUserDialogComponent`: dialogo para associar novos usuarios.
- Arquivos `configurations`: definem filtros reutilizados pelas tabelas.

## Regra geral para IA

Ao editar esse modulo, a IA deve preservar:

- heranca correta das bases `BaseComponentListDirective` e `BaseComponentDetailDirective`
- endpoints em `URLS`
- rotas em `WEB`
- inputs de `Group` usados pelos componentes filhos
- parametros de busca e associacao que a API espera
- consistencia entre filtros, modelos e colunas de tabela
