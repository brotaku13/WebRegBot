import requests
from bs4 import BeautifulSoup as bs
import time
from twilio.rest import Client
import login
import datetime

def log(msg):
    time = datetime.datetime.now()
    try:
        with open('logs.txt', 'a') as f:
            f.write(f'{time}: {msg}\n')
    except:
        pass

def send_message(current, total, code):

    client = Client(login.account_sid, login.auth_token)

    msg = f'Course Code: {code}, Current: {current}, Total: {total} Go to https://www.reg.uci.edu/registrar/soc/webreg.html'
    try:
        message = client.messages.create(
            to=login.my_phone, 
            from_=login.phone,
            body= msg)
    except Exception as e:
        log(f'Exception sending text message: {str(e)}')
    
    log(f'Sent to Text: {msg}')

def main():
    while(True):
        wanted = ['34210', '34211', '34212', '34213', '34214']

        cookies = {
            '_ga': 'GA1.2.104024798.1545289628',
            '_fbp': 'fb.1.1549339617326.2030097213',
            '__unam': '8440ce1-16908925b1a-1561aff5-6',
            'ucinetid_auth': 'JAigiJJMc6UxOIUOGOVKUST6HzFo7eQZL3ChER9K1a35TQP3VjFduz67okyOVNvU',
            'DCA0_reg809': '!wyKtsNhDPRfKF9zyihE1IqTBlE7xpFy5ZWIj4Se1AVecO8v4qVUcNu66pB2LYZcMpNmRiYFg0g/HlBc=',
        }

        headers = {
            'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:65.0) Gecko/20100101 Firefox/65.0',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Referer': 'https://www.reg.uci.edu/perl/WebSoc',
            'Content-Type': 'application/x-www-form-urlencoded',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        }

        data = {
            'YearTerm': '2019-14',
            'ShowComments': 'on',
            'ShowFinals': 'on',
            'Breadth': 'ANY',
            'Dept': 'COMPSCI',
            'CourseNum': '',
            'Division': 'ANY',
            'CourseCodes': '',
            'InstrName': '',
            'CourseTitle': '',
            'ClassType': 'ALL',
            'Units': '',
            'Days': '',
            'StartTime': '',
            'EndTime': '',
            'MaxCap': '',
            'FullCourses': 'ANY',
            'FontSize': '100',
            'CancelledCourses': 'Exclude',
            'Bldg': '',
            'Room': '',
            'Submit': 'Display Web Results'
        }

        try:
            response = requests.post('https://www.reg.uci.edu/perl/WebSoc', headers=headers, cookies=cookies, data=data)
            log('Response received from websoc')
        except:
            log('Response Denied from Websoc. Sleeping and retrying in 10 seconds')
            time.sleep(10)
            continue

        soup = bs(response.content, 'lxml')
        results = soup.find_all('tr', {'valign': 'top', 'bgcolor': '#fff0ff'})

        rows = soup.find_all('tr', {'valign': 'top'})

        current_course_name = ''
        current_course_number = ''
        for row in rows:
            try:
                # prints course names
                data = row.find_all('td')[0].contents
                course_no = data[0].split(' ')
                current_course_number = course_no[1] + ' ' + course_no[3]
                current_course_name = data[1].find('b').contents[0]
                # print(course, course_name)
            except:
                # if exception thrown, then not on course name
                data = row.find_all('td')
                code = data[0].contents[0]
                maxEnr = data[8].contents[0]
                curEnr = data[9].contents[0]
            
                if code in wanted:
                    if int(curEnr) < int(maxEnr):
                        log(f'Space found! {current_course_name}, {current_course_number}')
                        try:
                            send_message(curEnr, maxEnr, code)
                        except:
                            log('Exception occurred sending text message')
                            pass
                    

        log('Sleeping Until next request')
        time.sleep(10)

if __name__ == '__main__':
    main()