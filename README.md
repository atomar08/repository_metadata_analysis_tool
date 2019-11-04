source env.sh
source ../venv/bin/activate
python manage.py runserver

## Installation ##
pip install --upgrade pip

pip install django

pip install django-cors-headers

pip install djangorestframework

djongo doc: https://nesdis.github.io/djongo/get-started/
pip install djongo

PyGithub doc: https://github.com/PyGithub/PyGithub
pip install PyGithub

brew update
brew install mongodb
brew services start mongodb

Celery Implementation:
pip install Celery
Install RabbitMQ

Use Celery:
source env.sh
cd repository_metadata_analysis_tool
celery -A VCM worker -l info

