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
    def get_queryset(self):
        """
        Optionally restricts the returned user submissions to a given user and document,
        by filtering against `username` and `document` query params in the URL.
        """
        queryset = UserSubmission.objects.all()
        username = self.request.query_params.get('username')
        document = self.request.query_params.get('document')
        if username is not None:
            try:
                source = Agent.objects.get(name=username)
            except Agent.DoesNotExist:
                return queryset.none()
            queryset = queryset.filter(source=source)
        if document is not None:
            try:
                document_obj = Document.objects.get(id=document)
            except Document.DoesNotExist:
                return queryset.none()
            queryset = queryset.filter(document=document_obj)
        return queryset
    def list(self, request, *args, **kwargs):
        # Check if both query parameters are present
        username = request.query_params.get('username')
        document = request.query_params.get('document')
        
        if username and document:
            # Use the existing get_queryset() logic to filter
            queryset = self.filter_queryset(self.get_queryset())
            
            if queryset.exists():
                # Get the single object
                instance = queryset.get()
                serializer = self.get_serializer(instance)
                return Response(serializer.data)
            else:
                return Response(
                    status=status.HTTP_204_NO_CONTENT
                )
        
        # For other cases (single param or no params), use default list behavior
        return super().list(request, *args, **kwargs)

        





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

