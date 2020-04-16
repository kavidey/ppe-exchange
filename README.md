# PPE Exchange Website

## Getting Started with Python
1. Download and install [Python3](https://www.python.org/downloads/)
2. Run `pip install -r requirements.txt` in the root folder of this directory to install the necessary libraries. (You may need to use pip3 instead of pip based on your python installation)
3. Start the website by running the command `flask run` in the root directory.
    1. The ip address can be changed by adding `--host [new ip address]` to the command
    2. The port can be changed by adding `--port [new port]`

## Getting Started with Docker
1. Download and install [Docker](https://docs.docker.com/get-docker/)
2. Run the command ``docker run -p 5000:5000 kavidey/ppe-exchange``

## Usage
1. By default, the website will run on [http://127.0.0.1:5000/](http://127.0.0.1:5000/)
2. There will be a warning about not having entered login email login info. Don't worry about that, 90% of the website will still work.