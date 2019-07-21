import json
from datetime import datetime
from datetime import timedelta

from django.conf import settings
from django.core import serializers
from django.http import HttpResponse
from github import Github

from .models import Repo
from .models import RepoMetadata

GIT_ACCOUNT_ID = settings.GIT_ACCOUNT_ID
GIT_ACCOUNT_KEY = settings.GIT_ACCOUNT_KEY

# g = Github("git user id", "git account pkey")
g = Github(GIT_ACCOUNT_ID, GIT_ACCOUNT_KEY)


# r4 = g.get_repo("notepad-plus-plus/notepad-plus-plus")  # 2998
# r4 = g.get_repo("apache/spark")  # 24165 commits
# r4 = g.get_repo("atomar08/cs537")  # 34 commits

# test method to test any new functionality
def test(request):
    print("in git test method")
    repo_name = request.GET.get('repo_name')
    project_name = request.GET.get('project_name')

    print("returning from git test")
    return HttpResponse("git_test completed successfully. data ".format())


def validate_repository(request):
    print("In validate repository")
    project_name = request.GET.get('project_name')
    repo_name = request.GET.get('repo_name')
    if is_repo_valid(project_name, repo_name):
        return HttpResponse("Valid repository")
    else:
        return HttpResponse("Invalid repository", status=412)


def get_commits(request):
    project_name = request.GET.get('project_name')
    repo_name = request.GET.get('repo_name')
    print("received request to collect logs of {} repo under {} project".format(repo_name, project_name))

    if not is_repo_valid(project_name, repo_name):
        return HttpResponse("Invalid repository", status=412)

    collect_commits(project_name, repo_name)
    repo_metadata_dic = read_repo_metadata(project_name, repo_name)

    # print("Saved all commits, going to return type {}, {}".format(type(repo_metadata), repo_metadata))
    response_data = dict()
    response_data['metadata'] = repo_metadata_dic
    response_data['project_name'] = project_name
    response_data['repo_name'] = repo_name
    response_data['number_commits'] = len(repo_metadata_dic)
    print("created response, sending back")
    return HttpResponse(json.dumps(response_data), content_type='application/json', status=200)


####### Helper Methods #######


def is_repo_valid(project_name, repo_name):
    try:
        g.get_repo("{}/{}".format(project_name, repo_name))
    except Exception as e:
        # please refer: GithubException.py/UnknownObjectException
        # print("e: {}, type: {}, status: {}, message: {}".format(e, type(e), e.status, e.data.get('message')))
        if e.status == 404 and e.data.get('message', '') == 'Not Found':
            return False
        else:
            raise e
    return True


def read_repo_metadata(project_name, repo_name):
    print("in read_repo_metadata, project name {}, repo name {}".format(project_name, repo_name))
    repo_metadata_content = RepoMetadata.objects.filter(project_name=project_name, repo_name=repo_name)

    # metadata_rows = json.loads(serializers.serialize('json', list(repo_metadata_content), fields=('commit_no',
    # 'author_name')))
    metadata_rows = json.loads(serializers.serialize('json', repo_metadata_content,
                                                     fields=(
                                                         'commit_no',
                                                         'project_name',
                                                         'repo_name',
                                                         'commit_id',
                                                         'author_name',
                                                         'commit_date',
                                                         'commit_message',
                                                         'files')))
    # print("response type 1: {}, {}, {}".format(type(metadata_rows), metadata_rows[0], metadata_rows[-1]['fields']))
    metadata_list = []
    for commit in metadata_rows:
        metadata_list.append(commit.get('fields', {}))

    # print("in read_repo_metadata, response {}".format(metadata_list))
    print("successfully completed read_repo_metadata()")
    return metadata_list


def collect_commits(project_name, repo_name):
    # method to get all commits, if we already have few commits pull only new commits
    # checking if repo information already exist or not, if not make an entry
    repo_objects = Repo.objects.filter(project_name=project_name, repo_name=repo_name)
    if not len(repo_objects):
        print("first time request for {}".format(repo_name))
        row = Repo(
            project_name=project_name,
            repo_name=repo_name,
            latest_commit_no=0,
            latest_commit_date=datetime.now()
        )
        row.save()

        # Feature: if mongo do down here what will happen because next time if request comes it will request from
        # current time and may be no commit comes at all

        # make git query for all records
        total_commits, last_commit_date = get_all_commits(project_name, repo_name)
        print("currently {} have {} commits & last commit is on {}".format(repo_name, total_commits, last_commit_date))
        Repo.objects.filter(project_name=project_name, repo_name=repo_name) \
            .update(
            latest_commit_no=total_commits,
            latest_commit_date=last_commit_date
        )
    else:
        # we already have few commits, so just pull new commits from github
        print("received request for old repo {} under {} project".format(repo_name, project_name))
        repo = repo_objects.first()
        since = repo.latest_commit_date + timedelta(seconds=1)
        total_commits, last_commit_date = get_commits_since(project_name, repo_name, since, repo.latest_commit_no)
        # if their are no more commit don't update repo table entry
        if total_commits > repo.latest_commit_no:
            Repo.objects.filter(project_name=project_name, repo_name=repo_name) \
                .update(
                latest_commit_no=total_commits,
                latest_commit_date=last_commit_date
            )
        print("retrieved {} commits, last commit is from {}".format(total_commits - repo.latest_commit_no,
                                                                    last_commit_date))
    return


def get_commits_since(project_name, repo_name, since, latest_commit_no):
    repo = g.get_repo("{}/{}".format(project_name, repo_name))
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


def get_all_commits(project_name, repo_name):
    repo = g.get_repo("{}/{}".format(project_name, repo_name))
    commits = repo.get_commits()
    print("Repo name: ", repo.name)
    print("Total number of commits: ", commits.totalCount)
    commit_date = ""
    commit_no = 0
    for commit_obj in commits.reversed:
        commit_no += 1
        commit_date = commit_obj.commit.committer.date  # type=datetime.datetime
        save_commit_metadata(commit_no, repo, commit_obj)
    return commit_no, commit_date


def save_commit_metadata(commit_no, repo, commit_obj):
    data_obj = RepoMetadata(
        commit_no=commit_no,
        project_name=repo.full_name.split('/')[0],  # this is not 100% sure logic or u can pass project name
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
