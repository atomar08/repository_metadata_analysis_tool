# https://medium.com/@vasjaforutube/django-mongodb-django-rest-framework-mongoengine-ee4eb5857b9a

from rest_framework import serializers

from .models import Repo
from .models import RepoMetadata


class RepoMetadataSerializer(serializers.ModelSerializer):
    class Meta:
        model = RepoMetadata
        fields = ('commit_no', 'repo_name', 'commit_id', 'author_name', 'commit_date', 'commit_message', 'files')
        # fields = '__all__'


class RepoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Repo
        fields = ('repo_name', 'latest_commit_no', 'latest_commit_date')
        # fields = '__all__'
