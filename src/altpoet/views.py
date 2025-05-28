from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404

from rest_framework.decorators import action

from rest_framework import generics, permissions, status, viewsets, exceptions
from rest_framework.response import Response

from altpoet.models import Project, Alt, Agent, Document, Img , UserSubmission
from altpoet.serializers import AltSerializer, DocumentSerializer, ImgSerializer, UserSerializer, UserSubmissionSerializer

from django.db import transaction
from rest_framework.test import APIRequestFactory



class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer

    @action(detail=False, methods=["GET"], url_path='get-username', 
            url_name='get-username')
    def get_username(self, request, *args, **kwargs):
        username = request.user.username
        try:
            User.objects.get(username=username)
        except User.DoesNotExist:
            return Response({'detail': "User " + username + "Doesn't Exist"}, status=status.HTTP_400_BAD_REQUEST)
        return Response({"username": username}, status=status.HTTP_200_OK)


class DocumentViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows documents to be viewed or edited.
    """
    queryset = Document.objects.all().order_by('item')
    serializer_class = DocumentSerializer
    permission_classes = [permissions.IsAuthenticated]


    @action(detail=False, methods=["GET"], url_path='get-project-item', 
            url_name='get-project-item')
    def get_project_item(self, request, *args, **kwargs):
        project = request.query_params.get('project')
        item = request.query_params.get('item')
        if project is None:
            return Response({'detail': "Project Not Found"}, status=status.HTTP_400_BAD_REQUEST)
        try: 
            project = Project.objects.get(name=project)
        except:
            return Response({'detail': "Project Not Found"}, status=status.HTTP_400_BAD_REQUEST)
        if item is None:
                return Response({'detail': "Item Not Found"}, status=status.HTTP_400_BAD_REQUEST)
        try:
            document = Document.objects.get(project=project, item=item)
        except Document.DoesNotExist:
            return Response({'detail': "Document Doesn't Exist"}, status=status.HTTP_400_BAD_REQUEST)
        serializer = DocumentSerializer(document)
        return Response(serializer.data, status=status.HTTP_200_OK)

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
    def update_img_alt_texts(self, user_json, document, source, user, username):
        source_req = source
        for key, value in user_json.items():
            img = Img.objects.filter(document=document, img_id=key).get()
            if source == None:
                source, created = Agent.objects.get_or_create(
                    user=user,
                    name=username)
            else:
                source, created = Agent.objects.get_or_create(user=None, name=source)
            alt, created = Alt.objects.update_or_create(img=img, source=source, 
                                                        defaults={
                                                            "text": value
                                                        })
            img.alt = alt
            img.save()
            source = source_req
    
    def add_user_sub_fk(self, user_sub, user_json, document, user, username):
        for key, value in user_json.items():
            img = Img.objects.filter(document=document, img_id=key).get()
            source = Agent.objects.filter(user=user, name=username).get()
            alt = Alt.objects.filter(img=img, source=source).get()
            alt.user_sub = user_sub
            alt.save()
                                
    # new alts_created [] in model, if "SB" then create alts and add them to obj, otherwise empty
    def create(self, request, *args, **kwargs):
        try:
            document = Document.objects.get(id=request.data.get('document', ''))
        except Document.DoesNotExist:
            return Response({'detail': 'Document not found'}, status=status.HTTP_404_NOT_FOUND)
        user_json = request.data.get('user_json', None)
        source = request.data.get('source', None)
        submission_type = request.data.get('submission_type', None)
        # if "SB" then add alts_created [] to updateorcreate "defaults" obj, otherwise empty 
        try:
            with transaction.atomic():
                if(submission_type == UserSubmission.SubmissionType.SUBMIT):
                    self.update_img_alt_texts(user_json, document, source, 
                            request.user, request.user.username)
                if source == None:
                    source, created = Agent.objects.get_or_create(
                        user=request.user,
                        name=request.user.username)
                else:
                    source, created = Agent.objects.get_or_create(user=None, name=source)

                user_sub, created = UserSubmission.objects.update_or_create(
                    document=document, 
                    source=source, 
                    defaults={
                        'user_json': user_json, 
                        "submission_type": submission_type
                    })
                if(submission_type == UserSubmission.SubmissionType.SUBMIT):
                    self.add_user_sub_fk(user_sub, user_json, document, 
                                         request.user, request.user.username)
        except Img.DoesNotExist:
            return Response({'detail': 'Img not found' }, status=status.HTTP_404_NOT_FOUND)
        except Agent.DoesNotExist:
            return Response({'detail': 'User not found: ' + request.user.username}, status=status.HTTP_404_NOT_FOUND)
        except Alt.DoesNotExist:
            return Response({'detail': 'Alt not found'}, status=status.HTTP_404_NOT_FOUND)        
        
        serializer = UserSubmissionSerializer(user_sub)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    def get_queryset(self):
        """
        Optionally restricts the returned user submissions to a given user and document,
        by filtering against `username` and `document` query params in the URL.
        """
        queryset = UserSubmission.objects.all()
        username = self.request.query_params.get('username')
        item = self.request.query_params.get('item')
        project = Project.objects.get(name='Project Gutenberg')
        if username is not None:
            try:
                source = Agent.objects.get(name=username)
            except Agent.DoesNotExist:
                return queryset.none()
            queryset = queryset.filter(source=source)
        if item is not None:
            try:
                document = Document.objects.get(project=project, item=item)
            except Document.DoesNotExist:
                return queryset.none()
            queryset = queryset.filter(document=document)
        return queryset
    def list(self, request, *args, **kwargs):
        # Check if both query parameters are present
        username = request.query_params.get('username')
        item = request.query_params.get('item')
        
        if username and item:
            # Use the existing get_queryset() logic to filter
            queryset = self.filter_queryset(self.get_queryset())
            
            if queryset.exists():
                # Get the single object
                instance = queryset.get()
                serializer = self.get_serializer(instance)
                return Response(serializer.data, status=status.HTTP_200_OK)
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
    def create(self, request, *args, **kwargs):
        '''
        creates a new alt, and sets it in the specified img
        '''
        try:
            img = Img.objects.get(id=request.data.get('img', ''))
        except Img.DoesNotExist:
            return Response({'detail': 'Img not found'}, status=status.HTTP_404_NOT_FOUND)
        text = request.data.get('text', '')
        source = request.data.get('source', None)
        user_sub = request.data.get('user_sub', None)
        if source == None:
            source, created = Agent.objects.get_or_create(
                user=request.user,
                name=request.user.username)
        else:
            source, created = Agent.objects.get_or_create(user=None, name=source)

        alt, created = Alt.objects.update_or_create(img=img, source=source, 
                                                    defaults={
                                                        "text": text,
                                                        "user_sub": user_sub
                                                    })
        img.alt = alt
        img.save()
        serializer = AltSerializer(alt)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    def update(self, request, *args, **kwargs):
        '''
        add user auth check to patch request
        '''
        text_source = self.get_object().source
        if(text_source == None):
            return Response({'detail': "Alt Text Source Doesn't Exist"}, status=status.HTTP_404_NOT_FOUND)
        try: 
            user = Agent.objects.get(user=request.user, name=request.user.username)
        except Agent.DoesNotExist:
            return Response({'detail': "User Doesn't Exist"}, status=status.HTTP_404_NOT_FOUND)
        if(user != text_source):
            return Response({'detail': "User Doesn't Have Permission To Edit"}, status=status.HTTP_404_NOT_FOUND)
        # if ok to edit, use regular patch
        return super().update(request, *args, **kwargs)

        
        



