# Arquitetura do Frontend

**Descrição**: Este é o documento-mãe do frontend no PAIA. Ele define a estrutura obrigatória dos artefatos de frontend, registra decisões transversais da stack e aponta para os documentos especializados da camada.

## 1. Papel deste arquivo

Este arquivo deve ser usado para:

- orientar a criação e edição de projetos frontend no padrão do PAIA;
- definir o skeleton base do frontend;
- registrar decisões transversais de arquitetura, UI e integração;
- servir como índice oficial dos documentos especializados de frontend.

Este arquivo não deve ser usado para:

- concentrar toda a implementação de componentes, services, diretivas ou telas;
- duplicar exemplos extensos que já existam nos guias especializados;
- virar um repositório solto de snippets sem contrato arquitetural.

## 2. Estrutura obrigatória do projeto

Todo frontend gerado para o PAIA deve ser criado dentro de `artifacts/frontend/`.

Estrutura base esperada:

```console
artifacts/
    frontend/
        <project_name>/
            src/
                app/
                    core/
                    accounts/
                    shared/
                    <domain_feature>/
```

Diretrizes:

- não criar artefatos de frontend fora de `artifacts/frontend/`;
- considerar `core` e `accounts` como skeleton padrão da aplicação frontend;
- `core` deve concentrar infraestrutura compartilhada da aplicação;
- `accounts` deve concentrar autenticação, sessão, usuário autenticado e fluxos de senha;
- novas features de domínio devem nascer sobre esse skeleton, consumindo `core` e `accounts`.

Exemplo de skeleton:

- `core`: base técnica compartilhada, serviços base, componentes base, guards e configuração;
- `accounts`: login, sessão, refresh token, recuperação de senha e contexto do usuário;
- `schools`: feature de gerenciamento de escolas consumindo `core` e `accounts`.

## 3. Decisões transversais de arquitetura

### 3.1. Stack principal

- o frontend padrão deve usar Angular;
- a aplicação deve operar em modo zoneless;
- componentes novos devem preferir `standalone: true`;
- estado local de UI deve preferir `signal`, `computed` e `effect` quando fizer sentido;
- formulários devem preferir `ReactiveFormsModule`;
- layout e responsividade devem preferir Tailwind com flexbox.

### 3.2. Organização por camadas

- `core/`: camada base obrigatória de infraestrutura, bases, serviços e contratos reutilizáveis;
- `accounts/`: camada base obrigatória para autenticação, sessão e contexto do usuário;
- `shared/`: componentes, pipes, helpers e utilitários visuais reaproveitáveis;
- `<domain_feature>/`: features de negócio, como `schools`, `groups`, `courses` ou equivalentes.

Regra para features de domínio:

- toda nova feature deve nascer sobre o skeleton `core` + `accounts`;
- a feature deve herdar bases técnicas de `core`;
- a feature deve consumir autenticação e contexto de usuário de `accounts`;
- a feature não deve redefinir autenticação global nem contratos base já existentes.

### 3.3. Componentes e UI

- componentes devem preferir arquitetura standalone;
- telas de listagem devem prever paginação;
- telas de listagem e cadastro devem seguir os contratos definidos pelas bases compartilhadas;
- para layouts recorrentes ou mais complexos, preferir encapsular estrutura em componentes reaproveitáveis;
- o frontend deve seguir o style guide de referência informado pelo projeto.

### 3.4. Estado e fluxo

- estado efêmero de tela deve preferir `signal`;
- integração assíncrona deve permanecer clara entre UI, services e bases;
- regras de sessão, token, refresh e usuário autenticado devem ficar em `accounts`;
- lógica de navegação, carga de contexto e infraestrutura compartilhada deve ficar em `core`.

### 3.5. Integração com backend

- autenticação deve seguir o contrato da app `accounts` do backend;
- access token, refresh token e recuperação de sessão devem ser tratados por camada própria de autenticação;
- chamadas HTTP compartilhadas devem preferir um service base ou abstração equivalente;
- rotas e contratos do frontend devem permanecer coerentes com as specs e docs de backend.

## 4. Padrão mínimo para novos componentes

Ao criar componentes novos:

- preferir `standalone: true`;
- usar `inject(...)` quando o padrão do projeto permitir;
- usar `ReactiveFormsModule` para formulários;
- usar `signal` para estado de UI quando houver estado local;
- manter separação entre componente, service e configuração da feature;
- não concentrar autenticação, sessão ou refresh token fora de `accounts`.

## 5. Mapa oficial dos docs de frontend

Use este mapa como ponto de entrada para criação e edição de código frontend:

