**Descrição:** Você é um especialista em usar o mixin para performance de campos que são expandidos usando a biblioteca drf-flex-fields


Exemplo de serializer com expands

```python
class ModuleSerializer(serializers.SerializerBase):
    class Meta:
        model = models.Module
        fields = '__all__'

    expandable_fields = {
        'courses': (
            'education.ModuleCourseSerializer',
            {
                'source': 'modules_module',
                'fields': ['url', 'id', 'course'],
                'many': True
            }
        ),
    }
```

O mixin

```python
class ExpandViewSetMixin:
    """
    1) Calcula select_related/prefetch_related a partir de expandable_fields (estilo drf-flex-fields).
    2) Reflete fields/omit na query via only()/Prefetch(...only()) ou defer() (opcional).
    >>> Sempre recebe um queryset e devolve um queryset (não usa self.queryset).
    """

    APPLY_ONLY_STRICT: bool = True
    DEFER_HEAVY_FIELDS: Tuple[str, ...] = ("file", "content", "blob", "json")
    INCLUDE_ORDERING_FIELDS: bool = True
    ALWAYS_INCLUDE_FIELDS: Tuple[str, ...] = ()

    # ============================ Ponto de entrada =============================

    def make_queryset_expandable(self, request, queryset: Optional[QuerySet] = None) -> QuerySet:  # noqa: C901
        """
        Aplica expand/select_related/prefetch_related e only()/defer() sobre `queryset` e retorna o resultado.
        """
        qs = queryset if queryset is not None else getattr(self, "queryset", None)
        if qs is None:
            try:
                qs = super().get_queryset()
            except Exception:
                raise RuntimeError("make_queryset_expandable requer um queryset.")

        raw_expand = request.query_params.get('expand', '')
        raw_fields = request.query_params.get('fields')
        raw_omit = request.query_params.get('omit')
        optimize_only = bool(raw_fields or raw_omit)

        if not raw_expand and not optimize_only:
            return qs

        serializer_cls = self._get_effective_serializer_class()
        expand_list = self._parse_expand_list(serializer_cls, raw_expand) if raw_expand else []

        root_model = getattr(qs, "model", None)

        # 1) Caminhos para select/prefetch
        selects, prefetches = self._collect_paths(serializer_cls, expand_list, root_model)
        if selects:
            qs = qs.select_related(*sorted(selects))

        # ========= AJUSTE: não duplicar Prefetch customizado =========
        # Se o queryset já tem um Prefetch explícito (ex.: vindo do FilterSet),
        # não tente adicionar o mesmo lookup novamente via expand.
        existing_prefetch_to: Set[str] = set()
        for item in getattr(qs, "_prefetch_related_lookups", []) or []:
            if isinstance(item, Prefetch):
                existing_prefetch_to.add(item.prefetch_to)
            else:
                existing_prefetch_to.add(str(item))

        effective_prefetches = set(prefetches) - existing_prefetch_to
        if effective_prefetches:
            qs = qs.prefetch_related(*sorted(effective_prefetches))

        # 2) Refletir fields/omit
        try:
            serializer = self._get_effective_serializer(request)

            # Base: o que o serializer expõe (fallback)
            needed_paths = self._collect_model_field_paths_from_serializer(serializer)

            # Autoritativo: campos da querystring
            explicit_paths = self._augment_needed_paths_from_query_fields(request)

            # Campos estáticos declarados em expandable_fields para rels em ?expand=
            static_expand_paths = self._augment_needed_paths_from_expandable_config(
                serializer.__class__, expand_list
            )

            # Se há fields=..., ele é autoritativo; senão, usa introspecção + estáticos
            if explicit_paths:
                needed_paths = explicit_paths | static_expand_paths
            else:
                needed_paths = needed_paths | static_expand_paths

            # Remover omit=...
            omit_paths = self._augment_needed_paths_from_query_omit(request)
            if omit_paths:
                needed_paths -= omit_paths

            base_needed, rel_needed = self._compute_only_field_sets(
                qs=qs,
                root_model=root_model,
                selects=selects,
                needed_paths=needed_paths,
                include_ordering=self.INCLUDE_ORDERING_FIELDS,
            )

            if self.APPLY_ONLY_STRICT:
                if base_needed or rel_needed:
                    qs = qs.only(
                        *sorted(base_needed | set(self.ALWAYS_INCLUDE_FIELDS)),
                        *sorted(rel_needed)
                    )

                # Prefetch com only() nos many
                adjusted = self._build_adjusted_prefetches(
                    root_model=root_model,
                    prefetch_paths=effective_prefetches,  # usar o conjunto efetivo
                    needed_paths=needed_paths
                )
                if adjusted:
                    # mantém os prefetches customizados já existentes e substitui os "plain"
                    qs = qs.prefetch_related(None, *adjusted)
            else:
                heavy_to_defer = self._guess_heavy_fields(root_model) if root_model else []
                if heavy_to_defer:
                    qs = qs.defer(*heavy_to_defer)

        except Exception:
            return qs

        return qs

    # ------------------- HELPERS ORIGINAIS (mantidos) --------------------

    # (1) Infra básica

    def _get_effective_serializer_class(self):
        try:
            return self.get_serializer_class()
        except Exception:
            return self.serializer_class

    def _get_effective_serializer(self, request):
        """
        Instancia o serializer com context={"request": request}, usando get_serializer()
        quando disponível, para o drf-flex-fields respeitar ?fields=/ ?omit=.
        """
        try:
            ctx = self.get_serializer_context()
            ctx["request"] = request
            return self.get_serializer(context=ctx)
        except Exception:
            cls = self._get_effective_serializer_class()
            return cls(context={"request": request})

    def _parse_expand_list(self, serializer_cls, raw: str) -> List[str]:
        if "~all" in raw or "*" in raw:
            keys = list(getattr(serializer_cls, 'expandable_fields', {}).keys())
        else:
            keys = [p.strip() for p in raw.split(",") if p.strip()]
        return list(dict.fromkeys(keys))

    def _normalize_lookup(self, s: str) -> str:
        return s.replace('.', '__')

    def _reduce_longest_paths(self, paths: Iterable[str]) -> List[str]:
        items = [p for p in paths if isinstance(p, str)]
        items.sort(key=lambda s: (s.count('__'), len(s)), reverse=True)
        kept: List[str] = []
        for p in items:
            if any(k.startswith(p + '__') for k in kept):
                continue
            kept.append(p)
        return kept

    # (2) Resolução de expandable_fields / serializers

    def _resolve_expandable_entry(self, serializer_cls, field: str) -> Tuple[Optional[Any], Dict[str, Any]]:
        expandable = getattr(serializer_cls, 'expandable_fields', {})
        entry = expandable[field]
        if isinstance(entry, tuple):
            ser, settings = entry
            return ser, (settings if isinstance(settings, dict) else {})
        if isinstance(entry, dict):
            return entry.get('serializer'), entry
        if isinstance(entry, str):
            return entry, {}
        return None, {}

    def _import_serializer_class(self, ser_ref: Union[str, type]) -> Any:
        if not isinstance(ser_ref, str):
            return ser_ref
        try:
            return import_string(ser_ref)
        except Exception:
            pass
        parts = ser_ref.split('.')
        if len(parts) == 2:
            app, cls = parts
            return import_string(f"{app}.serializers.{cls}")
        if len(parts) >= 2:
            *mod, cls = parts
            return import_string(".".join(mod + ["serializers", cls]))
        raise AttributeError(f"Não foi possível importar serializer '{ser_ref}'.")

    # (3) Inferência de cardinalidade & correção do primeiro salto

    def _infer_many_from_model(self, model: type[Model], first_segment: str) -> Optional[bool]:
        try:
            field = model._meta.get_field(first_segment)
        except FieldDoesNotExist:
            return None
        rel_many = getattr(field, 'many_to_many', False) or getattr(field, 'one_to_many', False)
        rel_one = getattr(field, 'many_to_one', False) or getattr(field, 'one_to_one', False)
        if rel_many and not rel_one:
            return True
        if rel_one and not rel_many:
            return False
        return None

    def _first_relation_name(self, model: type[Model], first_segment: str) -> str:
        try:
            model._meta.get_field(first_segment)
            return first_segment
        except Exception:
            pass
        if first_segment.startswith('id_'):
            candidate = first_segment[3:]
            try:
                model._meta.get_field(candidate)
                return candidate
            except Exception:
                pass
        return first_segment

    # (4) Coleta de caminhos

    def _collect_paths(
            self,
            root_serializer_cls,
            expand_list: List[str],
            root_model: Optional[type[Model]]
    ) -> Tuple[Set[str], Set[str]]:
        selects: Set[str] = set()
        prefetches: Set[str] = set()
        for expand in expand_list:
            sel, pref = self._paths_for_single_expand(root_serializer_cls, expand, root_model)
            selects.update(sel)
            prefetches.update(pref)
        return set(self._reduce_longest_paths(selects)), set(self._reduce_longest_paths(prefetches))

    def _paths_for_single_expand(
            self,
            root_serializer_cls,
            expand: str,
            root_model: Optional[type[Model]],
    ) -> Tuple[List[str], List[str]]:
        current_serializer = root_serializer_cls
        lookup_segments: List[str] = []
        encountered_many = False
        selects: List[str] = []
        prefetches: List[str] = []

        for i, raw_seg in enumerate(expand.split(".")):
            field = raw_seg.strip()
            try:
                ser_ref, settings = self._resolve_expandable_entry(current_serializer, field)
            except Exception:
                break

            source = self._normalize_lookup(settings.get('source', field))

            if i == 0 and root_model:
                first = source.split('__', 1)[0]
                fixed = self._first_relation_name(root_model, first)
                if fixed != first:
                    rest = source.split('__', 1)[1] if '__' in source else ''
                    source = fixed + (f'__{rest}' if rest else '')

            lookup_segments.append(source)
            full_lookup = '__'.join(lookup_segments)

            many = settings.get('many')
            if many is None and i == 0 and root_model:
                many = self._infer_many_from_model(root_model, source.split('__')[0])

            if encountered_many or many is True:
                encountered_many = True
                prefetches.append(full_lookup)
            else:
                selects.append(full_lookup)

            if ser_ref:
                try:
                    current_serializer = self._import_serializer_class(ser_ref)
                except Exception:
                    break
            else:
                break

        return selects, prefetches

    # ====================== HELPERS (otimização de colunas) =====================

    def _collect_model_field_paths_from_serializer(self, serializer, prefix: str = "") -> Set[str]:
        needed: Set[str] = set()
        fields = getattr(serializer, "fields", {})
        for name, field in fields.items():
            src = getattr(field, "source", name)
            if src == "*":
                continue
            path = src.replace(".", "__")
            if prefix:
                path = f"{prefix}__{path}"

            if getattr(field, "source_attrs", None) is not None:
                needed.add(path)

            sub = getattr(field, "child_serializer", None) or getattr(field, "serializer", None)
            if sub:
                needed |= self._collect_model_field_paths_from_serializer(sub, prefix=path)
            elif hasattr(field, "fields"):
                needed |= self._collect_model_field_paths_from_serializer(field, prefix=path)
        return needed

    def _augment_needed_paths_from_query_fields(self, request) -> Set[str]:
        raw = request.query_params.get("fields") or ""
        needed: Set[str] = set()
        if not raw:
            return needed
        for token in (p.strip() for p in raw.split(",") if p.strip()):
            if token == "url":
                continue
            needed.add(token.replace(".", "__"))
        return needed

    def _augment_needed_paths_from_query_omit(self, request) -> Set[str]:
        raw = request.query_params.get("omit") or ""
        omitted: Set[str] = set()
        if not raw:
            return omitted
        for token in (p.strip() for p in raw.split(",") if p.strip()):
            if token == "url":
                continue
            omitted.add(token.replace(".", "__"))
        return omitted

    def _augment_needed_paths_from_expandable_config(
            self,
            root_serializer_cls,
            expand_list: List[str]
    ) -> Set[str]:
        needed: Set[str] = set()
        expandable = getattr(root_serializer_cls, "expandable_fields", {}) or {}
        for rel in expand_list or []:
            entry = expandable.get(rel)
            if not entry:
                continue
            settings = {}
            if isinstance(entry, tuple):
                _, s = entry
                if isinstance(s, dict):
                    settings = s
            elif isinstance(entry, dict):
                settings = entry
            fields = settings.get("fields") or []
            for f in fields:
                if f == "url":
                    continue
                needed.add(f"{rel}__{f}")
        return needed

    def _compute_only_field_sets(
            self,
            qs: QuerySet,
            root_model: Optional[type[Model]],
            selects: Iterable[str],
            needed_paths: Set[str],
            include_ordering: bool = True,
    ) -> Tuple[Set[str], Set[str]]:
        """
        Monta os conjuntos para only():
          - base_needed: campos da raiz (fields reais do model)
          - rel_needed: lookups 'rel__campo' que resolvem em fields reais
        Ignora anotações e não empurra attnames (ex.: *_id) para o only().
        """
        base_needed: Set[str] = set()
        rel_needed: Set[str] = set()

        self._seed_only_field_sets(root_model, needed_paths, base_needed, rel_needed)
        self._include_ordering_fields(qs, root_model, include_ordering, base_needed, rel_needed)

        base_needed |= set(self.ALWAYS_INCLUDE_FIELDS)
        self._include_select_related_fields(root_model, selects, base_needed, rel_needed)

        return self._sanitize_only_field_sets(root_model, base_needed, rel_needed)

    def _seed_only_field_sets(
            self,
            root_model: Optional[type[Model]],
            needed_paths: Set[str],
            base_needed: Set[str],
            rel_needed: Set[str],
    ) -> None:
        if root_model is not None:
            base_needed.add(root_model._meta.pk.name)

        for path in needed_paths:
            if "__" in path:
                rel_needed.add(path)
            else:
                base_needed.add(path)

    def _include_ordering_fields(
            self,
            qs: QuerySet,
            root_model: Optional[type[Model]],
            include_ordering: bool,
            base_needed: Set[str],
            rel_needed: Set[str],
    ) -> None:
        if not include_ordering or root_model is None:
            return

        try:
            order_by = list(qs.query.order_by or []) or list(getattr(root_model._meta, "ordering", []) or [])
        except Exception:
            return

        for ordering_field in order_by:
            normalized = ordering_field.lstrip("-")
            if not normalized or normalized == "?":
                continue
            if "__" in normalized:
                if self._path_resolves_to_model_field(root_model, normalized):
                    rel_needed.add(normalized)
                continue
            if self._field_exists(root_model, normalized):
                base_needed.add(normalized)

    def _include_select_related_fields(
            self,
            root_model: Optional[type[Model]],
            selects: Iterable[str],
            base_needed: Set[str],
            rel_needed: Set[str],
    ) -> None:
        if root_model is None:
            return

        for select_path in selects or []:
            self._include_select_related_connector_fields(
                root_model=root_model,
                select_path=select_path,
                base_needed=base_needed,
                rel_needed=rel_needed,
            )

    def _sanitize_only_field_sets(
            self,
            root_model: Optional[type[Model]],
            base_needed: Set[str],
            rel_needed: Set[str],
    ) -> Tuple[Set[str], Set[str]]:
        if root_model is None:
            return base_needed, rel_needed

        sanitized_base = {name for name in base_needed if self._field_exists(root_model, name)}
        sanitized_rel = {path for path in rel_needed if self._path_resolves_to_model_field(root_model, path)}
        return sanitized_base, sanitized_rel

    def _include_select_related_connector_fields(
            self,
            root_model: type[Model],
            select_path: str,
            base_needed: Set[str],
            rel_needed: Set[str],
    ) -> None:
        current_model = root_model
        traversed_segments: List[str] = []

        for segment in select_path.split("__"):
            if not self._field_exists(current_model, segment):
                return

            connector_path = "__".join(traversed_segments + [segment])
            if traversed_segments:
                rel_needed.add(connector_path)
            else:
                base_needed.add(segment)

            field = current_model._meta.get_field(segment)
            related_model = getattr(field, "related_model", None)
            if related_model is None and getattr(field, "remote_field", None):
                related_model = field.remote_field.model
            if related_model is None:
                return

            current_model = related_model
            traversed_segments.append(segment)

    def _field_exists(self, model: type[Model], name: str) -> bool:
        try:
            model._meta.get_field(name)
            return True
        except Exception:
            return False

    def _path_resolves_to_model_field(self, model: type[Model], path: str) -> bool:
        cur = model
        for seg in path.split("__"):
            try:
                f = cur._meta.get_field(seg)
            except Exception:
                return False
            # segue para o próximo model quando houver relação
            nxt = getattr(f, "related_model", None)
            if nxt is None and getattr(f, "remote_field", None):
                nxt = f.remote_field.model
            cur = nxt or cur
        return True

    def _resolve_related_model_for_path(self, root_model: Optional[type[Model]], path: str) -> Optional[type[Model]]:
        if root_model is None:
            return None
        current = root_model
        for seg in path.split("__"):
            try:
                field = current._meta.get_field(seg)
            except Exception:
                return None
            related = getattr(field, "related_model", None)
            if related is None and getattr(field, "remote_field", None):
                related = field.remote_field.model
            if related is None:
                related = getattr(field, "model", None)
            if related is None:
                return None
            current = related
        return current

    def _build_adjusted_prefetches(
            self,
            root_model: Optional[type[Model]],
            prefetch_paths: Iterable[str],
            needed_paths: Set[str],
    ) -> List[Prefetch]:
        adjusted: List[Prefetch] = []
        for path in prefetch_paths:
            prefix = path + "__"
            child_fields = {
                p[len(prefix):]
                for p in needed_paths
                if p.startswith(prefix) and "__" not in p[len(prefix):]
            }
            child_model = self._resolve_related_model_for_path(root_model, path)
            if not child_model:
                continue
            child_pk = child_model._meta.pk.name
            child_only = sorted({child_pk} | (child_fields or set()))
            child_qs = child_model._default_manager.only(*child_only) if child_only else child_model._default_manager
            adjusted.append(Prefetch(path, queryset=child_qs))
        return adjusted

    def _guess_heavy_fields(self, model: Optional[type[Model]]) -> List[str]:
        heavy: List[str] = []
        if not model:
            return heavy
        for f in model._meta.get_fields():
            name = getattr(f, "name", "")
            internal = getattr(f, "get_internal_type", lambda: "")()
            if any(h in name.lower() for h in self.DEFER_HEAVY_FIELDS):
                heavy.append(name)
            elif internal in {"BinaryField"}:
                heavy.append(name)
        return heavy
        
```