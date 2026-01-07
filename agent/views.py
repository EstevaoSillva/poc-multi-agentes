from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from agent.agent import ask_team


class MultiAgentChatView(APIView):
    def post(self, request):
        user_query = request.data.get('pergunta')

        if not user_query:
            return Response(
                {"erro": "Envie o campo 'pergunta'."},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            resposta_texto = ask_team(user_query)

            return Response({
                "resposta": resposta_texto
            }, status=status.HTTP_200_OK)

        except Exception as e:
            print(f"Erro no Agno/Ollama: {e}")
            return Response(
                {"erro": "O sistema de AGENTES está indisponível no momento."},
                status=status.HTTP_503_SERVICE_UNAVAILABLE
            )