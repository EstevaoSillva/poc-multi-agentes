# Feature: Fluxos de domínio com actions e behaviors

## Objetivo
Definir quando uma regra deve ser implementada em `actions.py` e quando deve subir para `behaviors.py` em uma app backend do PAIA.

## Regras
- mutação síncrona, curta e reutilizável deve preferir `actions.py`
- fluxo com muitas etapas, pré-condições e estados intermediários deve preferir `behaviors.py`
- viewsets e serializers não devem carregar regra de domínio complexa
- tasks não devem virar substituto de `actions` ou `behaviors`

## Critérios de decisão
Use `actions.py` quando:
- a operação altera uma ou poucas entidades
- a sequência é curta
- a ação é reaproveitável entre serializer, viewset e task

Use `behaviors.py` quando:
- há múltiplas entidades envolvidas
- o fluxo possui várias etapas encadeadas
- existe transição de estado relevante
- há necessidade de métodos auxiliares por etapa

## Entregáveis
- action para operações CRUD e mutações simples
- behavior para fluxos longos de domínio
- testes cobrindo decisão e efeitos colaterais

## Referências
- `docs/backend/actions-instruct.md`
- `docs/backend/behaviors-instruct.md`
- `docs/backend/tasks-instruct.md`

## Checklist
- a regra foi colocada na camada correta?
- o fluxo longo está legível e com `run()` quando necessário?
- efeitos pós-commit estão fora do serializer e do viewset?
