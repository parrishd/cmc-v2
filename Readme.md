### Virtual Environment

Be sure to be using python 3.6 or greater.

Create the virtual environment
```shell
python -m venv venv
```

Activate the environment
```shell
. venv/bin/activate
```

Install the requirements
```shell
pip install -r requirements.txt
```

Update requirements.txt (when new packages are added)
```shell
pip freeze > requirements.txt
```

Running the instance
```shell
export FLASK_APP=api
export FLASK_ENV=development
flask run
```

#### References
https://flask.palletsprojects.com/en/2.0.x/installation/

#### Mac drivers/odbc drivers
```shell
brew install unixodbc
brew tap microsoft/mssql-release https://github.com/Microsoft/homebrew-mssql-release
brew update
brew install msodbcsql mssql-tools
```

#### Local Development Setup with Docker (Mac/Linux(?))

Pull and run Docker container. Using v2017 since it is the oldest available image
```shell
docker pull mcr.microsoft.com/mssql/server:2017-latest
docker run -d --name vims_sql_server -e 'ACCEPT_EULA=Y' -e 'SA_PASSWORD=V1m5DevDB' -p 1433:1433 mcr.microsoft.com/mssql/server:2017-latest
```

Install the command line tools and test connectivity
```shell
sudo npm install -g sql-cli
mssql -u sa -p V1m5DevDB -- may need new terminal if mssql command is not on path
```

Download and restore the CMC database
```shell
docker exec -it vims_sql_server mkdir /var/opt/mssql/backup
docker cp ~/Downloads/CMC_Backup_2022-03-18_14-41-43.txt vims_sql_server:/var/opt/mssql/backup

docker exec -it vims_sql_server /opt/mssql-tools/bin/sqlcmd -S localhost \
   -U SA -P 'V1m5DevDB' \
   -Q 'RESTORE FILELISTONLY FROM DISK = "/var/opt/mssql/backup/CMC_Backup_2022-03-18_14-41-43.txt"' \
   | tr -s ' ' | cut -d ' ' -f 1-2

docker exec -it vims_sql_server /opt/mssql-tools/bin/sqlcmd \
   -S localhost -U SA -P 'V1m5DevDB' \
   -Q 'RESTORE DATABASE vims FROM DISK = "/var/opt/mssql/backup/CMC_Backup_2022-03-18_14-41-43.txt" WITH MOVE "CMC" TO "/var/opt/mssql/data/vims.mdf", MOVE "CMC_Log" TO "/var/opt/mssql/data/vims.ldf"'
```
Reference: https://docs.microsoft.com/en-us/sql/linux/tutorial-restore-backup-in-sql-server-container?view=sql-server-ver15

#### Paseto
Install libsodium
```shell
brew install libsodium
```
Paseto: https://github.com/purificant/python-paseto
