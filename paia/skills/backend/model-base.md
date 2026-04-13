**Descrição**: Você é especialista em alinhar a base de modelos do backend para que entidades de domínio herdem corretamente de `ModelBase`.

## Objetivo

Garantir a existência e o uso correto de `core/models.py` com `ModelBase`, conforme o padrão oficial do projeto.

## Fontes de verdade

- `docs/backend/models-instruct.md`
- `docs/backend/architeture-back.md`
- `docs/database/rules.md`

## Regras obrigatórias

1. `ModelBase` deve existir em `core/models.py`.
2. Todo model de domínio deve herdar de `core_models.ModelBase`.
3. O padrão base deve incluir:
   - `id`
   - `created_at`
   - `modified_at`
   - `active`
4. Não criar model de domínio herdando direto de `models.Model`.

## Estrutura esperada

```python
class ModelBase(models.Model):
    id = models.BigAutoField(db_column="id", primary_key=True)
    created_at = models.DateTimeField(db_column="dt_created_at", auto_now_add=True, null=True)
    modified_at = models.DateTimeField(db_column="dt_modified_at", auto_now=True, null=True)
    active = models.BooleanField(db_column="cs_active", default=True)

    class Meta:
        abstract = True
        managed = True
        default_permissions = ("add", "change", "delete", "view")
```

## Checklist

- `ModelBase` existe.
- O nome do campo é `active`, não outro alias.
- O model de domínio herda da base correta.
- O model de domínio segue `db_table`, histórico e convenções do projeto.
