from django.contrib.auth.models import User

from rest_framework import serializers


from altpoet.models import Document, Img, Image, Alt, Agent, UserSubmission


# Serializers define the API representation.
class UserSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = User
        fields = ['url', 'username', 'email', 'is_staff']


class ImageSerializer(serializers.ModelSerializer):

    class Meta:
        model = Image
        fields = ['url', 'x', 'y', 'filesize']


class AltSerializer(serializers.ModelSerializer):
    source = serializers.SlugRelatedField(
        many=False, read_only=True, slug_field='name')

    class Meta:
        model = Alt
        fields = ['id', 'img', 'text', 'source', 'created']


class ImgSerializer(serializers.ModelSerializer):
    image = ImageSerializer(many=False, read_only=True)
    alt = serializers.PrimaryKeyRelatedField(
        many=False, read_only=False, allow_null=True, queryset=Alt.objects.all())
    alts = AltSerializer(many=True, read_only=True)

    class Meta:
        model = Img
        fields = ['id', 'image', 'img_id', 'img_type', 'is_figure', 'alt', 'alts']


class DocumentSerializer(serializers.ModelSerializer):
    project = serializers.SlugRelatedField(many=False, read_only=True, slug_field='name')
    imgs = ImgSerializer(many=True, read_only=True)
    class Meta:
        model = Document
        fields = ['project', 'id', 'item', 'base', 'imgs']

class UserSubmissionSerializer(serializers.ModelSerializer):
    source = serializers.SlugRelatedField(
        many=False, read_only=True, slug_field='name')
    
    # TODO: change document to slug field based on book num

    class Meta:
        model = UserSubmission
        fields = ['id', 'source', 'document', 'user_json', 'created']
        
