from rest_framework import viewsets, permissions
from rest_framework.response import Response


class ComentarioViewSet(viewsets.ViewSet):
    permission_classes = [permissions.AllowAny]

    def list(self, request):
        return Response([])

    def retrieve(self, request, pk=None):
        return Response({})


class RetroalimentacionIAViewSet(viewsets.ViewSet):
    permission_classes = [permissions.AllowAny]

    def list(self, request):
        return Response([])

    def create(self, request):
        return Response({'status': 'ok'})
