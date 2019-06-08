from rest_framework import viewsets, permissions

from .models import Repo
from .models import RepoMetadata
from .serializers import RepoMetadataSerializer
from .serializers import RepoSerializer


# class RepoViewset(viewsets.ModelViewSet):
#     queryset = Repo.objects.all()
#     permissions_classes = [
#         permissions.AllowAny
#     ]
#     serializer_class = RepoSerializer
#
#
# class RepoMetadataViewset(viewsets.ModelViewSet):
#     queryset = RepoMetadata.objects.all()
#     permissions_classes = [
#         permissions.AllowAny
#     ]
#     serializer_class = RepoMetadataSerializer
