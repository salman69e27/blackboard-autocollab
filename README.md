
# Blackboard Autocollab

This is a simple script to auto attend online sessions on Blackboard lms.
## Installation inscructions:
You need to have python 3.x installed with Selenium library. To install selenium just run 
<code>pip install selenium</code> in your terminal/cmd.   
You also need chromedriver if you will open sessions with Google Chrome or geckodriver if you will open sessions with Firefox.   
To download chromedriver follow this link: https://chromedriver.storage.googleapis.com/index.html?path=2.38/  
To download geckodriver follow this link: https://github.com/mozilla/geckodriver/releases  
After the download is finished extract the zip file. 
Now clone the repo or download its contents and put the downloaded driver in the same folder as the script. 

## Configuration:
You need to make a `config.yml` file for the script to work. These are the required tags:  
<pre>
username: your blackboard username
password: your blackboard password
url: your schools blackboard url
timeout:  maximum time (in seconds) to wait for action (page elements loading for example) before raising an error
browser: browser to use. Possible options are: firefox, google-chrome
courses:
  1:
    name: course name
    weekday: weekday of the lecture
    time: lecture start time
    length: lecture duration
   2:
    ...
</pre>

For each course you need to provide a name, weekday, time, and length. The file config.yml has an example. Follow the same structure and be careful about the indentation.

Notice that the config file is case sensitive so you need to be careful. Also make sure that the values are written in quotation marks.

## Usage:
After finishing the config file, run the script `driver.py` and it will open any (one) scheduled session that is within five minutes. The script automatically checks the schedule every two minutes to see if a session is scheduled. If any error happend the script will close and try again after two minutes (if less than five minutes passed from the session start time). 

After successfully opening a session, the script will wait for ten minutes then try to read the number of participants in the session, and will automatically close the session if the number of participants fell to less than half the maximum number of participants it read before.  If for some reason the script failed to read the number of participants, it will close after the session duration has passed. 
It's recommended that you put the script in autostartup.
