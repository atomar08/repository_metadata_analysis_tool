import string

from django.contrib.auth.models import User
from django.utils.crypto import get_random_string

from celery import shared_task

# @shared_task
# def create_random_user_accounts(total):
#     for i in range(total):
#         username = 'user_{}'.format(get_random_string(10, string.ascii_letters))
#         email = '{}@example.com'.format(username)
#         password = get_random_string(50)
#         User.objects.create_user(username=username, email=email, password=password)
#     return '{} random users created with success!'.format(total)

def get_commits_since(project_name, repo_name, since, latest_commit_no):
    print("**********In tasks.py: get_commits_since()**********")
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
    print("**********In tasks.py: get_all_commits()**********")
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

