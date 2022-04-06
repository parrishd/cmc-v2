FROM python:3.9.8-buster


# RUN apt update; \
#    apt install -y build-essential g++ unixodbc-dev libsodium-dev \

RUN curl https://packages.microsoft.com/keys/microsoft.asc | apt-key add -; \
    curl https://packages.microsoft.com/config/debian/10/prod.list > /etc/apt/sources.list.d/mssql-release.list; \
    apt update; \
    ACCEPT_EULA=Y apt install -y msodbcsql17; \
    apt install -y build-essential g++ unixodbc-dev libsodium-dev libgssapi-krb5-2; \
    echo 'export PATH="$PATH:/opt/mssql-tools/bin"' >> ~/.bashrc;
    # source ~/.bashrc

WORKDIR /app

COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt

COPY . .

ENV FLASK_APP=api
ENV FLASK_ENV=development

CMD [ "python3", "-m" , "flask", "run", "--host=0.0.0.0"]

EXPOSE 5000
