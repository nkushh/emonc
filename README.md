# emonc
A small flask API that reads data from google sheets, processes it, formats it in a specific format and saves to the database.

The purpose of this project is Emergency Obstetric & Newborn Care (EmONC) Mentorship program takes the classroom to public hospitals 
to ensure providers have the sustained skills to deliver life-saving care. This program empowers government midwives with a toolkit 
to provide standardized peer coaching and mentorship. An integral part of this program is Continuing Medical Education (CME) and 
drills – activities paramount to enhancing practitioners' skills.

This repository contains a Flask API application that fetches data from Google Sheets using the gspread library, processes the data, 
converts it into JSON objects, and finally, saves the processed data to a PostgreSQL database.

Prerequisites
Python 3.x
Google account with access to Google Sheets
PostgreSQL database with appropriate credentials

Setup
Create a directory/folder in your computer at a location of your choosing.
mkdir folder-name

cd into the created directory
cd /path/to/folder

Clone the repository:
git clone https://github.com/nkushh/emonc.git

Create a virtual environment
python -m venv virtual-environment-name

Install the required dependencies:

pip install -r requirements.txt

Configure Google Sheets API:

Go to the Google Developers Console and create a new project.
Enable the Google Sheets API for the project.
Create credentials (OAuth client ID) and download the JSON file.
Rename the JSON file to client_secret.json and place it in the config directory.

Configure PostgreSQL:
Open your configuration file or application entry point file and fill in your PostgreSQL database credentials.

Initialize the database and start the Flask app

Containerize the project using Docker
- Create a Dockerfile at the root of your app.
- Dockerfile lists out instructions to create layers that will be found in a docker image.
- Each line in a Dockerfile represents an individual layer of the image being created.
- The first instruction in Dockerfile is the parent Image/layer. FROM is the keyword used.
- The next layer is the WORKDIR which specifies the working directory for the project. It tells docker for any commands after this instruction should be done from inside the working directory.
- This is followed by the COPY instruction that copies the source files to the specified working directory.
- The RUN instruction follows and it takes the command to install dependencies of the project.
- EXPOSE command is usually used for port mapping but is optional.
- The CMD instruction takes commands that should be run at runtime when the container begins to run. It is a list of individual words in a command e.g. ["python",  "manage.py"]
Once the Dockerfile is complete and correct run the command docker build -t image_name . This command will create a docker image based on the instructions in the Dockerfile.
- The file .dockerignore is used to specify which files to ignore when creating an image. The ignored files will not be included in the docker image.

- To run an image to create a container you can use the image name or id.
- To view all images and their details run the command docker images.
- To run the image of choice to create a container for our application run the command docker run --name container_name -p exposed_port:port_number image_name. The port number is only necessary if in the Dockerfile you specified a port to EXPOSE.
- To view all running containers run the command docker ps. docker ps -a lists all available containers whether running or not.
- To stop a running container run the command docker stop container_name
- You can restart an existing container instead of creating a new one each time by running the command docker start container_name
- To delete a docker image you run the command docker image rm image_name. This works only if there is no container linked to it. This behavior can be overidden by docker image rm image_name -f.
- You can delete a container first before trying to delete an image. The command to delete containers is docker container rm container_name
- To remove all docker containers as well as images and volumes at once you can run the command docker system prune -a 
- In docker there is an option of versioning of your images to be re-used based on need by running the command docker build -t image_name:version name . 
- Docker images are read-only when created meaning that if you were to make any changes to your source code you will have to rebuild the image again for the changes to be effected.

Usage
The application is currently hosted on Render.
The default endpoint is https://emonc.onrender.com
To view all the current existing data, access the API by sending GET requests to http://localhost:5000/get_participations.

To featch, process, format and store data from the google sheet, send the POST request to http://localhost:5000/process_and_store the API fetches data from Google Sheets, processes it, and stores it in the PostgreSQL database.
Check the logs for information about the API's behavior and database updates.
Endpoints
GET /get_participations: Fetches data that has already been processed and saved in the database, and returns a list of objects.
POST /process_and_store: Fetches data from Google Sheets, processes it, saves it to the database, and returns a success message.
GET /delete_participations: deletes all existing data from teh database, and returns a success message.
