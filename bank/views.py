from rest_framework import generics, viewsets
from .models import Client, Wallet
from .serializers import ClientSerializer, WalletSerializer, WalletBalanceSerializer
from django.contrib.auth import authenticate
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken




class ClientViewSet(viewsets.ModelViewSet):
    queryset = Client.objects.all()
    serializer_class = ClientSerializer


class WalletViewSet(viewsets.ModelViewSet):
    queryset = Wallet.objects.all()
    serializer_class = WalletSerializer
    

class WalletBalanceView(generics.RetrieveAPIView):
    queryset = Wallet.objects.all()
    serializer_class = WalletBalanceSerializer
  
    
class ClientLoginView(generics.RetrieveAPIView):
      def post(self, request):
        client_id = request.data.get('client_id')
        password = request.data.get('password')

        try:
            client = Client.objects.get(id=client_id)
        except Client.DoesNotExist:
            return Response({'error': 'Client introuvable'}, status=status.HTTP_404_NOT_FOUND)

        user = authenticate(username=client.user.username, password=password)
        if user is None:
            return Response({'error': 'Mot de passe incorrect'}, status=status.HTTP_401_UNAUTHORIZED)

        refresh = RefreshToken.for_user(user)
        return Response({
            'access': str(refresh.access_token),
            'refresh': str(refresh),
        })
   