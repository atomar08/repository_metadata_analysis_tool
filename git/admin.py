from django.contrib import admin

from .models import Repo
from .models import RepoMetadata

# Register your models here.

admin.site.register(Repo)
admin.site.register(RepoMetadata)