- [architeture-front.md](/mnt/c/Users/estevao.silva/PycharmProjects/paia/docs/frontend/architeture-front.md): visão geral, skeleton base e decisões transversais do frontend.
- [frameworks-and-libs.md](/mnt/c/Users/estevao.silva/PycharmProjects/paia/docs/frontend/frameworks-and-libs.md): stack e bibliotecas preferenciais.
- [auth-component-instruct.md](/mnt/c/Users/estevao.silva/PycharmProjects/paia/docs/frontend/accounts/auth-component-instruct.md): guia para a feature visual de autenticação.
- [auth.service.md](/mnt/c/Users/estevao.silva/PycharmProjects/paia/docs/frontend/accounts/auth.service.md): guia para service de sessão, login, refresh token e usuário autenticado.
- [base.service.md](/mnt/c/Users/estevao.silva/PycharmProjects/paia/docs/frontend/core/base.service.md): contrato da base de serviços HTTP.
- [base-component-commons.md](/mnt/c/Users/estevao.silva/PycharmProjects/paia/docs/frontend/core/base-component-commons.md): base compartilhada para componentes comuns.
- [base-component-detail.directive.md](/mnt/c/Users/estevao.silva/PycharmProjects/paia/docs/frontend/core/base-component-detail.directive.md): base para telas de formulário e detalhe.
- [base-component-list.directive.md](/mnt/c/Users/estevao.silva/PycharmProjects/paia/docs/frontend/core/base-component-list.directive.md): base para listagens, filtros e paginação.
- [group-geral-instructios.md](/mnt/c/Users/estevao.silva/PycharmProjects/paia/docs/frontend/group/group-geral-instructios.md): mapa funcional do módulo de grupos.
- [group.component.md](/mnt/c/Users/estevao.silva/PycharmProjects/paia/docs/frontend/group/group.component.md): listagem principal de grupos.
- [group-item.component.md](/mnt/c/Users/estevao.silva/PycharmProjects/paia/docs/frontend/group/group-item.component.md): detalhe e edição de grupo.
- [configurations-group.md](/mnt/c/Users/estevao.silva/PycharmProjects/paia/docs/frontend/group/configurations-group.md): filtros e configuração da listagem de grupos.
- [menu-permission.component.md](/mnt/c/Users/estevao.silva/PycharmProjects/paia/docs/frontend/group/menu-permission.component.md): permissões de menu por grupo.
- [group-user.component.md](/mnt/c/Users/estevao.silva/PycharmProjects/paia/docs/frontend/group/group-user.component.md): usuários associados ao grupo.
- [group-user-configurations.md](/mnt/c/Users/estevao.silva/PycharmProjects/paia/docs/frontend/group/group-user-configurations.md): filtros de usuários associados ao grupo.
- [group-user-dialog.component.md](/mnt/c/Users/estevao.silva/PycharmProjects/paia/docs/frontend/group/group-user-dialog.component.md): diálogo de associação de usuários ao grupo.
- [group-user-dialog-configurations.md](/mnt/c/Users/estevao.silva/PycharmProjects/paia/docs/frontend/group/group-user-dialog-configurations.md): filtros do diálogo de usuários.

## 6. Fluxo recomendado para criação de feature frontend

1. Definir o domínio da feature e o contrato com backend.
2. Validar o skeleton do projeto: `core`, `accounts`, bases compartilhadas, services e configuração.
3. Escolher a base correta: componente comum, detalhe ou listagem.
4. Implementar a feature consumindo `core` e `accounts`, sem duplicar autenticação ou infraestrutura.
5. Registrar rotas e integrações da feature.
6. Validar paginação, formulário, UX, responsividade e consistência visual.
7. Atualizar os docs especializados quando surgir nova regra estrutural.

## 7. Checklist arquitetural

Ao criar ou revisar um frontend, valide:

1. [ ] O projeto está dentro de `artifacts/frontend/`.
2. [ ] `core` e `accounts` existem como skeleton base do projeto.
3. [ ] Componentes novos usam o padrão standalone quando aplicável.
4. [ ] O frontend usa zoneless.
5. [ ] Estado local usa `signal` quando fizer sentido.
6. [ ] Formulários usam Reactive Forms.
7. [ ] Listagens seguem paginação e as bases compartilhadas.
8. [ ] Sessão, login, refresh e senha estão centralizados em `accounts`.
9. [ ] A feature nova consome `core` e `accounts` sem duplicar contratos.

## 8. Conclusão

O [architeture-front.md](/mnt/c/Users/estevao.silva/PycharmProjects/paia/docs/frontend/architeture-front.md) deve permanecer como documento raiz do frontend. Ele organiza o uso dos demais guias e registra o skeleton padrão do projeto na camada cliente.
