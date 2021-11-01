FROM python:3.7

 EXPOSE 8080

 ENV SPOTIFY_client_id='0000000'
 ENV SPOTIFY_client_secret='0000000'
 ENV SPOTIFY_redirect_uri='http://localhost:8080/'
 ENV SPOTIFY_username='default'

 ENV DEEZER_application_id='default'
 ENV DEEZER_secret_key='default'

 WORKDIR /usr/src/app

 RUN /usr/local/bin/python -m pip install --upgrade pip

 RUN pip install pipenv

 COPY . .

 RUN pipenv install --system

 CMD [ "python" ,"main.py" ]