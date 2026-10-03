from rest_framework import generics, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response

from apps.market.models import Lot, Mill, Variety
from apps.market.serializers import LotSerializer, MillSerializer, VarietySerializer


@api_view(["GET"])
@permission_classes([permissions.AllowAny])
def api_root(request):
    return Response({"message": "RiceMandi API v1"})


class VarietyListAPIView(generics.ListAPIView):
    queryset = Variety.objects.filter(is_active=True)
    serializer_class = VarietySerializer
    permission_classes = [permissions.AllowAny]


class LotListAPIView(generics.ListAPIView):
    queryset = Lot.objects.filter(status=Lot.STATUS_ACTIVE, is_available=True).select_related("variety", "mill", "merchant")
    serializer_class = LotSerializer
    permission_classes = [permissions.AllowAny]
