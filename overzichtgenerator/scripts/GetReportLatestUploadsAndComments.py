import csv
from Tools import Tools
import os
import requests
import json
from datetime import datetime
import pypandoc
from urllib.parse import parse_qs, urlparse

def read_api_key_from_file(filename):
    api_key_fullpath = Tools.get_full_path_from_script_path(filename)
    api_key = Tools.read_from_file(api_key_fullpath)
    return api_key

def parse_link_header(headers):
    """
    Parseert de 'Link' header om de URL voor de volgende pagina op te halen.
    Retourneert None als er geen volgende pagina is.
    """
    link_headers = headers.get('Link', '')
    links = [link.split(';') for link in link_headers.split(',')]
    next_link = [link[0].strip('<>') for link in links if 'rel="next"' in link[1]]
    return next_link[0] if next_link else None

def get_all_assignments(course_id, api_key):
    """
    Haalt alle assignments op voor een gegeven cursus.
    """
    canvas_domain = 'canvas.hu.nl'
    assignments_url = f"https://{canvas_domain}/api/v1/courses/{course_id}/assignments"
    headers = {'Authorization': f'Bearer {api_key}'}

    assignments = []
    while assignments_url:
        response = requests.get(assignments_url, headers=headers)
        if response.status_code == 200:
            assignments.extend(json.loads(response.text))
            assignments_url = parse_link_header(response.headers)
        else:
            print(f"Request failed with status {response.status_code}")
            break
    
    return assignments

def get_full_path_from_script_path(local_filename):    
    script_dir = os.path.dirname(os.path.abspath(__file__))
    fullpath = os.path.join(script_dir, local_filename)
    return fullpath

def get_clickable_url_link(text, url):
    return f'\033]8;;{url}\033\\{text}\033]8;;\033\\'

def get_url_link_for_md(text, url):
    return f'[{text}]({url})'

def get_clickable_file_link(text, path):
    url = f'file:///{path.replace("\\", "/")}'
    return f'\033]8;;{url}\033\\{text}\033]8;;\033\\'

def get_markdown_link(text, url):
    return f'[{text}]({url})'

def get_self_id():
    canvas_domain = 'canvas.hu.nl'
    self_url = f'https://{canvas_domain}/api/v1/users/self'
    headers = {'Authorization': f'Bearer {api_key}'}

    response = requests.get(self_url, headers=headers)

    if response.status_code == 200:
        user_data = response.json()
        #print(f'Your user ID is: {user_data["id"]}')
        return user_data["id"]
    else:
        print('Failed to retrieve user information:', response.status_code)
        exit()

