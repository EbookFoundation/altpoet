from django.contrib.auth.models import User

from rest_framework import serializers

from altpoet.models import Document, Img, Alt


# Serializers define the API representation.
class UserSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = User
        fields = ['url', 'username', 'email', 'is_staff']

class DocumentSerializer(serializers.ModelSerializer):
    project = serializers.SlugRelatedField(many=False, read_only=True, slug_field='name')
    imgs = serializers.HyperlinkedRelatedField(many=True, read_only=True, view_name='img-detail')
    class Meta:
        model = Document
        fields = ['project', 'id', 'item', 'base', 'imgs']
        

class ImgSerializer(serializers.ModelSerializer):
    image = serializers.SlugRelatedField(many=False, read_only=True, slug_field='url')
    alt = serializers.HyperlinkedRelatedField(many=False, read_only=True, view_name='alt-detail')
    alts = serializers.HyperlinkedRelatedField(many=True, read_only=True, view_name='alt-detail')
    class Meta:
        model = Img
        fields = ['image', 'img_id', 'img_type', 'is_figure', 'alt', 'alts']


class AltSerializer(serializers.ModelSerializer):
    source = serializers.SlugRelatedField(many=False, read_only=True, slug_field='name')
    class Meta:
        model = Alt
        fields = ['text', 'source', 'created']
