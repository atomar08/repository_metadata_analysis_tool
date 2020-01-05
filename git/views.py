import json
import time

from celery import shared_task
from datetime import datetime
from datetime import timedelta

from django.conf import settings
from django.core import serializers
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.http import HttpResponse
from github import Github

from .models import Repo
from .models import RepoMetadata

GIT_ACCOUNT_ID = settings.GIT_ACCOUNT_ID
GIT_ACCOUNT_KEY = settings.GIT_ACCOUNT_KEY

# g = Github("git user id", "git account pkey")
g = Github(GIT_ACCOUNT_ID, GIT_ACCOUNT_KEY)

NUMBER_OF_RECORDS_PER_PAGE = 10
NEW_REPO_INITIAL_SLEEP_DURATION = 7

# r4 = g.get_repo("notepad-plus-plus/notepad-plus-plus")  # 2998
# r4 = g.get_repo("apache/spark")  # 24165 commits
# r4 = g.get_repo("atomar08/cs537")  # 34 commits


# test method to test any new functionality
def test(request):
    print("in git test method")
    repo_name = request.GET.get('repo_name')
    project_name = request.GET.get('project_name')

    repo = g.get_repo("{}/{}".format(project_name, repo_name))
    commits = repo.get_issues()

    page_number = 0
    total_commits = commits.totalCount
    commit_date = ""
    commit_no = 0

    while total_commits > 0:
        commits_page = commits.get_page(page_number)
        for commit_obj in commits_page:
            commit_no += 1
            # print("commit_obj: {}, type: {}".format(commit_obj, type(commit_obj)))
            # id = commit_obj.id
            # title = commit_obj.title
            # state = commit_obj.state
            # number = commit_obj.number
            # milestone = commit_obj.milestone
            # body = commit_obj.body
            # print("title: {}, {}, {}, {}, {}, {}".format(id, title, state, number, milestone, body))
            # comments_count = commit_obj.comments 
            # created_at = commit_obj.created_at
            # user_login = getattr(getattr(commit_obj, 'user'), 'login', '')
            # user_name = getattr(getattr(commit_obj, 'user'), 'name', '')

            total_commits -= 1
        page_number += 1
    
    metadata_list = [total_commits]
    response_data = dict()
    response_data['metadata'] = metadata_list
    response_data['project_name'] = project_name
    response_data['repo_name'] = repo_name
    response_data['number_commits'] = len(metadata_list)
    print("created response, sending back")

    return HttpResponse(json.dumps(response_data), content_type='application/json', status=200)

    # print("in read_repo_metadata, response {}".format(metadata_list))
    # print("successfully completed read_repo_metadata()")
    # dev
    # print("returning from git test")
    # return HttpResponse("git_test completed successfully. data ".format(), status=200)

# def search(request):
#     project_name = request.GET.get('project_name')
#     repo_name = request.GET.get('repo_name')
#     commit_id = request.GET.get('commit_id')
#     print("received request to collect commit_id of {} repo under {} project".format(repo_name, project_name))


def validate_repository(request):
    print("In validate repository")
    project_name = request.GET.get('project_name')
    repo_name = request.GET.get('repo_name')
    if is_repo_valid(project_name, repo_name):
        return HttpResponse("Valid repository")
    else:
        return HttpResponse("Invalid repository", status=404)


def get_commits(request):
    """
    Http method to collect all commits from git-hub server, save locally and then return all commits
    :param request:
        project_name
        repo_name
    :return:
        http_response
    """
    project_name = request.GET.get('project_name')
    repo_name = request.GET.get('repo_name')
    print("received request to collect logs of {} repo under {} project".format(repo_name, project_name))

    if not is_repo_valid(project_name, repo_name):
        return HttpResponse("Invalid repository", status=404)

    collect_commits.delay(project_name, repo_name)
    should_i_wait(project_name, repo_name)
    repo_metadata_list = read_repo_metadata(project_name, repo_name)

    # print("Saved all commits, going to return type {}, {}".format(type(repo_metadata), repo_metadata))
    response_data = dict()
    response_data['metadata'] = repo_metadata_list
    response_data['project_name'] = project_name
    response_data['repo_name'] = repo_name
    response_data['number_commits'] = len(repo_metadata_list)
    print("created response, sending back")
    return HttpResponse(json.dumps(response_data), content_type='application/json', status=200)


