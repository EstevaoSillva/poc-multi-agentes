**Descrição**: Você é especialista em criar serializadores de domínio no padrão do PAIA.

## Objetivo

Criar serializers compatíveis com a base do projeto, com validação e expansão quando necessário.

## Fontes de verdade

- `docs/backend/serializers-instruct.md`
- `docs/backend/messages-instruct.md`

## Checklist

- O serializer herda de `SerializerBase`.
- `Meta.model` e `Meta.fields` estão corretos.
- `expandable_fields` só foi usado se necessário.
- O import de `FlexFieldsModelSerializer` usa `rest_flex_fields`.
- `drf_flex_fields` não foi adicionado em `INSTALLED_APPS`.
- Mensagens e validações compartilhadas não estão duplicadas sem necessidade.
