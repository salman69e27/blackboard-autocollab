from os.path import join
import re
import traceback
from time import sleep
from datetime import datetime, timedelta
from selenium import webdriver 
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.ui import WebDriverWait
from urllib.parse import urljoin
import sys
import argparse

blackboard_collab_link = '/webapps/blackboard/content/launchLink.jsp?course_id={}&tool_id=_1705_1&tool_type=TOOL&mode=view&mode=reset'
def parse():
    parser = argparse.ArgumentParser()
    parser.add_argument("-u", "--url", help = "School blackboard url.", required = True)
    parser.add_argument("-i", "--username", help = "Student username.", required = True)
    parser.add_argument("-s", "--password", help = "Student password.", required = True)
    parser.add_argument("-l", "--length", help = "Session length.", required = True)
    parser.add_argument("-c", "--course", help = "Course name", required = True)
    parser.add_argument("-o", "--timeout", help = "Choose maximum time to wait for an action.")
    parser.add_argument("-b", "--browser", help = "Specify browser to use. Available: firefox, google-chrome.")
    args=parser.parse_args()
    return (args.url, args.username, args.password, args.course, 
            args.browser, int(args.timeout), int(args.length))

def login(student_username, student_password):
    # wait some time for blackboard terms agreement window (in case this is the first login from profile)
    try:
        agree_button = wait.until(ec.visibility_of_element_located((By.ID, 'agree_button')))
        agree_button.click()
    except:
        pass
    # fill username, pass, and login
    username_box = driver.find_element_by_name('user_id')
    username_box.clear()
    username_box.send_keys(student_username)

    password_box = driver.find_element_by_name('password')
    password_box.clear()
    password_box.send_keys(student_password)

    login_button = driver.find_element_by_id('entry-login')
    login_button.click()
    timestamp = datetime.now()
    successful_login = False
    # wait to assert that login is successful
    while datetime.now() - timestamp < timedelta(seconds=timeout):
        if driver.title != 'Blackboard Learn':
            successful_login = True
            break
    if not successful_login:
        raise Exception('Error in login. Please check your login information.')

def getCourseId(course_name):
    try:
        course = wait.until(ec.visibility_of_element_located((By.XPATH, "//*[contains(text(), {})]".format(course_name))))
        course.click()
    except Exception as ex:
        raise Exception('Couldn\'t find course due to {}'.format(ex))

    timestamp = datetime.now()
    course_id = None
    while (datetime.now()-timestamp) < timedelta(seconds=timeout):
        url = driver.current_url
        course_id = re.search('_[0-9]+_[0-9]+', url) # get course id from url
        if course_id is not None:
            course_id = course_id.group(0)
            break
    if course_id is None:
        raise Exception('Error in opening course page')
    return course_id

def goToCollab(course_name):
    # go to course blackboard collaborate ultra
    driver.get('https://blackboard.ejust.edu.eg/ultra/course')
    course_id = getCourseId(course_name)
    course_collab = blackboard_collab_link.format(course_id)
    driver.get( urljoin(school_url, course_collab) )
    if 'Blackboard Collaborate Ultra' not in driver.title:
        raise Exception('Couldn\'t open course collab')

def enterAvailableSession():
    collab_frame = wait.until(ec.visibility_of_element_located((By.CSS_SELECTOR, '#collabUltraLtiFrame'))) # switch to collab ultra frame
    driver.switch_to.frame(collab_frame)
    sleep(timeout)
    # expand all lists
    for button in driver.find_elements_by_css_selector('.expand-children'):
        button.click()
    found = False
    # iterate over all list items to see available sessions
    for li in driver.find_elements_by_tag_name('li')[::-1]:
        if 'in progress' in li.text:
            found = True
            li.click()
            break
        raise Exception('Can\'t find session')

    sleep(timeout//4)
    # join session
    driver.find_element_by_xpath("//*[contains(text(), {})]".format("'Join'")).click()

def monitorSession(length):
    timestamp = datetime.now()
    while datetime.now() - timestamp < timedelta(seconds=timeout):
        try:
            driver.switch_to.window(driver.window_handles[1])
            break
        except:
            pass

    sleep(60*10)
    auto_close = True
    try:
        side_panel = wait.until(ec.visibility_of_element_located((By.CSS_SELECTOR, '#side-panel-open')))
        side_panel.click()
    except:
        pass

    try:
        participants_button = wait.until(ec.visibility_of_element_located((By.CSS_SELECTOR, '#panel-control-participants')))
        participants_button.click()
    except:
        auto_close = False
        print('Error in finding participants. Will close after 2 hours.')
    if auto_close:
        mx_participants = 0
        err = 0
        while err<10:
            try:
                num_participants = wait.until(ec.visibility_of_element_located((By.CSS_SELECTOR, '.participant-header')))
                num_participants = int( re.search('[0-9]+', num_participants.text).group(0) )
                mx_participants = max(mx_participants, num_participants)
                if mx_participants > 2*num_participants:
                    break
            except:
                err += 1
        return
    else:
        sleep(length*60*60)

if __name__ == '__main__':
    try:
        (school_url, student_username, student_password, course_name, browser,timeout, length) = parse() 
        course_name = "'{}'".format(course_name)

        assert browser in ['firefox', 'google-chrome']
        if browser == 'firefox':
            path_to_driver = join(sys.path[0], 'geckodriver')
            driver = webdriver.Firefox(executable_path=path_to_driver)
        else:
            path_to_driver = join(sys.path[0], 'chromedriver')
            driver = webdriver.Chrome(path_to_driver)

        wait = WebDriverWait(driver, timeout)
        driver.get(school_url)
        assert driver.title == 'Blackboard Learn'
        login(student_username, student_password)
        goToCollab(course_name)
        enterAvailableSession()
        monitorSession(length)
        driver.close()
        sys.exit(0)
    except Exception as ex:
        traceback.print_exc()
        if 'driver' in globals():
            driver.close()
        sys.exit(1)