def get_commits_page(request):
    """
    Http method to collect all commits from git-hub server, save locally and then return 
    first commits page
    :param request:
        project_name
        repo_name
        page_number
        records_per_page
    :return:
    """
    project_name = request.GET.get('project_name')
    repo_name = request.GET.get('repo_name')
    page_number = request.GET.get('page_number')
    records_per_page = request.GET.get('records_per_page', NUMBER_OF_RECORDS_PER_PAGE)
    print("received request to collect logs of {} repo under {} project".format(repo_name, project_name))

    if not is_repo_valid(project_name, repo_name):
        return HttpResponse("Invalid repository", status=404)

    # collect_commits(project_name, repo_name) # original
    collect_commits.delay(project_name, repo_name) # celery implementation
    should_i_wait(project_name, repo_name)
    return read_repo_metadata_page(project_name, repo_name, page_number, records_per_page)


def read_commits_page(request):
    """
    Http method to get repository commits (page-wise) present locally
    :param request:
        project_name
        repo_name
        page_number
        records_per_page
    :return:
    """
    project_name = request.GET.get('project_name')
    repo_name = request.GET.get('repo_name')
    page_number = request.GET.get('page_number', 1)
    records_per_page = request.GET.get('records_per_page', NUMBER_OF_RECORDS_PER_PAGE)
    print("received request to collect logs from project {}, repo {}, page number: {}, records/page: {}".format(
        project_name, repo_name, page_number, records_per_page))

    if not is_repo_valid(project_name, repo_name):
        return HttpResponse("Invalid repository", status=404)

    # if not is_repo_information_present_locally(project_name, repo_name):
    #     return HttpResponse("New repository, please pull metadata using /get_commits_page/",
    #                         status=303)  # 303: See Other
    collect_commits.delay(project_name, repo_name)
    should_i_wait(project_name, repo_name)
    return read_repo_metadata_page(project_name, repo_name, page_number, records_per_page)


def get_commits_id(request):
    print("in read repo  page")
    repo_name = request.GET.get('repo_name')
    project_name = request.GET.get('project_name')
    commit_id=request.GET.get('commit_id')
    collect_data1 = collect_data(project_name, repo_name, commit_id)
    print("received cid", type(collect_data1))
    return  collect_data1 
    # return read_repo_metadata_page(project_name, repo_name, page_number, records_per_page)


def get_repo_issues(request):
    print("in get_repo_issues method")
    repo_name = request.GET.get('repo_name')
    project_name = request.GET.get('project_name')

    repo = g.get_repo("{}/{}".format(project_name, repo_name))
    repo_issues = repo.get_issues().reversed

    page_number = 0
    total_issues = repo_issues.totalCount
    commit_date = ""
    issue_no = 0
    repo_issue_list = []

    while total_issues > 0:
        repo_issues_page = repo_issues.get_page(page_number)
        for issue_obj in repo_issues_page:
            # issue = dict()
            issue = {}
            issue_no += 1
            issue_id = issue_obj.id
            issue_title = issue_obj.title
            issue_state = issue_obj.state
            issue_number = issue_obj.number
            issue_milestone = issue_obj.milestone
            issue_body = issue_obj.body
            issue_user_name = getattr(getattr(issue_obj, 'user'), 'name', '')
            issue_user_login = getattr(getattr(issue_obj, 'user'), 'login', '')
            issue_comment_count = issue_obj.comments 
            issue_created_at = issue_obj.created_at

            issue['issue_no'] = issue_no
            issue['issue_id'] = issue_id
            issue['issue_title'] = issue_title
            issue['issue_state'] = issue_state
            issue['issue_number'] = issue_number
            issue['issue_milestone'] = issue_milestone
            issue['issue_body'] = issue_body
            issue['issue_user_name'] = issue_user_name
            issue['issue_user_login'] = issue_user_login
            issue['issue_comment_count'] = issue_comment_count
            issue['issue_created_at'] = str(issue_created_at)
            repo_issue_list.append(issue)
            # print("================")
            # print("ID: {}, {}, {}".format(issue_id, issue_title, issue_state))
            # print("No: {}, {}, {}".format(issue_number, issue_milestone, issue_body))
            # print("User: {}, {}, {}, {}".format(issue_user_name, issue_user_login, issue_comment_count, issue_created_at))
            # print("******************")
            print("issue_id:{}, issue_number:{}, issue_created_at:{}".format(issue_id, issue_number, issue_created_at))
            total_issues -= 1
        page_number += 1
    
    # repo_issue_list = [total_issues]
    response_data = dict()
    response_data['repo_issues'] = repo_issue_list
    response_data['project_name'] = project_name
    response_data['repo_name'] = repo_name
    response_data['number_of_issues'] = len(repo_issue_list)
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


def is_repo_information_present_locally(project_name, repo_name):
    repo_metadata_content = RepoMetadata.objects.filter(project_name=project_name, repo_name=repo_name)
    print("in is_repo_information_present_locally(): ", type(repo_metadata_content))
    if repo_metadata_content.exists():
        return True
    return False


