"""Design-time connector catalogue descriptors; no credentials or connectivity."""

from dataclasses import dataclass


@dataclass(frozen=True)
class ConnectorDefinition:
    key: str
    display_name: str
    category: str
    description: str
    vendor: str
    version: str
    availability: str
    capabilities: tuple[str, ...]


CATALOGUE = (
    ConnectorDefinition(
        "postgresql", "PostgreSQL", "BOTH", "Design-time PostgreSQL connector descriptor.",
        "PostgreSQL Global Development Group", "1.0", "AVAILABLE", ("read", "write"),
    ),
    ConnectorDefinition(
        "sqlserver", "SQL Server", "BOTH", "Design-time SQL Server connector descriptor.",
        "Microsoft", "1.0", "AVAILABLE", ("read", "write"),
    ),
    ConnectorDefinition(
        "mysql", "MySQL", "BOTH", "Design-time MySQL connector descriptor.",
        "Oracle", "1.0", "AVAILABLE", ("read", "write"),
    ),
    ConnectorDefinition(
        "mariadb", "MariaDB", "BOTH", "Design-time MariaDB connector descriptor.",
        "MariaDB plc", "1.0", "AVAILABLE", ("read", "write"),
    ),
)
