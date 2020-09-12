# AWS EC2 Instance Startup Instructions

After creating an EC2 instance of OS type Amazon Linux, ssh into it using the generated security key and follow these instructions to setup the server.
`ssh -i [keypair].pem ubuntu@[Elastic IP Address]`

## Install Dependencies
#### Update system
`sudo apt-get update -y`

#### Install tmux and nginx
`sudo apt-get install nginx -y`

#### Install pip3
`sudo apt install python3-pip -y`

#### Upgrade pip
`sudo python3 -m pip install --upgrade pip`

#### Clone git repository
`git clone https://github.com/KaviMD/ppe-exchange.git`

#### Enter the git repo
`cd ppe-exchange`

#### Install virtualenv
`sudo apt-get install python3-venv -y`
`sudo apt install virtualenv -y`

#### Set the correct timezone
https://stackoverflow.com/questions/34394279/how-to-set-aws-amazon-server-time-cant-find-etc-sysconfig-clock-file

## Setup nginx [guide] (https://chrisdtran.com/2017/deploy-flask-on-ec2/)
#### Delete default nginx server
`sudo rm /etc/nginx/sites-enabled/default`

#### Create a symlink for the server config file
`sudo ln -s ~/ppe-exchange/example.com /etc/nginx/sites-enabled/example.com`

#### Copy the SSL Certificate and Key on to the server using scp

#### Update the example.com file with the correct domain name and SSL Certificate and Key locations

#### Restart nginx to apply changes
`sudo service nginx restart`

## Setup Website
#### Create a new virtual enviornment
`python3 -m venv venv`

#### Enter the environment
`source venv/bin/activate`

#### Install libraries from requirements.txt
`pip install -r requirements.txt`

#### Create a new tmux session with
`tmux new -s ppe-exchange`

#### Start the server with
`flask run -h localhost -p 5000`

#### Exit the tmux session with
`CTRL-b` and then `d`

#### You can reattach to the session by running
`tmux a -t ppe-exchange`


#### You should be able to access the server by findings its hostname in the EC2 Console and going to:
`[Elastic IP Address]`

If you cannot access it, make sure that:
1. The hostname is correct
3. That you have an inbound rule allowing access to port 5000
