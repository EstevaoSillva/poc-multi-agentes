# Document Model Moderno

## Objetivo

Este guia descreve como a IA deve recriar [`src/app/models/rag/document.model.ts`](/mnt/c/Users/estevao.silva/WebstormProjects/flake-front/src/app/models/rag/document.model.ts) de forma moderna e neutra.

## Papel real do arquivo

O model representa um documento indexado ou enviado para uma feature de busca aumentada, com:

- identificador
- descricao
- referencia ao arquivo
- data de criacao
- data de atualizacao

## Contrato que deve ser preservado

- existir `id`
- existir descricao
- existir localizacao ou referencia do arquivo
- existir timestamps de criacao e atualizacao

## Reimplementacao moderna sugerida

```ts
export interface KnowledgeDocument {
    id: number;
    description: string;
    fileUrl: string;
    createdAt: string;
    updatedAt: string;
}
```

## Prompt recomendado para IA

```text
Recrie um model de documento para uma feature de knowledge base ou RAG.
Preserve id, descricao, referencia do arquivo e timestamps.
Use interface e nomes neutros.
```

## Erros comuns

- tratar caminho de arquivo como objeto complexo sem necessidade
- misturar metadados do documento com estado de upload da UI
