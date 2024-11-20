from rest_framework import generics
from rest_framework.response import Response
from rest_framework.permissions import IsAdminUser
from LabelCarftAccount.serializers import UserSerializer
from LabelCarftAccount.models import User


class GetAllUserAdmin(generics.GenericAPIView):
    serializer_class = UserSerializer
    permission_classes = [IsAdminUser]

    def get(self, request, *args, **kwargs):
        users = User.objects.all()
        serializer = self.get_serializer(users, many=True)
        return Response(serializer.data)