def read_repo_metadata_page(project_name, repo_name, page_no=1, records_per_page=NUMBER_OF_RECORDS_PER_PAGE):
    # DEV
    # Pagination doc:
    # https://simpleisbetterthancomplex.com/tutorial/2016/08/03/how-to-paginate-with-django.html
    # Efficiency: https://stackoverflow.com/questions/16161727/efficient-pagination-and-database-querying-in-django

    print("in read repo metadata page")
    status_code = 200
    response_message = "OK"
    repo_metadata_content = RepoMetadata.objects.filter(project_name=project_name, repo_name=repo_name).order_by(
        'commit_no')
    metadata_paginator = Paginator(repo_metadata_content, records_per_page)
    try:
        print("In read_repo_metadata_page reading page number {}, records/page: {}".format(page_no, records_per_page))
        metadata_page = metadata_paginator.page(page_no)
    except PageNotAnInteger:
        status_code = 200
        response_message = "requested page number is not an integer, re-setting to page 1"
        print("page number is not an integer, re-setting to page 1")
        page_no = 1
        metadata_page = metadata_paginator.page(page_no)
    except EmptyPage:
        status_code = 200
        response_message = "requested page number is not valid, re-setting to page 1"
        print("invalid page number, re-setting to page 1")
        page_no = 1
        # page_no = metadata_paginator.num_pages
        metadata_page = metadata_paginator.page(page_no)

    print("Total no of records: ", metadata_paginator.count)
    print("Total no of pages: ", metadata_paginator.num_pages)
    print("has next page: ", metadata_page.has_next())
    if metadata_page.has_next():
        print("Next page number:", metadata_page.next_page_number())
    print("has previous page: ", metadata_page.has_previous())
    if metadata_page.has_previous():
        print("Previous page number: ", metadata_page.previous_page_number())
    print("Page start index: ", metadata_page.start_index())  # Exception: InvalidPage
    print("Page end index: ", metadata_page.end_index())  # Exception: InvalidPage

    commits_list = serialize_commit_records(metadata_page)
    response_data = dict()
    response_data['project_name'] = project_name
    response_data['repository_name'] = repo_name
    response_data['metadata'] = commits_list
    response_data['numbercd_of_commits'] = len(commits_list)
    response_data['commit_start_index'] = metadata_page.start_index()
    response_data['commit_end_index'] = metadata_page.end_index()
    response_data['current_page_number'] = page_no
    response_data['total_number_of_pages'] = metadata_paginator.num_pages
    response_data['total_number_of_commits'] = metadata_paginator.count
    response_data['has_next_page'] = metadata_page.has_next()
    response_data['has_previous_page'] = metadata_page.has_previous()
    response_data['message'] = response_message
    print("created response, sending back")

    return HttpResponse(json.dumps(response_data), content_type='application/json', status=status_code)


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
    commits_list = []
    for commit in metadata_rows:
        commits_list.append(commit.get('fields', {}))

    # print("in read_repo_metadata, response {}".format(metadata_list))
    print("successfully completed read_repo_metadata()")
    return commits_list

@shared_task
def collect_commits(project_name, repo_name):
    print("********* in collect commits *********")
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
    print("****** get commits since ********")
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
    try:
        print("*********** get all commits ********")
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
    except Exception as e:
        print("got exception. Error: {}".format(e))
        return commit_no, commit_date


def serialize_commit_records(commit_records):
    commit_rows = json.loads(serializers.serialize('json', commit_records,
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
    commits_list = []
    for commit in commit_rows:
        commits_list.append(commit.get('fields', {}))
    return commits_list

 
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
    '''
    Helper method to return all modified files in passed git commit object.

    Parameters:
    commit_obj: Git Commit Object collected from git

    Returns:
    list: list of files modified in commit
    '''

    file_list = []
    for file in commit_obj.files:
        file_list.append(file.filename)
    return file_list


def collect_data(project_name, repo_name,commit_id):
   status_code=200
   repo_data= RepoMetadata.objects.filter(commit_id=commit_id)
   commits_list = serialize_commit_records(repo_data)
   response_data = dict()
   response_data['project_name'] = project_name
   response_data['repository_name'] = repo_name
   response_data['metadata'] = commits_list
   print("successfully completed read_data()")
   return HttpResponse(json.dumps(response_data), content_type='application/json', status=status_code)


def should_i_wait(project_name, repo_name):
    repo_objects = Repo.objects.filter(project_name=project_name, repo_name=repo_name)
    if not len(repo_objects):
        time.sleep(NEW_REPO_INITIAL_SLEEP_DURATION)