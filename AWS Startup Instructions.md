#### Update system
`sudo yum update -y`

#### Install tmux
`sudo yum install tmux -y

#### Install python3 and pip3
`sudo yum install python34 -y`
`sudo yum install python34-pip -y`

#### Upgrade pip
`sudo python3 -m pip install --upgrade pip`

#### Install git
`sudo yum install git -y`

#### Clone git repository
`git clone https://github.com/KaviMD/ppe-exchange.git`

#### Enter the git repo
`cd ppe-exchange`

#### Install virtualenv
`sudo python3 -m pip install virtualenv`

#### Create a new virtual enviornment
`python3 -m venv venv`
`virtualenv venv`

#### Enter the environment
`source venv/bin/activate`

#### Install libraries from requirements.txt
`pip install -r requirements.txt`

#### Create a new tmux session with
`tmux new -s ppe-exchange`

#### Start the server with
`flask run -h 0.0.0.0 -p 5000`

#### Exit the tmux session with
`CTRL-b` and then `d`

#### You can reattach to the session by running
`tmux a -t ppe-exchange`


#### You should be able to access the server by findings its hostname in the EC2 Console and going to:
`hostaname:5000'

If you cannot access it, make sure that:
1. The hostname is correct
2. The port is correct
3. That you have an inbound rule allowing access to port 5000
