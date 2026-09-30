"""Versioned metadata for executable Pipeline node kinds."""

from dataclasses import asdict, dataclass


@dataclass(frozen=True)
class PortDefinition:
    key: str
    display_name: str
    multiple: bool = False


@dataclass(frozen=True)
class NodeTypeDefinition:
    key: str
    display_name: str
    category: str
    description: str
    icon: str
    inputs: tuple[PortDefinition, ...]
    outputs: tuple[PortDefinition, ...]
    configuration_schema: dict[str, object]
    configuration_defaults: dict[str, object]
    executor_key: str
    supports_preview: bool = True
    supports_schema_inference: bool = True

    def representation(self) -> dict[str, object]:
        value = asdict(self)
        value["displayName"] = value.pop("display_name")
        value["configurationSchema"] = value.pop("configuration_schema")
        value["configurationDefaults"] = value.pop("configuration_defaults")
        value["executorKey"] = value.pop("executor_key")
        value["supportsPreview"] = value.pop("supports_preview")
        value["supportsSchemaInference"] = value.pop("supports_schema_inference")
        for group in (value["inputs"], value["outputs"]):
            for port in group:
                port["displayName"] = port.pop("display_name")
        return value


INPUT = (PortDefinition("input", "Input"),)
OUTPUT = (PortDefinition("output", "Output"),)


def _definition(key: str, name: str, category: str, description: str, *, inputs=INPUT, outputs=OUTPUT, required: tuple[str, ...] = (), defaults: dict[str, object] | None = None, preview: bool = True) -> NodeTypeDefinition:
    return NodeTypeDefinition(
        key, name, category, description, key.replace("_", "-"), inputs, outputs,
        {"type": "object", "required": list(required)}, defaults or {}, key,
        preview, True,
    )


NODE_TYPES = (
    _definition("database_source", "Database Source", "SOURCE", "Read a table or view in bounded batches.", inputs=(), required=("connectionId", "schema", "dataset"), defaults={"columns": [], "batchSize": 1000}),
    _definition("sql_query_source", "SQL Query Source", "SOURCE", "Read from a validated read-only SQL query.", inputs=(), required=("connectionId", "query"), defaults={"batchSize": 1000}),
    _definition("select_columns", "Select Columns", "TRANSFORM", "Choose and order propagated columns.", required=("columns",)),
    _definition("rename_columns", "Rename Columns", "TRANSFORM", "Rename one or more columns.", required=("mappings",)),
    _definition("filter", "Filter", "TRANSFORM", "Keep rows matching structured predicates.", required=("predicate",)),
    _definition("derived_column", "Derived Column", "TRANSFORM", "Create a column with a safe expression.", required=("column", "expression", "outputType")),
    _definition("cast", "Cast / Convert Type", "TRANSFORM", "Apply explicit, checked type conversions.", required=("casts",)),
    _definition("sort", "Sort", "TRANSFORM", "Order rows using bounded staging.", required=("columns",)),
    _definition("distinct", "Distinct", "TRANSFORM", "Remove duplicate rows using bounded staging."),
    _definition("aggregate", "Aggregate", "TRANSFORM", "Group rows and calculate aggregates.", required=("aggregates",)),
    _definition("join", "Join", "TRANSFORM", "Join left and right streams.", inputs=(PortDefinition("left", "Left"), PortDefinition("right", "Right")), required=("joinType", "keys")),
    _definition("lookup", "Lookup", "TRANSFORM", "Enrich a primary stream from a lookup stream.", inputs=(PortDefinition("primary", "Primary"), PortDefinition("lookup", "Lookup")), required=("keys",)),
    _definition("union", "Union", "TRANSFORM", "Combine compatible inputs.", inputs=(PortDefinition("input", "Input", True),)),
    _definition("split_router", "Split / Router", "TRANSFORM", "Route rows to named conditional outputs.", outputs=(PortDefinition("matched", "Matched", True),), required=("routes",)),
    _definition("null_handling", "Null Handling", "TRANSFORM", "Replace, retain or reject null values.", required=("rules",)),
    _definition("deduplicate", "Deduplicate", "TRANSFORM", "Keep one row for each configured key.", required=("keys",)),
    _definition("data_quality", "Data Quality Check", "GOVERNANCE", "Evaluate row and dataset quality rules.", outputs=(PortDefinition("output", "Valid", True), PortDefinition("invalid", "Invalid", True)), required=("rules", "action")),
    _definition("limit_sample", "Limit / Sample", "TRANSFORM", "Bound the number of output rows.", required=("limit",)),
    _definition("validation_gate", "Validation Gate", "GOVERNANCE", "Stop execution when validation conditions fail.", required=("rules",)),
    _definition("database_target", "Database Target", "TARGET", "Write mapped rows to a database target.", outputs=(), required=("connectionId", "schema", "table", "writeMode"), defaults={"writeMode": "APPEND", "mappings": []}, preview=False),
)

NODE_TYPE_BY_KEY = {item.key: item for item in NODE_TYPES}
