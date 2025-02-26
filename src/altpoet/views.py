from django.contrib.auth.models import User
from rest_framework import permissions, viewsets

from altpoet.models import Document, Img, Alt
from altpoet.serializers import DocumentSerializer, ImgSerializer, AltSerializer, UserSerializer


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer


class DocumentViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows documents to be viewed or edited.
    """
    queryset = Document.objects.all().order_by('item')
    serializer_class = DocumentSerializer
    permission_classes = [permissions.IsAuthenticated]


class ImgViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows imgs to be viewed or edited.
    """
    queryset = Img.objects.all().order_by('document')
    serializer_class = ImgSerializer
    permission_classes = [permissions.IsAuthenticated]
 
    
class AltViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows alt text to be viewed or edited.
    """
    queryset = Alt.objects.all().order_by('-created')
    serializer_class = AltSerializer
    permission_classes = [permissions.IsAuthenticated]