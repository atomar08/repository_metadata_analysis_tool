from django.http import HttpResponse
from github import Github

from .models import RepoMetadata
from .models import Repo
from django.conf import settings

from datetime import datetime

GIT_ACCOUNT_ID = settings.GIT_ACCOUNT_ID
GIT_ACCOUNT_KEY = settings.GIT_ACCOUNT_KEY

# g = Github("git user id", "git account pkey")
g = Github(GIT_ACCOUNT_ID, GIT_ACCOUNT_KEY)

# r4 = g.get_repo("notepad-plus-plus/notepad-plus-plus")  # 2998
# r4 = g.get_repo("apache/spark")  # 24165 commits
# r4 = g.get_repo("atomar08/cs537")  # 34 commits


def home(request):
    # queryset = RepoMetadata.objects.all()
    repo = request.GET.get('repo')
    repo_metadata = RepoMetadata.objects.all()
    print("In home".format(repo))
    check_repo(repo)

    # get_all_git_commits(repo)
    print("Hello Anjali")
    return HttpResponse("this url is working.. see terminal for op")


def check_repo(repo_name):
    # checking if repo information already exist or not, if not make an entry
    repo_objects = Repo.objects.filter(repo_name=repo_name)
    if not len(repo_objects):
        row = Repo(
            repo_name=repo_name,
            latest_commit_no=0,
            latest_commit_date=datetime.now()
        )
        row.save()
        # make git query for all records
        commit_no, commit_date = get_all_git_commits(repo_name)
        print("Received {} & {}".format(commit_no, commit_date))
        Repo.objects.filter(repo_name=repo_name)\
            .update(
                latest_commit_no=commit_no,
                latest_commit_date=commit_date
            )
    else:
        repo = repo_objects.first()
        print("Repo name: {}".format(repo.repo_name))
        # make git query from current records
    return


def get_all_git_commits(repo):
    r4 = g.get_repo("atomar08/{}".format(repo))
    commits = r4.get_commits()
    print("Repo name; ", r4.name)
    print("Total number of commits: ", commits.totalCount)
    print(type(commits))
    commit_date = ""
    commit_no = 0
    for commit_obj in commits.reversed:
        file_list = []
        for file in commit_obj.files:
            file_list.append(file.filename)

        commit_no = commit_no + 1
        commit_date = commit_obj.commit.committer.date
        data_obj = RepoMetadata(
            commit_no=commit_no,
            repo_name=r4.name,
            commit_id=commit_obj.commit.sha,
            # author_name = commit_obj.author.name,
            author_name=getattr(getattr(commit_obj, 'author'), 'name', ''),
            # author_name=commit_obj.get('author', '{}').get('name', ''),
            commit_date=commit_date,
            commit_message=commit_obj.commit.message,
            files=file_list
        )
        data_obj.save()
        # print("sha: {}".format(commit_obj.sha))
        # print(type(commit_obj.commit.committer.date))
        # d = datetime.datetime.strptime("2017-10-13T10:53:53.000Z", "%Y-%m-%dT%H:%M:%S.000Z")
        # print("commit date:{}\n".format(commit_obj.commit.committer.date))
    return commit_no, commit_date
