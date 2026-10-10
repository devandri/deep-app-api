from utils.query import FilterSpec

GOAL_FILTER_SPECS = {
    "search": FilterSpec(
        type="search",
        fields=["name", "status", "category", "description"],
    ),
    "name": FilterSpec(field="name", type="icontains"),
    "category": FilterSpec(field="category", type="icontains"),
    "status": FilterSpec(field="status", type="exact"),
    "start_date": FilterSpec(field="start_date", type="gte"),
    "end_date": FilterSpec(field="end_date", type="lte"),
}

GOAL_SORT_FIELDS = {
    "name": "name",
    "category": "category",
    "start_date": "start_date",
    "end_date": "end_date",
}