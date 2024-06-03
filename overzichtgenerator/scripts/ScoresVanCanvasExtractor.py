import csv
import requests
import json
from datetime import datetime
from Tools import Tools
import time
import pandas as pd

from urllib.parse import parse_qs, urlparse

def get_list_of_all_students(canvas_domain, canvas_course_id, api_key):
    headers = {"Authorization": f"Bearer {api_key}"}
    enrollments_url = f"https://{canvas_domain}/api/v1/courses/{canvas_course_id}/enrollments"
    params = {"type[]": "StudentEnrollment", "per_page": 100}  # grotere paginagrootte om minder verzoeken te doen

    students = []

    while enrollments_url:
        response = requests.get(enrollments_url, headers=headers, params=params)
        if response.status_code == 200:
            enrollments = response.json()
            for enrollment in enrollments:
                user = enrollment['user']
                student_info = {
                    "student_number": user.get('sis_user_id'),  # Het studentnummer, als dat is ingesteld
                    "name": user.get('name')  # De naam van de student
                }
                students.append(student_info)

            # Controleer de 'Link' header voor paginatie
            if 'next' in response.links:
                enrollments_url = response.links['next']['url']
            else:
                enrollments_url = None
        else:
            print(f"Error: {response.status_code} - {response.text}")
            break

    return students

def parse_link_header(headers):
    """
    Parseert de 'Link' header om de URL voor de volgende pagina op te halen.
    Retourneert None als er geen volgende pagina is.
    """
    link_headers = headers.get('Link', '')
    links = [link.split(';') for link in link_headers.split(',')]
    next_link = [link[0].strip('<>') for link in links if 'rel="next"' in link[1]]
    return next_link[0] if next_link else None

def get_all_assignments(canvas_domain, canvas_course_id, api_key):
    """
    Haalt alle assignments op voor een gegeven cursus.
    """
    assignments_url = f"https://{canvas_domain}/api/v1/courses/{canvas_course_id}/assignments"
    headers = {'Authorization': f'Bearer {api_key}'}
    params = {"per_page": 100}

    assignments = []
    while assignments_url:
        response = requests.get(assignments_url, headers=headers, params=params)
        if response.status_code == 200:
            assignments.extend(json.loads(response.text))
            assignments_url = parse_link_header(response.headers)
        else:
            print(f"Request failed with status {response.status_code}")
            break
    
    return assignments

def get_all_enrollments(canvas_domain, canvas_course_id, api_key):
    # Functie om alle inschrijvingen op te halen met paginatie
    headers = {"Authorization": f"Bearer {api_key}"}
    enrollments_url = f"https://{canvas_domain}/api/v1/courses/{canvas_course_id}/enrollments"
    params = {
        'per_page': 100,  # grotere paginagrootte om minder verzoeken te doen
        'type': ['StudentEnrollment'],  # Alleen studentinschrijvingen
        'state': ['active'],  # Alleen actieve inschrijvingen
    }

    enrollments = []

    while enrollments_url:
        response = requests.get(enrollments_url, headers=headers, params=params)
        if response.status_code == 200:
            enrollments.extend(response.json())

            # Controleer de 'Link' header voor paginatie
            if 'next' in response.links:
                enrollments_url = response.links['next']['url']
            else:
                enrollments_url = None
        else:
            print(f"Error: {response.status_code} - {response.text}")
            break

    return enrollments

def getNonStudentComments(canvas_domain, canvas_course_id, course_name, ignored_assignments, api_key):
    headers = {"Authorization": f"Bearer {api_key}"}

    # Initialize report list
    report = []

    print("*********************************")
    print(course_name)
    print("*********************************")

    # Haal alle opdrachten op met paginatie
    assignments = get_all_assignments(canvas_domain, canvas_course_id, api_key)

    # Check if assignments are retrieved
    if assignments is not None:
        # Haal alle studentinschrijvingen op met paginatie
        enrollments = get_all_enrollments(canvas_domain, canvas_course_id, api_key)

        if enrollments is not None:
            for assignment in assignments:
                if assignment['name'] not in ignored_assignments:
                    for enrollment in enrollments:
                        # Get each student's submission for the assignment
                        submission_url = f"https://{canvas_domain}/api/v1/courses/{canvas_course_id}/assignments/{assignment['id']}/submissions/{enrollment['user_id']}?include[]=submission_comments"
                        submission_response = requests.get(submission_url, headers=headers)

                        if submission_response.status_code == 200:
                            # Parse the JSON response
                            submission = json.loads(submission_response.text)

                            # Check if there are submission comments
                            comments = submission['submission_comments'] if 'submission_comments' in submission else []

                            # Check the last comments that are not from the student (assuming student's comment has 'author_id' equals 'user_id')
                            # That is assumed to be from a teacher (so don't enable peer reviews in canvas, unless a list with author id's 
                            # of teachers will be used in the code below). Or todo: check role of author_id.
                            if comments:
                                for comment in comments:
                                    if comment['author_id'] != enrollment['user_id']:
                                        report_line = (assignment['name'], enrollment['user']['name'], enrollment['user']['sis_user_id'], comment['created_at'], submission_url, comment['comment'])
                                        report.append(report_line)
                        else:
                            print(f"Request failed with status {submission_response.status_code}")
        else:
            print(f"Failed to retrieve enrollments")
    else:
        print(f"Failed to retrieve assignments")

    return report

