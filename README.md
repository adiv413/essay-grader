# Group 5 Understudyathon: Essay Grader

A platform to speed up essay grading.

https://essay-grader.sites.tjhsst.edu/

## Local Setup

 * Install RabbitMQ and Erlang
	* MacOS/Linux
		* Follow the instructions at https://www.rabbitmq.com/download.html
	* Windows
		* Issues during setup? Try going here:
			* https://www.rabbitmq.com/windows-quirks.html
		* For windows, it's easiest if you download RabbitMQ via Chocolatey. You can download Chocolatey here:
			* https://chocolatey.org/docs/installation
		* After you've installed chocolatey and made sure to add it to the PATH, make sure you're in a terminal which has administrative access and run 
			```
			choco install rabbitmq
			```
		* In a separate terminal window, go to the install location (such as C:\Program Files\RabbitMQ Server\rabbitmq_server-3.8.4) and add the sbin folder to the PATH. After this, run 
			```
			rabbitmq-server
			```
			* **Don't exit out of this terminal or stop this process when running any future commands. Instead, open up a separate terminal window and execute those tasks from there.** Stopping this process will kill the server, so you will have to start it again before running the Django app.
			* Note: since this command starts the server, you should see a picture of a rabbit in an ASCII-art format (this is RabbitMQ's logo), followed by some text, and finally a line which says "Starting broker"; no loading bars or anything special will pop up.

* Go to a suitable directory and clone the repository with
	* ```
  	  git clone git@gitlab.tjhsst.edu:understudyathon-2020/group-5/Essay-Grader.git
  	  ```
* Move into the folder where the repository was cloned
	* ```
	  cd Essay-Grader
	  ```

* Next setup a virtual environment with the virtualenv library(Install it with for)
	* MacOs/Linux
		* ```
		  python3 -m pip install --user virtualenv
		  ```
	* Windows
		* ```
		  py -m pip install --user virtualenv
		  ```
* Go to the directory where you cloned the repository and type
	* MacOs/Linux
		* ```
		  python3 -m venv venv
		  ```
	* Windows
		* ```
		  py -m venv venv
		  ```
* Next, you have to activate the virtual environment with
	* MacOS/Linux
		* ```
		  source venv/bin/activate
		  ```
	* Windows
		* ```
		  .\venv\Scripts\activate
		  ```
* Next, install all necessary libraries with the following command:
	* ```
	  pip3 install -r requirements.txt
	  ```
* Next, open up a new terminal window (don't close any of the other ones) and run:
	* ```
	  celery -A essay_grader worker -l info -P eventlet
	  ```
	* If you get an error regarding kombu, try running
	  ```
	  pip uninstall celery
	  pip install celery
	  ```
* At this point, you should have 3 terminal windows open
* In the empty terminal window, run:
	* ```
      python manage.py collectstatic
      python manage.py makemigrations
      python manage.py migrate
      python manage.py runserver
	  ```
	* And now go to http://127.0.0.1:8000/ to get access!
* Login via Ion
* Note: requires Python 3.6+

## Features
* Profile Management
	- [x] Settings
		- [x] Add teachers
		- [x] Change password
* Essay Checking 
	- [x] Spelling/Grammar
	- [x] Reference list formatting
	- [x] Citation formatting and style verification (conducted by an extensive home-made algorithm)
	- [x] Citation cross-referencing
	- [x] Plagarism Checker
* Interface:
	* Teacher 
		- [x] Seeing students essays and being able to grade them
		- [x] Add assignments
		- [x] Get notified via email when a student adds you as a teacher
		- [x] Comment system (interact with students)
	* Student
		- [x] Submitting essays via a rich text editor
		- [x] Get notified via email when your assignment is graded and when a new assignment is posted
* Automation
	- [x] Essay grading is automated by the use of Celery Workers
* Frameworks:
	* Django
	* Bootstrap
	* JQuery + AJAX
* Authentication:
	- [x] Login via OAuth
	- [x] Access information via Ion's API
	- [x] Role Based Access Control

