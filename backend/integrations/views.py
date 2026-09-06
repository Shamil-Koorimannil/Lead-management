from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

class IntegrationsPlaceholderView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return Response({
            'status': 'placeholder',
            'message': 'Automation integrations (n8n, OpenAI, WhatsApp) will be configured in a future phase.'
        })
