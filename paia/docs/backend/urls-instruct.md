# Guia de Construção de URLs para IA

**Descrição**: Este documento define como a IA deve criar ou alterar o `urls.py` principal do projeto Django e os `urls.py` das apps. Ele cobre organização de rotas, inclusão de apps e exposição consistente de endpoints.

## Regra Base Obrigatória

O roteamento do backend deve seguir este padrão:

- o projeto possui um `urls.py` principal;
- cada app de domínio possui seu próprio `urls.py`;
- o arquivo principal inclui as apps por `include(...)`;
- rotas de API devem ficar sob prefixo `/api/`;
- a organização deve ser previsível para facilitar manutenção e geração assistida por IA.

Estrutura típica:

```python
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path


urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/accounts/", include("accounts.urls")),
    path("api/core/", include("core.urls")),
    path("api/health/", include("health.urls")),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT) + static(
    settings.MEDIA_URL, document_root=settings.MEDIA_ROOT
)
```

## Instrução para a IA

- manter o `urls.py` principal como ponto central de inclusão das apps;
- criar `urls.py` por app quando a app expuser endpoints;
- usar `path(...)` como padrão, recorrendo a `re_path(...)` apenas quando necessário;
- manter rotas específicas antes de rotas genéricas;
- não expor endpoints internos ou administrativos sem necessidade;
- manter coerência entre prefixo da rota e domínio da app.

## Como estruturar o `urls.py` principal

O arquivo principal deve conter:

1. importações de Django;
2. importações auxiliares apenas quando realmente necessárias;
3. lista `urlpatterns`;
4. inclusão de arquivos estáticos e mídia quando aplicável.

Exemplo:

```python
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path


urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/core/", include("core.urls")),
    path("api/accounts/", include("accounts.urls")),
    path("api/manage_project/", include("manage_project.urls")),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT) + static(
    settings.MEDIA_URL, document_root=settings.MEDIA_ROOT
)
```

## Como estruturar o `urls.py` da app

Cada app deve expor apenas suas próprias rotas.

Exemplo:

```python
from rest_framework.routers import DefaultRouter

from . import viewsets


router = DefaultRouter()
router.register("projects", viewsets.ProjectViewSet, basename="projects")

urlpatterns = router.urls
```

## Regras de organização

- agrupar rotas por domínio de negócio;
- usar nomes de prefixo estáveis, curtos e legíveis;
- evitar registrar múltiplas apps sob prefixos ambíguos;
- preservar compatibilidade com o contrato público da API quando a rota já existir;
- quando houver autenticação especial, documentar a rota com clareza.
- autenticação e usuário autenticado devem preferir o prefixo `/api/accounts/`.

## Regras para arquivos estáticos e mídia

- usar `static(...)` apenas quando o projeto realmente precisar servir arquivos por Django;
- se o projeto usa storage externo, manter coerência com `STATIC_URL` e `MEDIA_URL` definidos em `settings.py`;
- não hardcode caminhos físicos no `urls.py`.

## Segurança

- rotas administrativas devem ser expostas com cautela;
- não incluir apps de desenvolvimento ou debug em ambientes indevidos;
- não expor URLs sensíveis por conveniência;
- nunca colocar credenciais ou segredos em rotas.

## Checklist para a IA

- existe `urls.py` na app?
- o `urls.py` principal inclui a app corretamente?
- as rotas estão sob `/api/`?
- o prefixo da app está coerente com o domínio?
- a ordem das rotas evita conflito entre caminhos específicos e genéricos?
- `STATIC_URL` e `MEDIA_URL` estão sendo usados de forma consistente?

## O Que a IA Não Deve Fazer

- não espalhar rotas principais em múltiplos arquivos sem necessidade;
- não criar prefixos incoerentes com a app;
- não usar regex complexa quando `path(...)` resolve;
- não hardcode URLs absolutas do ambiente;
- não incluir app inexistente no `urlpatterns`.

## Prompt Recomendado

Use este documento quando a tarefa envolver:

- criação do `urls.py` principal;
- criação do `urls.py` de uma nova app;
- inclusão de uma app no roteamento principal;
- reorganização de rotas do backend.
