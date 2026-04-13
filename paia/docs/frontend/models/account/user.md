# User Model Moderno

## Objetivo

Este guia descreve como a IA deve recriar [`src/app/models/account/user.ts`](/mnt/c/Users/estevao.silva/WebstormProjects/flake-front/src/app/models/account/user.ts) com abordagem moderna e separacao entre credencial e perfil.

## Papel real do arquivo

O model atual mistura:

- identificacao do usuario
- dados de perfil
- flags de permissao
- senha de login
- grupo e avatar

## Como a IA deve recriar

Na versao moderna, a IA deve separar ao menos dois contratos:

- um tipo para credenciais de autenticacao
- um tipo para perfil/autorizacao do usuario

## Contrato que deve ser preservado

- existir `id`
- existir `url`
- existir `username`
- existir `password` em contrato de credencial, nao necessariamente no perfil persistido
- existir `name` e `email`
- existir dados de ultimo login
- existir flags como `isActive`, `isSuperuser` e `isStaff`
- existir grupos e avatar

## Reimplementacao moderna sugerida

```ts
export interface AccountCredentials {
    login: string;
    secret: string;
}

export interface AccountProfile {
    id: number;
    url: string;
    username: string;
    fullName: string;
    email: string;
    lastLogin?: string;
    active: boolean;
    superuser: boolean;
    staff: boolean;
    groups?: string[];
    avatarUrl?: string;
    primaryGroup?: string;
}
```

## Prompt recomendado para IA

```text
Recrie a modelagem de usuario separando credencial de autenticacao e perfil de usuario.
Preserve identificacao, perfil, flags de permissao, grupos e avatar.
Use nomes neutros e tipagem moderna.
```

## Erros comuns

- manter senha junto do perfil carregado pela aplicacao
- usar `Date` diretamente quando a API trafega string
- misturar naming de API com naming interno sem mapper
