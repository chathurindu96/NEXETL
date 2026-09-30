"""REST control plane for configured database Connections."""

import json
from uuid import UUID

from django.conf import settings
from django.db import transaction
from django.http import HttpRequest
from rest_framework import status
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from rest_framework.views import APIView

from nexetl.api.authentication import NexetlSessionAuthentication
from nexetl.api.errors import NexetlAPIError
from pipelines.connections import ADAPTERS, ConnectorFailure, LocalEncryptedSecretProvider
from pipelines.authorization import require_capability
from pipelines.infrastructure.persistence.models import ConnectionRecord


SAFE_FIELDS = {
    "postgresql": {"host", "port", "database", "username", "sslMode", "applicationName"},
    "mysql": {"host", "port", "database", "username", "sslMode"},
    "mariadb": {"host", "port", "database", "username", "sslMode"},
    "sqlserver": {"host", "port", "database", "username", "driver", "encrypt", "trustServerCertificate"},
}


def representation(record: ConnectionRecord) -> dict[str, object]:
    return {
        "id": str(record.id), "name": record.name, "connectorKey": record.connector_key,
        "description": record.description, "configuration": record.configuration,
        "secretReference": str(record.secret_id) if record.secret_id else None,
        "secretConfigured": bool(record.secret_id), "state": record.state,
        "createdAt": record.created_at.isoformat(), "updatedAt": record.updated_at.isoformat(),
    }


def _record(value: str) -> ConnectionRecord:
    try: return ConnectionRecord.objects.get(id=UUID(value))
    except (ValueError, ConnectionRecord.DoesNotExist) as error:
        raise NexetlAPIError("NEXETL_CONNECTION_NOT_FOUND", "The Connection was not found.", http_status=404, category="not_found") from error


def _configuration(connector_key: object, value: object) -> tuple[str, dict[str, object]]:
    if not isinstance(connector_key, str) or connector_key not in ADAPTERS:
        raise ValidationError({"connectorKey": "A supported Connector is required."})
    if not isinstance(value, dict): raise ValidationError({"configuration": "Must be an object."})
    if "password" in value: raise ValidationError({"configuration": "Secrets must use the write-only password field."})
    extra = set(value) - SAFE_FIELDS[connector_key]
    if extra: raise ValidationError({"configuration": f"Unsupported fields: {', '.join(sorted(extra))}."})
    return connector_key, value


def _adapter_context(record: ConnectionRecord):
    if not record.secret_id:
        raise NexetlAPIError("NEXETL_CONNECTION_SECRET_UNAVAILABLE", "The Connection secret is unavailable.", category="configuration")
    return ADAPTERS[record.connector_key], LocalEncryptedSecretProvider().resolve(record.secret_id)


def _connector_call(operation):
    try: return operation()
    except ConnectorFailure as error:
        raise NexetlAPIError(error.code, error.public_message, category="connector", http_status=503 if error.transient else 422) from error


class ConnectionCollectionView(APIView):
    authentication_classes = [NexetlSessionAuthentication]

    def get(self, request: HttpRequest) -> Response:
        require_capability(request, "pipelines.list_connection")
        records = ConnectionRecord.objects.select_related("secret").order_by("name", "id")
        return Response({"items": [representation(item) for item in records]})

    def post(self, request: HttpRequest) -> Response:
        require_capability(request, "pipelines.create_connection")
        payload = request.data if isinstance(request.data, dict) else {}
        name, description, password = payload.get("name"), payload.get("description", ""), payload.get("password")
        connector_key, configuration = _configuration(payload.get("connectorKey"), payload.get("configuration"))
        if not isinstance(name, str) or not name.strip() or len(name.strip()) > 120: raise ValidationError({"name": "A name of at most 120 characters is required."})
        if not isinstance(description, str) or len(description) > 1000: raise ValidationError({"description": "Must be at most 1000 characters."})
        if not isinstance(password, str) or not password: raise ValidationError({"password": "A password is required."})
        with transaction.atomic():
            secret_id = LocalEncryptedSecretProvider().store(password)
            record = ConnectionRecord.objects.create(name=name.strip(), description=description, connector_key=connector_key, configuration=configuration, secret_id=secret_id)
        return Response(representation(record), status=status.HTTP_201_CREATED)