def splitReportLinesForLeerdoelen(report):
    # Parse de score data.
    reportLinesSplitForLeerdoelen=[]
    for line in report:
        print(line)
        comment = line[5]

        pos=0
        while True:
            strLeerdoelIndex=""
            strScore=""

            # lees regels als @23:1.0;@12:1,2 @14:0.5, @2:-0.2
            # (dus . en , zijn toegestaan voor decimaal, en spatie, ; en , en.. anything als separator)
            pos = comment.find("@",pos)
            if pos==-1:
                break
            pos+=1
            startpos=pos
            if pos>=len(comment):
                break
            curChar=comment[pos]
            while ('0'<=curChar) and (curChar<='9'):
                strLeerdoelIndex+=curChar
                pos+=1
                if pos>=len(comment):
                    break
                curChar=comment[pos]
            if pos>=len(comment):
                break

            # consume :
            if curChar==':':
                pos+=1
                if pos>=len(comment):
                    break
                curChar=comment[pos]
            if pos>=len(comment):
                break

            if ((curChar<'0')or(curChar>'9'))and(curChar!='-'):
                break

            # consume any minus sign:
            while curChar=='-':
                strScore+=curChar
                pos+=1
                if pos>=len(comment):
                    break
                curChar=comment[pos]
            if pos>=len(comment):
                break

            # comsume leading digits
            while ('0'<=curChar) and (curChar<='9'):
                strScore+=curChar
                pos+=1
                if pos>=len(comment):
                    break
                curChar=comment[pos]

            # comsume any decimal dot or comma
            if ((curChar=='.')or(curChar==',')) and pos<len(comment):
                strScore+=curChar
                pos+=1
                curChar=comment[pos]
                # consume any trailing digits
                while ('0'<=curChar) and (curChar<='9'):
                    strScore+=curChar
                    pos+=1
                    if pos<len(comment):
                        curChar=comment[pos]
            if (pos>startpos):
                leerdoelIndex=int(strLeerdoelIndex)
                score=float(strScore.replace(',','.'))
                reportLinesSplitForLeerdoelen.append((line[0],line[1],line[2],line[3],line[4],leerdoelIndex,score))
    return reportLinesSplitForLeerdoelen

def getStudentsAndScoreData(canvas_domain,canvas_course_id,api_key,course_name,ignored_assignments):
    start_time = time.time()

    students = get_list_of_all_students(canvas_domain=canvas_domain,canvas_course_id=canvas_course_id,api_key=api_key)
    for student in students:
        print(f"Studentnummer: {student['student_number']}, Naam: {student['name']}")

    report = getNonStudentComments(canvas_domain=canvas_domain,canvas_course_id=canvas_course_id,course_name=course_name,ignored_assignments=ignored_assignments,api_key=api_key)

    end_time = time.time()
    elapsed_time = end_time - start_time
    print(f"De functie duurde {elapsed_time:.4f} seconden")

    # Print report
    for line in report:
        print(line)

    reportLinesSplitForLeerdoelen = splitReportLinesForLeerdoelen(report)

    #print(reportLinesSplitForLeerdoelen)
    dataframe = pd.DataFrame (reportLinesSplitForLeerdoelen, columns=['Opdrachtnaam', 'Student', 'StudentNummer', 'Tijd', 'Inleverlink', 'LeerdoelIndex', 'Score'])
    #print(dataframe)

    sorted_dataframe = dataframe.sort_values(by=['StudentNummer','LeerdoelIndex', 'Tijd'], ascending=[True, True, True])

    partial_dataframe = dataframe[['StudentNummer', 'LeerdoelIndex', 'Score']]
    summedscores_dataframe = partial_dataframe.groupby(['StudentNummer', 'LeerdoelIndex'], as_index=False).sum()

    return students, sorted_dataframe, summedscores_dataframe


