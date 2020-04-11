FROM python:3

# set a directory for the app
WORKDIR /Users/kavidey/github/ppe-exchange

# copy all the files to the container
COPY . .

# install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# setup database
RUN flask db init; flask db migrate -m "users table"; flask db upgrade

# define the port number the container should expose
EXPOSE 5000

# run the command
CMD ["flask", "run", "--host=0.0.0.0"]
