from django.http import HttpResponse
from github import Github

from .models import RepoMetadata
from .models import Repo
from django.conf import settings

from datetime import datetime
from datetime import timedelta

GIT_ACCOUNT_ID = settings.GIT_ACCOUNT_ID
GIT_ACCOUNT_KEY = settings.GIT_ACCOUNT_KEY
GIT_USER_ID = settings.GIT_USER_ID

# g = Github("git user id", "git account pkey")
g = Github(GIT_ACCOUNT_ID, GIT_ACCOUNT_KEY)

# r4 = g.get_repo("notepad-plus-plus/notepad-plus-plus")  # 2998
# r4 = g.get_repo("apache/spark")  # 24165 commits
# r4 = g.get_repo("atomar08/cs537")  # 34 commits


def validate_repo(request):
    print("In validate repo")
    return


def get_commits(request):
    repo = request.GET.get('repo')
    print("received request to collect logs of {}".format(repo))

    collect_commits(repo)

    # get_all_commits(repo)
    print("Saved all commits")
    return HttpResponse("this url is working.. see terminal for op")


def collect_commits(repo_name):
    # checking if repo information already exist or not, if not make an entry
    repo_objects = Repo.objects.filter(repo_name=repo_name)
    if not len(repo_objects):
        print("first time request for {}".format(repo_name))
        row = Repo(
            repo_name=repo_name,
            latest_commit_no=0,
            latest_commit_date=datetime.now()
        )
        row.save()

        # make git query for all records
        total_commits, last_commit_date = get_all_commits(repo_name)
        print("Currently {} have {} commits & last commit is on {}".format(repo_name, total_commits, last_commit_date))
        Repo.objects.filter(repo_name=repo_name)\
            .update(
                latest_commit_no=total_commits,
                latest_commit_date=last_commit_date
            )
    else:
        print("received request for old repo {}".format(repo_name))
        repo = repo_objects.first()
        since = repo.latest_commit_date + timedelta(seconds=1)
        total_commits, last_commit_date = get_commits_since(repo_name, since, repo.latest_commit_no)
        # if their are no more commit don't update repo table entry
        if total_commits > repo.latest_commit_no:
            Repo.objects.filter(repo_name=repo_name) \
                .update(
                latest_commit_no=total_commits,
                latest_commit_date=last_commit_date
            )
        print("retrieved {} commits, last commit is from {}".format(total_commits-repo.latest_commit_no, last_commit_date))
    return


def get_commits_since(repo_name, since, latest_commit_no):
    repo = g.get_repo("{}/{}".format(GIT_USER_ID, repo_name))
    commits = repo.get_commits(since=since).reversed

    page_number = 0
    total_commits = commits.totalCount
    commit_date = ""
    commit_no = latest_commit_no

    while total_commits > 0:
        commits_page = commits.get_page(page_number)
        for commit_obj in commits_page:
            commit_no += 1
            # git save commit time/date is in UTC timezone
            commit_date = commit_obj.commit.committer.date  # type=datetime.datetime
            save_commit_metadata(commit_no, repo, commit_obj)
            total_commits -= 1
        page_number += 1
    print("collected commits from {} date".format(since))
    return commit_no, commit_date


def get_all_commits(repo_name):
    repo = g.get_repo("{}/{}".format(GIT_USER_ID, repo_name))
    commits = repo.get_commits()
    print("Repo name: ", repo.name)
    print("Total number of commits: ", commits.totalCount)
    commit_date = ""
    commit_no = 0
    for commit_obj in commits.reversed:
        commit_no +=    1
        commit_date = commit_obj.commit.committer.date  # type=datetime.datetime
        save_commit_metadata(commit_no, repo, commit_obj)
    return commit_no, commit_date


def save_commit_metadata(commit_no, repo, commit_obj):
    data_obj = RepoMetadata(
        commit_no=commit_no,
        repo_name=repo.name,
        commit_id=commit_obj.commit.sha,
        author_name=getattr(getattr(commit_obj, 'committer'), 'login', ''),
        # author_name=getattr(getattr(commit_obj, 'author'), 'name', ''),
        # author_name=commit_obj.get('author', '{}').get('name', ''),
        commit_date=commit_obj.commit.committer.date,  # git save commit time/date is in UTC timezone
        commit_message=commit_obj.commit.message,
        files=collect_commit_files(commit_obj)
    )
    data_obj.save()


def collect_commit_files(commit_obj):
    file_list = []
    for file in commit_obj.files:
        file_list.append(file.filename)
    return file_list
