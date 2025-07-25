Linux ubuntu 22.04 is required.

Steps to Run application without docker. 

Python 3.10 or above versions.

sudo apt install python3-pip -y

sudo apt install postgresql (version should be >= 14)
   . inside this path /etc/postgresql/16/main
   . Open postgresql.conf : 
      . Make sure -> listen_addresses = '*'
    . Open pg_hba.conf :
      . Make sure inside IPv4 host value should be : 127.0.0.1 and mode = md5 

OPtional : sudo apt install pgbouncer
    . For connection pooling.
    . Inside database host : 6432 (by default)

sudo apt install redis
sudo apt update && sudo apt upgrade
sudo systemctl enable postgresql
sudo systemctl enable redis
sudo systemctl enable pgbouncer.service


Take clone: 
   . git clone <url>

create virtual environment using:
 . python3.10 -m venv env

pip install -r requirements.txt

There are two ways create .env file or inside env/bin/activate:
  . Write environment variables as mentioned in envtemplate

Now deactivate the env and again activate it.

Make sure database, smtp creds should be correctly mention in environment variables.

Run command: 
python3 deploy.py


Steps to Run application using docker.

Install docker engine:

  . Follow these steps mentioned in below url.:
  https://docs.docker.com/engine/install/ubuntu/

Run command:
  . docker-compose up