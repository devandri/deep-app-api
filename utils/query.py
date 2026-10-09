from typing import Any, Dict, List, Optional, Type
from django.db.models import Model, QuerySet, Q
from django.utils import timezone
import logging

logger = logging.getLogger(__name__)

class FilterSpec:
    """
    Declarative filter definition.
    
    type:
    - 'search': icontains across multiple fields (OR)
    - 'exact': exact match
    - 'icontains': case-insensitive contains
    - 'in': value in list
    - 'bool': True / False / None
    - 'gte': >= (dates, numbers)
    - 'lte': <= (dates, numbers)
    - 'range': tuple/list of 2 values
    - 'custom': callable(queryset, value) -> queryset
    """
    
    def __init__(
        self,
        field: Optional[str] = None,
        fields: Optional[List[str]] = None,
        type: str = "exact",
        lookup: Optional[str] = None,
        custom: Optional[callable] = None,
    ):
        self.field = field
        self.fields = fields
        self.type = type
        self.lookup = lookup
        self.custom = custom
        
class QueryEngine:
    """Generic filter + sort + paginate + engine for any Django model."""

    # FILTERING

    @staticmethod
    def apply_filters(
        queryset: QuerySet,
        filters: Dict[str, Any],
        specs: Dict[str, FilterSpec],
    ) -> QuerySet:
        for key, value in filters.items():
            if value in (None, "", []):
                continue
            
            spec = specs.get(key)
            if spec is None:
                continue
            
            queryset = QueryEngine._apply_one(queryset, spec, value)

        return queryset
    
    @staticmethod
    def _apply_one(queryset: QuerySet, spec: FilterSpec, value: Any) -> QuerySet:
        t = spec.type
        
        if t == "search":
            q = Q()
            for f in spec.fields or []:
                q |= Q(**{f"{f}__icontains": value})
            return queryset.filter(q)
        
        if t == "exact":
            return queryset.filter(**{spec.field: value})
        
        if t == "icontains":
            return queryset.filter(**{f"{spec.field}__icontains": value})

        if t == "in":
            return queryset.filter(**{f"{spec.field}__in": value})
        
        if t == "bool":
            return queryset.filter(**{{spec.field: bool(value)}})
        
        if t == "gte":
            return queryset.filter(**{f"{spec.field}__gte": value})
        
        if t == "lte":
            return queryset.filter(**{f"{spec.field}__lte": value})
        
        if t == "range":
            if isinstance(value, (list, tuple)) and len(value) == 2:
                return queryset.filter(
                    **{f"{spec.field}__gte": value[0], f"{spec.field}__lte": value[1]}
                )
            return queryset
        
        if t == "custom" and callable(spec.custom):
            return spec.custom(queryset, value)
        
        if spec.lookup:
            return queryset.filter(**{f"{spec.field}__{spec.lookup}": value})
        
        return queryset
    
    # SORTING
    @staticmethod
    def apply_sorting(
        queryset: QuerySet,
        sort_by: str,
        sort_order: str,
        valid_fields: Dict[str, str],
        default: str = "-d",
    ) -> QuerySet:
        field = valid_fields.get(sort_by)
        if field is None:
            return queryset.order_by(default)
        
        if sort_order.lower() == "desc":
            field = f"-{field}"
            
        return queryset.order_by(field)
    
    # PAGINATION
    @staticmethod
    def paginate(queryset: QuerySet, page: int = 1, per_page: int = 10) -> Dict[str, Any]:
        page = max(int(page), 1)
        per_page = max(int(per_page), 1)
        
        total = queryset.count()
        start = (page - 1) * per_page
        end = start + per_page
        
        items = list(queryset[start:end])
        
        total_pages = (total + per_page -1) // per_page if per_page else 0
        
        logger.warning("Items: %s", [i.name for i in items])
        
        return {
            "items": items,
            "pagination": {
                "total": total,
                "page": page,
                "per_page": per_page,
                "total_pages": total_pages,
                "has_next": page < total_pages,
                "has_previous": page > 1,
                "from": start + 1 if total > 0 else 0,
                "to": min(end, total) if total > 0 else 0,
            }
        }
        
    # SOFT DELETE
    @staticmethod
    def get_base_queryset(
        model: Type[Model],
        include_deleted: bool = False,
        only_deleted: bool = False,
    ) -> QuerySet:
        has_soft_delete = hasattr(model, "all_objects") and hasattr(model, "deleted_at")
        
        if not has_soft_delete:
            return model.objects.all()

        if only_deleted:
            return model.all_objects.filter(deleted_at__isnull=False)
        if include_deleted:
            return model.all_objects.all()
        return model.objects.all()