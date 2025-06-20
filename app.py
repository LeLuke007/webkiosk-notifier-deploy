from requests_html import HTMLSession
from datetime import datetime
from inscriptis import get_text
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import difflib
import os

LOGIN_URL = 'https://webkiosk.thapar.edu/CommonFiles/UserAction.jsp'
sem = '2425EVESEM'
EMAIL_ADDRESS = os.getenv('EMAIL_ADDRESS')
EMAIL_PASSWORD = os.getenv('EMAIL_PASSWORD')
TO_ADDRESS = os.getenv('TO_ADDRESS')
ROLL_NUMBER = os.getenv('ROLL_NUMBER')
PASSWORD = os.getenv('PASSWORD')

payload = {
    'UserType': 'S',
    'MemberCode': ROLL_NUMBER,
    'Password': PASSWORD, 
    'BTNSubmit': 'Submit'
}

webpages = [
    {
        'name': 'Subject Details',
        'url': 'https://webkiosk.thapar.edu/StudentFiles/Academic/Studregdetails.jsp'
    },
    {
        'name': 'Exam Marks',
        'url': 'https://webkiosk.thapar.edu/StudentFiles/Exam/StudentEventMarksView.jsp?x=&exam='+sem
    },
    {
        'name': 'Exam Grades',
        'url': 'https://webkiosk.thapar.edu/StudentFiles/Exam/StudentEventGradesView.jsp?x=&exam='+sem+'&Subject=ALL'
    },
    {
        'name': 'CGPA Report',
        'url': 'https://webkiosk.thapar.edu/StudentFiles/Exam/StudCGPAReport.jsp'
    },
    {
        'name': 'Seating Plan',
        'url': 'https://webkiosk.thapar.edu/StudentFiles/Exam/StudViewSeatPlan.jsp'
    },
    {
        'name': 'Datesheet',
        'url': 'https://webkiosk.thapar.edu/StudentFiles/Exam/StudViewDateSheet.jsp'
    },
    {
        'name': 'Electives',
        'url': 'https://webkiosk.thapar.edu/StudentFiles/Academic/PRStudentView.jsp'
    }

    # Add more entries here for other webpages
]

def fetch_content(session, url):
    session.post(LOGIN_URL, data=payload)
    response = session.get(url)
    return str(get_text(response.text))

def send_email(subject, body):
    msg = MIMEMultipart()
    msg['From'] = EMAIL_ADDRESS
    msg['To'] = TO_ADDRESS
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'plain'))

    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
        server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
        server.sendmail(EMAIL_ADDRESS, TO_ADDRESS, msg.as_string())

def main():
    session = HTMLSession()
    update = []
    mailed = []
    for page in webpages:
        name = page['name']
        url = page['url']
        content_file = f'content_{name.replace(" ", "_")}.txt'
        current_content = fetch_content(session, url)

        if os.path.exists(content_file):
            with open(content_file, 'r') as f:
                previous = f.read()
        else:
            previous = ''

        if previous != current_content:
            send_email(f'Webkiosk Updated: {name}', current_content)
            with open(content_file, 'w') as f:
                f.write(current_content)
            mailed.append(name)
        update.append(name)
    
    print('Checked at:', datetime.now())
    print('Updated:', update)
    print('Mailed:', mailed)

if __name__ == '__main__':
    main()