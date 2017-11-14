FROM python:3
MAINTAINER Tue Haulund <tue.haulund@gmail.com>

ENV INSTALL_PATH /JSONVault
RUN mkdir -p $INSTALL_PATH
WORKDIR $INSTALL_PATH

COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt

COPY . .

CMD ["python", "jsonvault.py"]