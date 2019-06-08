from __future__ import unicode_literals

from djongo import models


class RepoMetadata(models.Model):
    # created_at = models.DateTimeField(auto_now_add=True, auto_now=False)
    # updated_at = models.DateTimeField(auto_now_add=False, auto_now=True)
    commit_no = models.IntegerField(null=False, default=1)
    repo_name = models.CharField(max_length=50, null=False)
    commit_id = models.CharField(max_length=50, null=True)
    author_name = models.CharField(max_length=20, null=True)
    commit_date = models.DateTimeField(auto_now=False)
    commit_message = models.CharField(max_length=200, null=True)
    files = models.CharField(max_length=3000, null=True)
    # date=models.dateTimeField()

    class Meta:
        db_table = 'repo_metadata'

    def __str__(self):
        return self.repo_name


class Repo(models.Model):
    repo_name = models.CharField(max_length=50, null=False, unique=True)
    latest_commit_no = models.IntegerField(null=False)
    latest_commit_date = models.DateTimeField(auto_now=False)

    class Meta:
        db_table = 'repo'

    def __str__(self):
        return self.repo_name
