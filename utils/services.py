from typing import Any, Dict, Type, Optional
from django.db.models import Model
from .query import QueryEngine, FilterSpec

class ListService:
    """
    Generic list service:
    - soft-delete scoping
    - filters
    - sorting
    - pagination
    """
    
    @staticmethod
    def get_list(
        model: Type[Model],
        filter_specs: Dict[str, FilterSpec],
        sort_fields: Dict[str, str],
        filters: Dict[str, Any],
        sort_by: str = "id",
        sort_order: str = "desc",
        page: int = 1,
        per_page: int = 10,
        include_deleted: bool = False,
        only_deleted: bool = False,
        default_sort: str = "-id",
    ) -> Dict[str, Any]:
        # 1. base queryset (handles soft delete)
        qs = QueryEngine.get_base_queryset(
            model, include_deleted=include_deleted, only_deleted=only_deleted
        )
        
        # 2. filters
        qs = QueryEngine.apply_filters(qs, filters, filter_specs)

        # 3. sorting
        qs = QueryEngine.apply_sorting(
            qs, sort_by, sort_order, sort_fields, default=default_sort
        )
        
        # 4. pagination
        return QueryEngine.paginate(qs, page=page, per_page=per_page)