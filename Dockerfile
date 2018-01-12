FROM python:3.6

RUN pip3 install --upgrade 
RUN pip3 install --upgrade google-api-python-client google-auth google-auth-oauthlib google-auth-httplib2