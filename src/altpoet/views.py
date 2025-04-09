from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404

from rest_framework import generics, permissions, status, viewsets
from rest_framework.response import Response

from altpoet.models import Alt, Agent, Document, Img , UserSubmission
from altpoet.serializers import AltSerializer, DocumentSerializer, ImgSerializer, UserSerializer, UserSubmissionSerializer


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

class UserSubmissionViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows user JSON alt text submissions to be viewed or edited.
    """
    queryset = UserSubmission.objects.all()
    serializer_class = UserSubmissionSerializer
    permission_classes = [permissions.IsAuthenticated]

    '''
    creates a new submission and autoassigns source
    '''
    def create(self, request, *args, **kwargs):
        try:
            document = Document.objects.get(id=request.data.get('document', ''))
        except Document.DoesNotExist:
            return Response({'detail': 'Document not found'}, status=status.HTTP_400_BAD_REQUEST)
        user_json = request.data.get('user_json', None)
        source = request.data.get('source', None)
        if source == None:
            source, created = Agent.objects.get_or_create(
                user=request.user,
                name=request.user.username)
        else:
            source, created = Agent.objects.get_or_create(user=None, name=source)

        user_sub, created = UserSubmission.objects.get_or_create(user_json=user_json, 
                                                            document=document, source=source)
        serializer = UserSubmissionSerializer(user_sub)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    # query func to get json field based on username and document
    # def query(username, document):
        # ...


class ImgViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows imgs to be viewed or edited.
    """
    queryset = Img.objects.all().order_by('document')
    serializer_class = ImgSerializer
    permission_classes = [permissions.IsAuthenticated]
 
    
class AltViewSet(viewsets.ModelViewSet, generics.CreateAPIView):
    """
    API endpoint that allows alt text to be viewed or edited.
    """
    queryset = Alt.objects.all().order_by('-created')
    serializer_class = AltSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    '''
    creates a new alt, and sets it in the specified img
    '''
    def create(self, request, *args, **kwargs):
        try:
            img = Img.objects.get(id=request.data.get('img', ''))
        except Img.DoesNotExist:
            return Response({'detail': 'Img not found'}, status=status.HTTP_400_BAD_REQUEST)
        text = request.data.get('text', '')
        source = request.data.get('source', None)
        if source == None:
            source, created = Agent.objects.get_or_create(
                user=request.user,
                name=request.user.username)
        else:
            source, created = Agent.objects.get_or_create(user=None, name=source)

        alt, created = Alt.objects.get_or_create(img=img, text=text, source=source)
        img.alt = alt
        img.save()
        serializer = AltSerializer(alt)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