# we converteren de .md naar .html, en gaan ervan uit dat de github-markdown.css in dezelfde directory staat.
def convert_md_to_html_and_update(md_path):
    html_path = md_path.replace(".md", ".html")
    
    title = md_path.replace('.md','')
    title = title.replace('_',' ')

    # Convert .md to .html using pypandoc
    output = pypandoc.convert_file(md_path, 'html', outputfile=html_path, extra_args=['--metadata', f'title={title}', '--css=./github-markdown.css', '--standalone'])
    
    # Read the content of the HTML file
    with open(html_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Replace <body> with <body class="markdown-body">
    updated_content = content.replace('<body>', '<body class="markdown-body">')
    
    # Write the updated content back to the HTML file
    with open(html_path, 'w', encoding='utf-8') as f:
        f.write(updated_content)

    os.remove(md_path) # comment out for debugging

    return html_path

def GetReportLatestUploadsAndComments(course_id, course_name, ignored_assignments):
    print("*********************************")
    print(course_name)
    print("*********************************")
    print("bezig.. bij een grote cursus kan het even duren.. (10 seconden per cursist oid)")

    self_id = get_self_id()

    canvas_domain = 'canvas.hu.nl'

    # The URL of the API endpoint
    assignments_url = f"https://{canvas_domain}/api/v1/courses/{course_id}/assignments"

    # The headers for the request
    headers = {
        'Authorization': f'Bearer {api_key}',
    }

    # Make the HTTP request
    #assignments_response = requests.get(assignments_url, headers=headers)
    assignments = get_all_assignments(course_id, api_key)

    # Check the status code
    if assignments is not None:

        # Get the list of student enrollments
        enrollments_url = f"https://{canvas_domain}/api/v1/courses/{course_id}/enrollments"
        params = {
            'per_page': 100,  # Get 100 enrollments per page
            'type': ['StudentEnrollment'],  # Only get student enrollments
            'state': ['active'],  # Only get active enrollments
        }
        enrollments_response = requests.get(enrollments_url, headers=headers, params=params)

        if enrollments_response.status_code == 200:
            # Parse the JSON response
            enrollments = json.loads(enrollments_response.text)

            # Initialize report list
            report = []

            for assignment in assignments:
                if(assignment['name'] not in ignored_assignments):
                    for enrollment in enrollments:
                        # Get each student's submission for the assignment
                        submission_url = f"https://{canvas_domain}/api/v1/courses/{course_id}/assignments/{assignment['id']}/submissions/{enrollment['user_id']}?include[]=submission_comments"
                        submission_response = requests.get(submission_url, headers=headers)

                        if submission_response.status_code == 200:
                            # Parse the JSON response
                            submission = json.loads(submission_response.text)

                            # Check if there are submission comments
                            comments = submission['submission_comments'] if 'submission_comments' in submission else []
                            
                            # Voorheen maakten we een clickable link naar de canvas-pagina van de inlevering, maar handiger is een link naar de bijbehorende speedgrader-pagina.
                            #clickable_link_obs = get_url_link_for_md(assignment['name'] + " - " + enrollment['user']['name'], f"https://{canvas_domain}/courses/{course_id}/assignments/{assignment['id']}/submissions/{enrollment['user_id']}")
                            clickable_link = get_url_link_for_md(assignment['name'] + " - " + enrollment['user']['name'], f"https://{canvas_domain}/courses/{course_id}/gradebook/speed_grader?assignment_id={assignment['id']}&student_id={enrollment['user_id']}")

                            # Check if there's a new upload without any comment
                            if submission['submitted_at'] is not None and (not comments or datetime.fromisoformat(comments[-1]['created_at'][:-1]) < datetime.fromisoformat(submission['submitted_at'][:-1])):
                                # If there's no comment at all or the last comment was before the latest submission
                                report_line = f"{clickable_link}, new upload"
                                #report_line = f"{assignment['name']} - {enrollment['user']['name']}, new upload"
                                # Add the student's comment if there's any
                                if comments and comments[-1]['author_id'] == enrollment['user_id']:
                                    report_line += ', "{}"'.format(comments[-1]['comment'])
                                report_line+="\n"
                                report.append(report_line)

                            #Check if the last comment is not from myself (from anothor reviewer or the student)
                            #elif comments and comments[-1]['author_id'] != self_id:
                            # No, let's check if the last comment is from the student (assuming student's comment has 'author_id' equals 'user_id')
                            elif comments and comments[-1]['author_id'] == enrollment['user_id']:
                                report_line = f"{clickable_link} - {enrollment['user']['name']}, new comment \"{comments[-1]['comment']}\""
                                #report_line = f"{assignment['name']} - {enrollment['user']['name']}, new comment \"{comments[-1]['comment']}\""
                                report_line+="\n"
                                report.append(report_line)
                        else:
                            print(f"Request failed with status {submission_response.status_code}")

            # Print report
            #for line in report:
            #    print(line)
            # nope, schrijf het naar een .md bestand in de huidige directory:
            filename = f"{course_name}_nakijkoverzicht.md"
            filename_fullpath=get_full_path_from_script_path(filename)
            with open(filename_fullpath, "w", encoding="utf-8") as file:
                file.write("# Nakijkrapport\n")
                file.write("De onderstaande canvas-inleveringen hebben feedback nodig:\n")
                file.write("- Ze zijn geupload na het laatste comment, of\n")
                file.write("- Het laatste comment is van de student zelf.\n\n")
                
                file.write("Tip: Log eerst in op canvas bij je browser die automatisch opent bij het klikken op een document-link, voordat je op een link klinkt.\n\n")
                file.write("## Entries  \n  ")
                for line in report:
                    file.write(f"{line}\n")
            
            html_path = convert_md_to_html_and_update(filename_fullpath)
            clickable_link = get_clickable_file_link(html_path, html_path)
            print(f"Report written to {clickable_link}")
        else:
            print(f"Request failed with status {enrollments_response.status_code}")

    else:
        #print(f"Request failed with status {assignments_response.status_code}")
        pass # get_all_assignments already prints the error

# Store your canvas api-key in a file in this folder called "api_key.txt". 
# Obtain it as follows:
# canvas -> account -> press the button "+nieuw toegangstoken"
api_key = read_api_key_from_file('api_key.txt')

# Output: an overview of links to initial uploads, new uploads after a comment of someone else (i.e. the teacher)
#         and comments of students after the latest comment of someone else (i.e. the teacher).

# It is also possible to specify a set of "ignored assignments", to ignore assignments that you are not interested in (because it is the responsibility of a colleague, for instance).
# For example, if ignored_assignments={'Opdracht 6 - AC / DC'} would have been passed, the comment of Isaak van Luijk above would have been ignored.

# Last note: have some patience, it may take about 10 minutes to generate the report.

import time
start_time = time.time()

ignored_assignments_s2={"sprint 1 - C++ opdrachten","sprint 2 - C++ opdrachten",
                        "sprint 3 - C++ opdrachten","sprint 4 - C++ opdrachten", 
                        "sprint 5 - C++ opdrachten","sprint 6 - C++ opdrachten", 
                        "Roll Call Attendance",
                        "Eindbeslissing",
                        "Peilmoment 1", "Peilmoment 2", "Peilmoment 3", 
                        "Link naar C++ opdrachten","Verslag Excursie",
                        "Prototyping Solderen","Back log Sprint 5",
                        "MAC adres Raspberry Pi"}

#GetReportLatestUploadsAndComments(course_id='32508',course_name="MRB",ignored_assignments={})
#GetReportLatestUploadsAndComments(course_id='32732',course_name="Vision",ignored_assignments={})
#GetReportLatestUploadsAndComments(course_id='32504',course_name="DIT",ignored_assignments={})
#GetReportLatestUploadsAndComments(course_id='39715',course_name="THGA_2023",ignored_assignments={})
#GetReportLatestUploadsAndComments(course_id='39897',course_name="S2",ignored_assignments=ignored_assignments_s2)
GetReportLatestUploadsAndComments(course_id='39897',course_name="S2",ignored_assignments=ignored_assignments_s2)

end_time = time.time()
elapsed_time = end_time - start_time
print(f"Het duurde {elapsed_time:.4f} seconden")