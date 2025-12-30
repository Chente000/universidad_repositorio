# Ejemplo de lo que debes buscar y cambiar en tu backend
from rest_framework import viewsets
from rest_framework.permissions import AllowAny # 1. Importa esto
# ... tus otros imports

class CarreraViewSet(viewsets.ReadOnlyModelViewSet): # O la que uses
    queryset = Carrera.objects.all()
    serializer_class = CarreraSerializer
    
    # 2. AÑADE ESTA LÍNEA para que sea pública
    permission_classes = [AllowAny]