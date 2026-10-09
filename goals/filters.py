from utils.query import FilterSpec

GOAL_FILTER_SPECS = {
    "search": FilterSpec(
        type="search",
        fields=["name", "category", "description"],
    ),
    "name": FilterSpec(field="name", type="icontains"),
}

GOAL_SORT_FIELDS = {
    "name": "name",
    "category": "category",
}