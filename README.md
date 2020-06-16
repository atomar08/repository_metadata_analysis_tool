source env.sh
source ../venv/bin/activate
python manage.py runserver

## Installation ##
pip install --upgrade pip


djongo doc: 
https://nesdis.github.io/djongo/get-started/


PyGithub doc: i
https://github.com/PyGithub/PyGithub


brew update
brew install mongodb
brew services start mongodb


Celery Implementation:
https://www.rabbitmq.com/install-debian.html#apt
https://tecadmin.net/install-rabbitmq-server-on-ubuntu/


RabbitMQ:
Install RabbitMQ
sudo apt-get update
sudo apt-get upgrade
echo 'deb http://www.rabbitmq.com/debian/ testing main' | sudo tee /etc/apt/sources.list.d/rabbitmq.list
wget -O- https://www.rabbitmq.com/rabbitmq-release-signing-key.asc | sudo apt-key add -
sudo apt-get install rabbitmq-server


Using Init –
sudo update-rc.d rabbitmq-server defaults
sudo service rabbitmq-server start
sudo service rabbitmq-server stop


Uisng Systemctl –
sudo systemctl enable rabbitmq-server

sudo systemctl start rabbitmq-server

sudo systemctl stop rabbitmq-server


Use Celery:

source env.sh

cd repository_metadata_analysis_tool

celery -A VCM worker -l info


To run python django server:

source gitVenv/bin/activate

cd repository_metadata_analysis_tool

source env.sh

python manage.py runserver 8000


Sample Http Calls:


1. Validate Repo
http://127.0.0.1:8000/git/validate_repository?repo_name=cs537&project_name=atomar08

    Repo: cs537

    Project: atomar08


2. Search
http://localhost:8000/git/get_commits_id?repo_name=cs537&project_name=atomar08&commit_id=18e7c7cf000ecd7182f30ac645258fffcc2ed993

    Repo: cs537
    
    Project: atomar08
    
    Commit Id: 18e7c7cf000ecd7182f30ac645258fffcc2ed993


3. Pull Request:
http://localhost:8000/git/get_repo_pull_requests?project_name=githubtraining&repo_name=hellogitworld
    
    Repo: hellogitworld
    
    Project: githubtraining


4. Issues:
http://localhost:8000/git/get_repo_issues?project_name=JasonEtco&repo_name=todo

    Repo: todo
    
    Project: JasonEtco


5. Commits:
http://localhost:8000/git/get_commits_page?repo_name=notepad-plus-plus&project_name=notepad-plus-plus&records_per_page=5&page_number=2

    Repo: notepad-plus-plus
    
    Project: notepad-plus-plus
    
    Records per page: 5
    
    page_number: 2
