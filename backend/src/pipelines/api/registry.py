from django.http import HttpRequest
from rest_framework.response import Response
from rest_framework.views import APIView

from nexetl.api.authentication import NexetlSessionAuthentication
from pipelines.authorization import require_capability
from pipelines.node_registry import NODE_TYPES


class NodeTypeCollectionView(APIView):
    authentication_classes=[NexetlSessionAuthentication]
    def get(self,request:HttpRequest)->Response:
        require_capability(request,"pipelines.inspect_pipeline_definition")
        return Response({"items":[item.representation() for item in NODE_TYPES]})
