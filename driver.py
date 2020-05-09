import traceback
import os
import traceback
import sys
from datetime import datetime, timedelta
from time import sleep
import yaml

weekdays = {'monday':0, 'tuesday':1, 'wednesday':2, 'thursday':3, 'friday':4, 'saturday':5, 'sunday':6}
path_to_config = os.path.join(sys.path[0], 'config.yml')
with open(path_to_config) as config:
    cfg = yaml.load(config, Loader=yaml.CLoader)

courses = cfg['courses']
for course in courses:
    courses[course]['hour'] = int(courses[course]['time'].split(':')[0])
    courses[course]['minute'] = int(courses[course]['time'].split(':')[1])
    courses[course]['weekday'] = weekdays[ courses[course]['weekday'].lower() ]

while True:
    try:
        for course in courses:
            course = courses[course]
            now = datetime.now()
            if course['weekday'] != now.weekday():
                continue
            course_time = datetime(now.year, now.month, now.day, course['hour'], course['minute']) 
            if abs(now-course_time) < timedelta(minutes=5):
                path_to_autocollab = os.path.join(sys.path[0], 'autocollab.py')
                command = 'python "{}" --username {} --password {} --url {} --timeout {} --browser {} --course "{}" --length {}'.format(path_to_autocollab, 
                        cfg['username'],
                        cfg['password'],
                        cfg['url'], 
                        cfg['timeout'], 
                        cfg['browser'], 
                        course['name'], 
                        course['length'])
                print('Entering course {}'.format(course['name']))
                os.system(command)
    except Exception as ex:
        traceback.print_exc()
        break
    sleep(120)
