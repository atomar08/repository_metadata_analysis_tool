# Models documentation:
# https://docs.djangoproject.com/en/2.2/ref/models/fields/
# https://www.django-rest-framework.org/api-guide/serializers/

# Django Queryset API reference doc:
# https://docs.djangoproject.com/en/2.2/ref/models/querysets/

from __future__ import unicode_literals

from djongo import models


class RepoMetadata(models.Model):
    # created_at = models.DateTimeField(auto_now_add=True, auto_now=False)
    # updated_at = models.DateTimeField(auto_now_add=False, auto_now=True)
    commit_no = models.IntegerField(null=False, default=1)
    project_name = models.CharField(max_length=50, null=False)
    repo_name = models.CharField(max_length=50, null=False)
    author_name = models.CharField(max_length=20, null=True)
    commit_id = models.CharField(max_length=50, null=True)
    commit_date = models.DateTimeField(auto_now=False)
    commit_message = models.CharField(max_length=200, null=True)
    files = models.CharField(max_length=3000, null=True)
    # date=models.dateTimeField()

    class Meta:
        db_table = 'repo_metadata'

    def __str__(self):
        return self.repo_name

    # def serializable_value(self, field_name):
    #     return self.__dict__

    # def serialize(self):
    #     return self.__dict__
    #     # return obj.__dict__


class Repo(models.Model):
    project_name = models.CharField(max_length=50, null=False)
    repo_name = models.CharField(max_length=50, null=False)
    latest_commit_no = models.IntegerField(null=False)
    latest_commit_date = models.DateTimeField(auto_now=False)

    class Meta:
        db_table = 'repo'
        unique_together = ('project_name', 'repo_name')

    def __str__(self):
        return self.repo_name