class ConnectionDetailView(APIView):
    authentication_classes = [NexetlSessionAuthentication]

    def get(self, request: HttpRequest, connection_id: str) -> Response:
        require_capability(request, "pipelines.inspect_connection")
        return Response(representation(_record(connection_id)))

    def patch(self, request: HttpRequest, connection_id: str) -> Response:
        require_capability(request, "pipelines.update_connection")
        record = _record(connection_id); payload = request.data if isinstance(request.data, dict) else {}
        connector_key, configuration = _configuration(payload.get("connectorKey", record.connector_key), payload.get("configuration", record.configuration))
        name, description, state_value = payload.get("name", record.name), payload.get("description", record.description), payload.get("state", record.state)
        if not isinstance(name, str) or not name.strip() or len(name.strip()) > 120: raise ValidationError({"name": "Invalid name."})
        if state_value not in {"ENABLED", "DISABLED"}: raise ValidationError({"state": "Must be ENABLED or DISABLED."})
        with transaction.atomic():
            record.name=name.strip(); record.description=str(description); record.connector_key=connector_key; record.configuration=configuration; record.state=state_value
            password=payload.get("password")
            if password is not None:
                if not isinstance(password,str) or not password: raise ValidationError({"password":"Must be non-empty."})
                if record.secret_id: LocalEncryptedSecretProvider().replace(record.secret_id,password)
                else: record.secret_id=LocalEncryptedSecretProvider().store(password)
            record.save()
        return Response(representation(record))


class ConnectionTestView(APIView):
    authentication_classes = [NexetlSessionAuthentication]
    def post(self, request, connection_id):
        require_capability(request,"pipelines.test_connection"); record=_record(connection_id); adapter,password=_adapter_context(record)
        return Response(_connector_call(lambda: adapter.test_connection(record.configuration,password,settings.CONFIGURATION.runtime.operation_timeout_seconds)))


class ConnectionSchemasView(APIView):
    authentication_classes=[NexetlSessionAuthentication]
    def get(self,request,connection_id):
        require_capability(request,"pipelines.inspect_connection"); record=_record(connection_id); adapter,password=_adapter_context(record)
        return Response({"items":_connector_call(lambda:adapter.discover_schemas(record.configuration,password,settings.CONFIGURATION.runtime.operation_timeout_seconds))})


class ConnectionDatasetsView(APIView):
    authentication_classes=[NexetlSessionAuthentication]
    def get(self,request,connection_id):
        require_capability(request,"pipelines.inspect_connection"); schema=request.query_params.get("schema","").strip()
        if not schema: raise ValidationError({"schema":"Required."})
        record=_record(connection_id); adapter,password=_adapter_context(record)
        return Response({"items":_connector_call(lambda:adapter.discover_datasets(record.configuration,password,schema,settings.CONFIGURATION.runtime.operation_timeout_seconds))})


class ConnectionDatasetSchemaView(APIView):
    authentication_classes=[NexetlSessionAuthentication]
    def get(self,request,connection_id,dataset):
        require_capability(request,"pipelines.inspect_connection"); schema=request.query_params.get("schema","").strip()
        if not schema: raise ValidationError({"schema":"Required."})
        record=_record(connection_id); adapter,password=_adapter_context(record)
        return Response({"fields":_connector_call(lambda:adapter.discover_schema(record.configuration,password,schema,dataset,settings.CONFIGURATION.runtime.operation_timeout_seconds))})


class ConnectionPreviewView(APIView):
    authentication_classes=[NexetlSessionAuthentication]
    def get(self,request,connection_id):
        require_capability(request,"pipelines.inspect_connection"); record=_record(connection_id); adapter,password=_adapter_context(record)
        try: limit=int(request.query_params.get("limit",settings.CONFIGURATION.runtime.preview_default_rows))
        except ValueError as error: raise ValidationError({"limit":"Must be an integer."}) from error
        if not 1<=limit<=settings.CONFIGURATION.runtime.preview_max_rows: raise ValidationError({"limit":f"Must be 1 through {settings.CONFIGURATION.runtime.preview_max_rows}."})
        source={"schema":request.query_params.get("schema"),"dataset":request.query_params.get("dataset"),"query":request.query_params.get("query")}
        rows=[]
        for batch in _connector_call(lambda:adapter.read_batches(record.configuration,password,source,min(limit,settings.CONFIGURATION.runtime.batch_size),settings.CONFIGURATION.runtime.operation_timeout_seconds)):
            rows.extend(batch[:limit-len(rows)])
            if len(rows)>=limit: break
        if len(json.dumps(rows,default=str).encode())>settings.CONFIGURATION.runtime.preview_max_bytes: raise NexetlAPIError("NEXETL_PREVIEW_PAYLOAD_LIMIT","The Preview exceeded the safe payload limit.",http_status=413,category="validation")
        return Response({"columns":list(rows[0]) if rows else [],"rows":rows,"rowCount":len(rows),"limit":limit})

