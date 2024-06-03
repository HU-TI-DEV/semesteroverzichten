import os
from Tools import Tools
from LeerdoelenkaartKleurder import LeerdoelenkaartKleurder
import ScoresVanCanvasExtractor
import pandas
import pickle
import random
import shutil
import pypandoc

# NB: de index in deze array correspondeert met de score van het leerdoel met die index.
# In de drawio grafiek is de eerste index 1 (L1_). De eerste score entry wordt dus niet gebruikt.
def generateTestScores(aantalTestScores):
    leerdoelenScores=dict()
    nLeerdoelIndex=0
    for score in Tools.float_range(-1.0,2.0,(2.0+1.0)/(aantalTestScores+1)):
        leerdoelenScores[nLeerdoelIndex]=score
        nLeerdoelIndex+=1
    return leerdoelenScores

# Deze functie is voor de testen van de inkleuring van de leerdoelenkaart.
# I.t.t. tot de functie hierboven, is er geen kans dat een leerdoel wit blijft,
# tenzijn is vergeten om een (lege) link aan een leerdoel-ellips toe te voegen.
def generateTestScoresMetUniformeScore(aantalTestScores,uniformeScore):
    leerdoelenScores=dict()
    nLeerdoelIndex=0
    for score in Tools.float_range(-1.0,2.0,(2.0+1.0)/(aantalTestScores+1)):
        leerdoelenScores[nLeerdoelIndex]=score
        nLeerdoelIndex+=1
    return leerdoelenScores

def read_api_key_from_file(filename):
    api_key_fullpath = Tools.get_full_path_from_script_path(filename)
    api_key = Tools.read_from_file(api_key_fullpath)
    return api_key

# Roep dezefunctie aan om te testen of aan alle ellipsen van leerdoelen
# wel (lege) links zijn toegevoegd (ALT+SHIFT+L, ENTER).
# Dat is noodzakelijk voor de structuur, en voor de inkleuring.
# Als een link ontbreekt, blijft het wit.
def testInkleuring(template_fullpath, output_fullpath, maxLeerdoel):
    leerdoelScores = generateTestScoresMetUniformeScore(maxLeerdoel,uniformeScore=0.5)
    LeerdoelenkaartKleurder.kleurLeerdoelenKaart(template_fullpath, output_fullpath, leerdoelScores, leerdoelbewijslinks={})

def getIndexFromLeerdoelnaam(leerdoelnaam):
    # Zoek de positie van 'L'
    start_pos = leerdoelnaam.find('L')

    # Controleer of 'L' is gevonden
    if start_pos != -1:
        # Zoek de positie van '_' die volgt op 'L'
        end_pos = leerdoelnaam.find('_', start_pos)
        
        # Controleer of '_' is gevonden
        if end_pos != -1:
            # Extraheer het gedeelte tussen 'L' en '_'
            decimal_part = leerdoelnaam[start_pos + 1:end_pos]
            
            # Controleer of het geëxtraheerde gedeelte een decimaal getal is
            if decimal_part.isdigit():
                pass #print(f"Het decimale getal is: {decimal_part}")
            else:
                print("Geen decimaal getal gevonden na 'L'")
        else:
            print("Geen '_' gevonden na 'L'")
    else:
        print("Geen 'L' gevonden in de tekst")

    return int(decimal_part)

def leesDeelfactorTabel(fileDeelfactorTabel_fullpath):
    strDeelfactorTabel = Tools.read_from_file(fileDeelfactorTabel_fullpath)
    lines = strDeelfactorTabel.splitlines()
    deelfactorTabel=dict()
    bLineIsTableBody=False
    for line in lines:
        if line.find('---')!=-1:      # this is part of the separator of the header
            bLineIsTableBody=True # from now on, the lines are in the table body
            continue
        if not bLineIsTableBody:
            continue
        splitLine=line.split('|')
        deelfactorTabel[getIndexFromLeerdoelnaam(splitLine[1])]={'leerdoelnaam':splitLine[1],'deelfactor':float(splitLine[2])}
    return deelfactorTabel

def generate_random_string(karakterkeuze='01',length=25):
    return ''.join(random.choice(karakterkeuze) for _ in range(length))

def generate_id():
    return generate_random_string(karakterkeuze='0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ',length=25)

# initieleLeerdoelenkaartTabel_fullpath specificeert waar leerdoelkaart-tabel-suggestie.md moet worden gegenereerd,
# het overzicht voor de docenten.
# semesteroverzichten_folder is de folder waar de leerdoelenkaarten van de studenten (.drawio en .html) worden neergezet.
def genereerInitieleLeerdoelenkaartTabel(students, kolomHeader, initieleLeerdoelenkaartTabel_fullpath,exportFileType):
    initieleLeerdoelkaartTabel=f"|{kolomHeader}|\n"
    initieleLeerdoelkaartTabel+="|---|\n"
    for student in students:
        naam = student['name']
        naam_underscored = naam.replace(" ","_")
        randompostfix=generate_id()
        link = f"[{naam}]({naam_underscored}_{randompostfix}{exportFileType})"
        initieleLeerdoelkaartTabel+= f"|{link}|\n"
    Tools.write_to_file(initieleLeerdoelkaartTabel,initieleLeerdoelenkaartTabel_fullpath)

def convertInleverlink(dataframe,rowIndex):
    inleverlink = dataframe.iloc[rowIndex]["Inleverlink"]
    # verander dit format:
    # https://canvas.hu.nl/api/v1/courses/39753/assignments/284176/submissions/220960?include[]=submission_comments
    # naar dit format:
    # https://canvas.hu.nl/courses/39753/assignments/284176/submissions/220960
    inleverlink = inleverlink.replace('api/v1','')
    inleverlink = inleverlink.replace('?include[]=submission_comments','')
    return inleverlink

def get_full_path_van_input_leerdoelenkaart_drawio(semester_config_folder):
    templateFileName = f"{semester_config_folder}/leerdoelenkaart.drawio" # De nog ongekleurde leerdoelenkaart
    template_fullpath = Tools.get_full_path_from_script_path(templateFileName)
    return template_fullpath

# Controleer of elke leerdoel-ellips wel een (lege-) link heeft... 
# door na aanroep van onderstaande functie "leerdoelenkaart-link-controle.drawio" in drawio desktop te inspecteren.
def controleerLinks(semester_config_folder):
    template_fullpath = get_full_path_van_input_leerdoelenkaart_drawio(semester_config_folder)
    output_fullpath = template_fullpath.replace("leerdoelenkaart","leerdoelenkaart-link-controle")
    testInkleuring(template_fullpath, output_fullpath,maxLeerdoel=72)

def genereer_initiele_studenten_id_suggesties_tabel(students, semester_config_folder, kolomHeadersStudentIdsTabel):
    kolomHeadersStudentIdsTabel = ["Naam","ID"]
    studenten_id_suggesties_fullpath = get_studenten_id_suggesties_fullpath(semester_config_folder)
    student_suggestie_tabel = "|"
    for header in kolomHeadersStudentIdsTabel:
        student_suggestie_tabel+=f"{header}|"
    student_suggestie_tabel+="\n|---|---|\n"
    for student in students:
        naam = student['name']
        randompostfix=generate_id()
        row = f"|{naam}|{randompostfix}|\n"
        student_suggestie_tabel += row
    Tools.write_to_file(student_suggestie_tabel,studenten_id_suggesties_fullpath)
    controleerLinks(semester_config_folder) # controleer standaard ook maar de links (of elke ellips er een heeft)

def get_studenten_id_suggesties_fullpath(semester_config_folder):
    studenten_id_suggesties_fullpath = Tools.get_full_path_from_script_path(f"{semester_config_folder}/alleen-initieel/studenten-id-tabel-suggestie.md")
    return studenten_id_suggesties_fullpath

def genereer_initiele_docent_id_suggestie(docenten_id_suggestie_file_fullpath):
    str_docenten_id_intieel = generate_id()
    Tools.write_to_file(str_docenten_id_intieel,docenten_id_suggestie_file_fullpath)

def lees_docenten_id(semester_config_folder):
    docenten_id_file_fullpath = get_docenten_id_file_fullpath(semester_config_folder)
    str_docenten_id = Tools.read_from_file(docenten_id_file_fullpath)
    return str_docenten_id

def get_docenten_id_file_fullpath(semester_config_folder):
    docenten_id_file_fullpath = Tools.get_full_path_from_script_path( f"{semester_config_folder}/docenten-id.md")
    return docenten_id_file_fullpath

def get_local_semester_folder_names(semester_naam):
    semester_folder_naam = f'semesters/{semester_naam}'
    semester_folder = f'../{semester_folder_naam}'
    semester_config_folder=f'{semester_folder}/config'
    return semester_folder_naam,semester_folder,semester_config_folder

def genereer_initiele_suggesties(strLogs, semester_naam, canvas_domain, canvas_course_id, api_key):

    # NB: Na de volgende call niet alle return values gebruikt - niet erg.
    semester_folder_naam, semester_folder, semester_config_folder = get_local_semester_folder_names(semester_naam)

    semester_config_folder_fullpath = Tools.get_full_path_from_script_path(semester_config_folder)
    config_initieel_folder = get_config_initieel_folder(semester_config_folder)
    config_initieel_folder_fullpath = Tools.get_full_path_from_script_path(config_initieel_folder)
    os.makedirs(semester_config_folder_fullpath, exist_ok=True)
    os.makedirs(config_initieel_folder_fullpath, exist_ok=True)

    docenten_id_suggestie_file_fullpath = get_docenten_id_suggestie_file_full_path(semester_config_folder)
    genereer_initiele_docent_id_suggestie(docenten_id_suggestie_file_fullpath)

    template_fullpath = get_full_path_van_input_leerdoelenkaart_drawio(semester_config_folder)
    initieleDeelfactorTabel_fullpath = get_initiele_deelfactor_tabel_full_path(semester_config_folder)

    gh_pages_startpagina_ontwerp_template_fullpath=Tools.get_full_path_from_script_path('gh-pages-startpagina_ontwerp_template.md')
    gh_pages_startpagina_source_fullpath=Tools.get_full_path_from_script_path(semester_config_folder+'/gh-pages-startpagina.md')
    if not os.path.exists(gh_pages_startpagina_source_fullpath):
        addLog(strLogs, f"\n {gh_pages_startpagina_source_fullpath} bestond niet.\n")
        shutil.copy(gh_pages_startpagina_ontwerp_template_fullpath,gh_pages_startpagina_source_fullpath)
        addLog(strLogs, f'{gh_pages_startpagina_source_fullpath} is gekopieerd vanuit {gh_pages_startpagina_ontwerp_template_fullpath}.\n')
        addLog(strLogs, "Customize {gh_pages_startpagina_source_fullpath} eventueel zelf nog naar believen.\n\n")

    if not os.path.exists(template_fullpath):
        addLog(strLogs, f"\nTemplate {template_fullpath} bestaat niet.\n")
        leerdoelenkaart_ontwerp_template_fullpath = Tools.get_full_path_from_script_path("leerdoelenkaart_ontwerp_template.drawio")
        shutil.copy(leerdoelenkaart_ontwerp_template_fullpath,template_fullpath)
        addLog(strLogs, f'Template {template_fullpath} is gekopieerd vanuit {leerdoelenkaart_ontwerp_template_fullpath}.\n')
        addLog(strLogs, "Customize {template_fullpath} zelf in drawio-desktop\n\n")

    LeerdoelenkaartKleurder.genereer_initiele_deelfactortabel(template_fullpath,initieleDeelfactorTabel_fullpath)

    students = ScoresVanCanvasExtractor.get_list_of_all_students(canvas_domain=canvas_domain,canvas_course_id=canvas_course_id,api_key=api_key)
    kolomHeadersStudentIdsTabel = getKolomHeadersStudentIdsTabel()
    genereer_initiele_studenten_id_suggesties_tabel(students, semester_config_folder, kolomHeadersStudentIdsTabel)
    addLog(strLogs, f"Initiele suggesties gegenereerd voor semester {semester_naam} in de folder {semester_config_folder}.\n")

def getKolomHeadersStudentIdsTabel():
    kolomHeadersStudentIdsTabel = ["Naam","ID"]
    return kolomHeadersStudentIdsTabel

def get_config_initieel_folder(semester_config_folder):
    return f"{semester_config_folder}/alleen-initieel"

def get_initiele_deelfactor_tabel_full_path(semester_config_folder):
    config_initieel_folder = get_config_initieel_folder(semester_config_folder)
    initieleDeelfactorTabel_fullpath = Tools.get_full_path_from_script_path( f"{config_initieel_folder}/deelfactor-tabel-suggestie.md")
    return initieleDeelfactorTabel_fullpath

def get_docenten_id_suggestie_file_full_path(semester_config_folder):
    config_initieel_folder = get_config_initieel_folder(semester_config_folder)
    docenten_id_suggestie_file_fullpath = Tools.get_full_path_from_script_path( f"{config_initieel_folder}/docenten-id-suggestie.md")
    return docenten_id_suggestie_file_fullpath

def addLog(strLogs,strLog):
    strLogs+=strLog
    print(strLog)
    return strLogs

def cleanup_pages_folders(semesteroverzichten_folder_fullpath):
    # de folders zelf verwijderen lukt niet altijd (windows rechten), maar leegmaken lukt zeker:
    Tools.remove_directory2(semesteroverzichten_folder_fullpath)
    os.makedirs(semesteroverzichten_folder_fullpath, exist_ok=True)

def get_output_folders(semester_naam):
    pages_folder='../../docs'
    alle_semesteroverzichten_folder = f'{pages_folder}/semesters'
    semester_output_folder=f'{alle_semesteroverzichten_folder}/{semester_naam}'
    semesteroverzichten_folder = f'{alle_semesteroverzichten_folder}/{semester_naam}'
    exportFileType = ".svg"

    semesteroverzichten_folder_fullpath = Tools.get_full_path_from_script_path(semesteroverzichten_folder)
    return pages_folder,semester_output_folder,exportFileType,semesteroverzichten_folder_fullpath

def get_studenten_id_tabel_fullpath(semester_config_folder):
    studenten_id_tabel_fullpath = Tools.get_full_path_from_script_path(f"{semester_config_folder}/studenten-id-tabel.md")
    return studenten_id_tabel_fullpath

def convert_md_to_html_and_update(semester_output_folder_fullpath,github_markdown_css_fullpath):
    for root, dirs, files in os.walk(semester_output_folder_fullpath):
        for file in files:
            if file.endswith(".md"):
                md_path = os.path.join(root, file)
                html_path = md_path.replace(".md", ".html")
                
                title = file.replace('.md','')
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

                shutil.copy(github_markdown_css_fullpath,os.path.join(root, 'github-markdown.css'))

                #os.remove(md_path)

# De uitleg van deze functie is onderaan dit bestand te vinden.
def genereerLeerdoelenkaarten(semester_naam, canvas_course_id, api_key, gitpageslink, DebugMode, useIDs, useGithubPages):
    strLogs=""
    canvas_domain = 'canvas.hu.nl'
    ignored_assignments={}
    course_name = semester_naam # puur voor weergave, voor de code maakt het niet uit.

    genereer_initiele_suggesties(strLogs, semester_naam, canvas_domain, canvas_course_id=canvas_course_id, api_key=api_key)

    semester_folder_naam, semester_folder, semester_config_folder = get_local_semester_folder_names(semester_naam)
    fileDeelfactorTabel_fullpath = Tools.get_full_path_from_script_path(f"{semester_config_folder}/deelfactor-tabel.md")
    
    # test of fileDeelfactorTabel_fullpath bestaat, zo niet kopieer dan de suggestie file.
    if not os.path.exists(fileDeelfactorTabel_fullpath):
        initieleDeelfactorTabel_fullpath = get_initiele_deelfactor_tabel_full_path(semester_config_folder)
        shutil.copy(initieleDeelfactorTabel_fullpath,fileDeelfactorTabel_fullpath)
        addLog(strLogs, f"\nDeelfactor-tabel bestand {fileDeelfactorTabel_fullpath} bestond niet, dus is de suggestie gekopieerd.\n")
        addLog(strLogs, "Als je de .drawio file in de config folder aanpast, dan moet je deze tabel ook aanpassen.\n")
        addLog(strLogs, "Dat kan bijvoorbeeld snel door rijen uit alleen-initieel/deelfactor-tabel-suggestie.md te kopieren en plakken.\n")

    # doe hetzelfde voor docenten-id.md
    docenten_id_file_fullpath = get_docenten_id_file_fullpath(semester_config_folder)
    if not os.path.exists(docenten_id_file_fullpath):
        docenten_id_suggestie_file_fullpath = get_docenten_id_suggestie_file_full_path(semester_config_folder)
        shutil.copy(docenten_id_suggestie_file_fullpath,docenten_id_file_fullpath)
        addLog(strLogs, f"Docenten-id bestand {docenten_id_file_fullpath} bestond niet, dus is de suggestie gekopieerd.")

    # doe hetzelfde voor studenten-id-tabel.md
    studenten_id_tabel_fullpath = get_studenten_id_tabel_fullpath(semester_config_folder)
    if not os.path.exists(studenten_id_tabel_fullpath):
        studenten_id_suggesties_fullpath = get_studenten_id_suggesties_fullpath(semester_config_folder)
        shutil.copy(studenten_id_suggesties_fullpath,studenten_id_tabel_fullpath)
        addLog(strLogs, f"Studenten-id-tabel bestand {studenten_id_tabel_fullpath} bestond niet, dus is de suggestie gekopieerd.")
    
    semester_folder_naam, semester_folder, semester_config_folder = get_local_semester_folder_names(semester_naam)

    # De folder docs is de folder die naar github pages wordt gerenderd.
    pages_folder, semester_output_folder, exportFileType, semesteroverzichten_folder_fullpath = get_output_folders(semester_naam)

    # Verwijder de oude overzichten.
    cleanup_pages_folders(semesteroverzichten_folder_fullpath)
    
    if DebugMode!="Release - field usage: No pickle buffering":
        strLog = '\n!!! LET OP !!! DEBUG BUILD: POSSIBLY NO INFORMATION FETCHED FROM CANVAS !!!!\n'
        addLog(strLogs, strLog)

    if DebugMode!="Fast output debug: Load pickle of earlier extracted Canvas data":
        students, dataframe, dataframe_summedScores = ScoresVanCanvasExtractor.getStudentsAndScoreData(canvas_domain,canvas_course_id,api_key,course_name,ignored_assignments)

    if DebugMode=="Initial Debug: Store and Load pickle":
        with open('temp.pkl', 'wb') as file:
            pickle.dump((students, dataframe, dataframe_summedScores), file)

    if DebugMode!="Release - field usage: No pickle buffering":
        try:
            with open('temp.pkl', 'rb') as file:
                students, dataframe, dataframe_summedScores = pickle.load(file)
        except:
            strLog="Fout bij inlezen pickle bestand."
            addLog(strLogs, strLog)
            strLog="Genereer nieuw met: DebugMode=\"Initial Debug: Store and Load pickle\" of schakel over naar release mode."
            addLog(strLogs, strLog)
            exit()

    print(students); print(dataframe); print(dataframe_summedScores);

    str_docenten_id = lees_docenten_id(semester_config_folder)
    
    #leerdoelenkaartTabel_fullpath = Tools.get_full_path_from_script_path(f"{semester_config_folder}/semesteroverzichten-tabel.md")
    studenten_id_tabel_fullpath = get_studenten_id_tabel_fullpath(semester_config_folder)
    kolomHeadersStudentIdsTabel = getKolomHeadersStudentIdsTabel()
    studenten_id_tabel = Tools.leesTabelUitMarkdown(studenten_id_tabel_fullpath,kolomHeadersStudentIdsTabel)
    studenten_id_from_name = {}
    for index in studenten_id_tabel:
        studenten_id_from_name[studenten_id_tabel[index]['Naam']] = studenten_id_tabel[index]['ID']

    # selecteer het "link deel", dus tussen () van de markdown links.
    dicNaamUnderscoredNaarId={} # dic van name_underscored -> link, uit leerdoelenkaartTabel
    for naam in studenten_id_from_name:
        naam_id = studenten_id_from_name[naam]
        naam_underscored=naam.replace(' ', '_')
        
        dicNaamUnderscoredNaarId[naam_underscored] = naam_id

    deelfactorTabel = leesDeelfactorTabel(fileDeelfactorTabel_fullpath)
    #print(deelfactorTabel)

    strEmptyMessage="### Nog geen rated feedback"
    lstNamenNogNietsIngeleverd=[]
    portfolioFilenaamFromStudentNaamNoSpaces={}
    portfolioTotalScoreFromStudentNaamNoSpaces={}
    leerdoelenkaartNaamFromStudentNaamNoSpaces={}
    for student in students:
        studentNummer=student['student_number']
        studentNaam=student['name']
        studentNaamNoSpaces=studentNaam.replace(' ','_')

        if not studentNaamNoSpaces in dicNaamUnderscoredNaarId:
            strLog=f"!!! {studentNaamNoSpaces} wordt geskipped, want nog niet toegevoegd aan config/semesteroverzichten-tabel.md !!!"
            addLog(strLogs, strLog)
            continue

        naam_id = dicNaamUnderscoredNaarId[studentNaamNoSpaces]
        naam_plus_naam_id = studentNaamNoSpaces
        if useIDs:
            naam_plus_naam_id+=f"_{naam_id}"

        student_full_path=semesteroverzichten_folder_fullpath+'/'+naam_plus_naam_id
        os.makedirs(student_full_path, exist_ok=True)

        leerdoelenkaart_naam=naam_plus_naam_id+"-leerdoelenkaart"
        leerdoelenkaartNaamFromStudentNaamNoSpaces[studentNaamNoSpaces]=leerdoelenkaart_naam

        drawio_output_fullpath = Tools.get_full_path_from_script_path(student_full_path+'/'+leerdoelenkaart_naam+".drawio")
        drawio_export_output_fullpath = Tools.get_full_path_from_script_path(student_full_path+'/'+leerdoelenkaart_naam+exportFileType)

        # Filter de DataFrame om alleen rijen te behouden waar 'StudentNummer' overeenkomt
        student_dataframe = dataframe[dataframe['StudentNummer'] == studentNummer]
        student_summedScoresDataFrame = dataframe_summedScores[dataframe_summedScores['StudentNummer'] == studentNummer]

        if student_dataframe.empty:
            lstNamenNogNietsIngeleverd.append(studentNaam)
            continue

        # omdat het one-and-only studentnummer van student_summedScoresDataFrame bekend is, 
        # kunnen we die kolom droppen:
        student_summedScoresDataFrame = student_summedScoresDataFrame.drop(columns=['StudentNummer'])

        # Nu omzeten naar een dict:
        leerdoelScores = dict(zip(student_summedScoresDataFrame['LeerdoelIndex'], student_summedScoresDataFrame['Score']))
        leerdoelbewijslinks=dict()

        #strPortfolio = f'# Semester {semester_naam}\n'
        #strPortfolio +="## Portfolio van "+studentNaam+'\n\n' #additional newline needed before table start.
        strPortfolio = "\n" # tabel moet starten met een newline.
        strPortfolio += "|Tijd|Score|Inlevering|\n"
        strPortfolio += "|---|---|---|\n"

        lstPortfolioItems=[]
        totalPortfolioScore = 0.0

        # Nu nog zijn bewijsmap vullen:
        student_bewijs_fullpath=student_full_path+'/'+'bewijsmappen'
        os.makedirs(student_bewijs_fullpath, exist_ok=True)
        for leerdoelIndex in leerdoelScores:
            summedScore = leerdoelScores[leerdoelIndex]
            if summedScore==0.0:
                continue

            student_leerdoel_dataframe = student_dataframe[student_dataframe['LeerdoelIndex'] == leerdoelIndex]
            number_of_rows = len(student_leerdoel_dataframe)
            if number_of_rows==0:
                continue
            
            bProblem=False
            deelfactorRow = deelfactorTabel.get(leerdoelIndex,'geen')
            if (deelfactorRow!='geen'):
                leerdoelnaam = deelfactorRow.get('leerdoelnaam','geen')
                if (leerdoelnaam=='geen'):
                    bProblem = True
            else:
                bProblem = True
            
            if bProblem:
                print (f"!!! leerdoelindex {leerdoelIndex} is niet aanwezig in de deelfactortabel, maar wel in de beoordelingen")
                print("Voeg het toe aan de deelfactor-tabel.md en de leerdoelenkaart.drawio, of verwijder het uit de beoordelingen.")
                continue
        
            #strLeerdoelBewijs = "# "+leerdoelnaam+'\n'
            #strLeerdoelBewijs += f"(Leerdoel L{leerdoelIndex})\n\n"
            strLeerdoelBewijs = "\n" # tabel moet starten met een newline.
            strLeerdoelBewijs += "|Tijd|Score|Inlevering|\n"
            strLeerdoelBewijs += "|---|---|---|\n"

            number_of_rows = len(student_leerdoel_dataframe)
            for i in range(number_of_rows):
                inleverlink = convertInleverlink(student_leerdoel_dataframe,i)

                strPrettyTime = student_leerdoel_dataframe.iloc[i]["Tijd"]
                strPrettyTime = strPrettyTime.replace('T',' ')
                strPrettyTime = strPrettyTime.replace('Z',' ')
                strLeerdoelBewijs += f'|{strPrettyTime}|{"{:.1f}".format(student_leerdoel_dataframe.iloc[i]["Score"])}|<a href="{inleverlink}">{student_leerdoel_dataframe.iloc[i]["Opdrachtnaam"]}</a>|\n'
                lstPortfolioItems.append((f'{strPrettyTime}',f'{"{:.1f}".format(student_leerdoel_dataframe.iloc[i]["Score"])}',f'<a href="{inleverlink}">{student_leerdoel_dataframe.iloc[i]["Opdrachtnaam"]}</a>'))

            deelfactor = float(deelfactorRow['deelfactor'])
            if summedScore==0.0:
                print(f"Fout in deelfactorTabel: deelfactor van leerdoel {leerdoelIndex} is 0!")
                continue
            
            weightedSummedScore = summedScore/deelfactor
            strLeerdoelBewijs += '\n'
            strLeerdoelBewijs += f'TotaalScore: {"{:.1f}".format(summedScore)}   \n'
            strLeerdoelBewijs += f"Gedeeld door deelfactor: {str(deelfactor)}   \n\n" # lege regel nodig voor pandoc om header te herkennen.
            strLeerdoelBewijs += f'## Gewogen TotaalScore: {str("{:.1f}".format(weightedSummedScore+0.01))}\n\n' #0.01 to force round up in doubt.
            
            leerdoelbewijsFilename = student_bewijs_fullpath+f"/Bewijs_Leerdoel_L{leerdoelIndex}.md"
            Tools.write_to_file(strLeerdoelBewijs,leerdoelbewijsFilename)

            # vewijder de prefix leerdoelenkaarten/, omdat de drawio daar al in komt.
            # vanuit de drawio hoeft dus alleen naar binnen de submap leerdoelenkaarten gelinkt te worden.
            leerdoelbewijsFilename=leerdoelbewijsFilename.replace(student_full_path+'/','')
            leerdoelbewijsFilename=leerdoelbewijsFilename.replace(' ','%20')
            leerdoelbewijsFilename=leerdoelbewijsFilename.replace('.md','.html') # omdat github pages html (erbij) maakt van .md.
            leerdoelbewijslinks[leerdoelIndex]=leerdoelbewijsFilename

        # compress all scores for the same portfolio item into one line.
        lstCompressedPortfolioItems=[]
        lstPortfolioItems.sort(key=lambda x: x[0])
        for portfolioItem in lstPortfolioItems:
            if len(lstCompressedPortfolioItems)==0:
                lstCompressedPortfolioItems.append(portfolioItem)
            else:
                # Als het leerdoel al aanwezig is, verhoog zijn score dan met het huidige portfolioItem.
                if lstCompressedPortfolioItems[-1][0]==portfolioItem[0] and lstCompressedPortfolioItems[-1][2]==portfolioItem[2]:
                    lstCompressedPortfolioItems[-1]=(portfolioItem[0],f"{float(lstCompressedPortfolioItems[-1][1])+float(portfolioItem[1])}",portfolioItem[2])
                    # Zoniet, voeg dan eer nieuwe regel toe voor het nieuwe portfolioItem (de eerste voor diens leerdoel)
                else:
                    lstCompressedPortfolioItems.append(portfolioItem)

        for portfolioItem in lstCompressedPortfolioItems:
            strPortfolio += f"|{portfolioItem[0]}|{portfolioItem[1]}|{portfolioItem[2]}|\n"
            totalPortfolioScore += float(portfolioItem[1])
        strPortfolio += f'\nTotaal: {"{:.1f}".format(totalPortfolioScore)}\n'

        portfolioTotalScoreFromStudentNaamNoSpaces[studentNaamNoSpaces] = float("{:.1f}".format(totalPortfolioScore)) # float, to allow numerical sorting.

        portfolio_filenaam = naam_plus_naam_id+"-portfolio"
        portfolio_output_fullpath = Tools.get_full_path_from_script_path(student_full_path+'/'+portfolio_filenaam+".md")
        Tools.write_to_file(strPortfolio,portfolio_output_fullpath)

        portfolioFilenaamFromStudentNaamNoSpaces[studentNaamNoSpaces]=portfolio_filenaam
        template_fullpath = get_full_path_van_input_leerdoelenkaart_drawio(semester_config_folder)
        gewogenLeerdoelScores = dict()
        for leerdoelIndex in leerdoelScores:
            deelfactorRow = deelfactorTabel.get(leerdoelIndex,'geen')
            if (deelfactorRow!='geen'):
                deelfactor = float(deelfactorRow['deelfactor'])
                gewogenLeerdoelScores[leerdoelIndex] = leerdoelScores[leerdoelIndex]/float(deelfactor)
            else:
                gewogenLeerdoelScores[leerdoelIndex] = 0.0

        LeerdoelenkaartKleurder.kleurLeerdoelenKaart(template_fullpath, drawio_output_fullpath, gewogenLeerdoelScores, leerdoelbewijslinks)

        # Exporteren.. kan zo'n 5 sec duren per .drawio.
        drawio_deskop_executable_fullpath="C:\\Program Files\\draw.io\\draw.io.exe"
        Tools.export_from_drawio(drawio_deskop_executable_fullpath, drawio_output_fullpath, drawio_export_output_fullpath,exportFileType)

        # eenmaal geconverteerd naar .svg is de .drawio niet meer nodig.
        os.remove(drawio_output_fullpath)

        # maak een index.md aan voor de student
        strIndex = f"\n# Overzicht van {studentNaam}\n\n"
        strIndex += f"[Portfolio]({portfolio_filenaam}.html)\n\n"
        strIndex += f"[Leerdoelenkaart]({leerdoelenkaart_naam}.svg)\n\n"
        Tools.write_to_file(strIndex,student_full_path+'/index.md')

        # nog eens voor de zekerheid:
        if DebugMode!="Release - field usage: No pickle buffering":
            print('\n!!! LET OP !!! DEBUG BUILD: POSSIBLY NO INFORMATION FETCHED FROM CANVAS !!!!\n')

    # Bereken links voor de cross-linking van de semesteroverzichten-tabel gesorteerd op naam en die gesorteerd op score.
    semesteroverzichten_tabel_naam_zonder_extensie = f"Semesteroverzicht_{semester_naam}_-_op_naam"
    if useIDs:
        semesteroverzichten_tabel_naam_zonder_extensie += f"-{str_docenten_id}"

    filenaam_semesteroverzichten_tabel_sorted_names = f"{semesteroverzichten_tabel_naam_zonder_extensie}.md"
    semesteroverzichten_tabel_sorted_names_link = f"{semesteroverzichten_tabel_naam_zonder_extensie}.html"

    semesteroverzichten_tabel_naam_sorted_scores_zonder_extensie = f"Semesteroverzicht_{semester_naam}_-_op_score"
    if useIDs:
        semesteroverzichten_tabel_naam_sorted_scores_zonder_extensie += f"-{str_docenten_id}"

    filenaam_semesteroverzichten_tabel_sorted_scores=f"{semesteroverzichten_tabel_naam_sorted_scores_zonder_extensie}.md"
    semesteroverzichten_tabel_sorted_scores_link=f"{semesteroverzichten_tabel_naam_sorted_scores_zonder_extensie}.html"

    # Maak een link naar de op naam gesorteerde variant voor docenten.
    # (die variant linkt zelf weer naar de op score gesorteerde variant)
    overzichtslink_fullpath=Tools.get_full_path_from_script_path(f"{semester_folder}/genereerde_overzichtslink.md")
    overzichtsweblink = f"{gitpageslink}/{semester_folder_naam}/{semesteroverzichten_tabel_sorted_names_link}"
    Tools.write_to_file(overzichtsweblink, overzichtslink_fullpath)
    
    print(f"\nlink naar semesteroverzichten tabel (na bouwen van github-pages): {overzichtsweblink}\n")

    # Bouw de semesteroverzichten-tabel
    # Verzamel de data eerst in een pandas dataframe:
    overzicht_dataframe = pandas.DataFrame(columns=['Naam','Score', 'Leerdoelenkaart','Portfolio'])
    for student in students:
        studentNaam=student['name']
        studentNaamNoSpaces=studentNaam.replace(' ','_')
        naam_id = dicNaamUnderscoredNaarId[studentNaamNoSpaces]
        if useIDs:
            naam_plus_naam_id = f"{studentNaamNoSpaces}_{naam_id}"
        else:
            naam_plus_naam_id = studentNaamNoSpaces

        df_row = None
        if not studentNaamNoSpaces in dicNaamUnderscoredNaarId:
            continue
        
        if studentNaamNoSpaces not in portfolioFilenaamFromStudentNaamNoSpaces:
            df_row = {'Naam': studentNaam, 'Score': 0.0, 
            'Leerdoelenkaart': "", 
            'Portfolio': ""}
        else:
            unweighted_totalScore = portfolioTotalScoreFromStudentNaamNoSpaces[studentNaamNoSpaces] 
            portfolio_filenaam = naam_plus_naam_id+"/"+portfolioFilenaamFromStudentNaamNoSpaces[studentNaamNoSpaces]+'.html'
            leerdoelenkaart_filenaam = naam_plus_naam_id+"/"+leerdoelenkaartNaamFromStudentNaamNoSpaces[studentNaamNoSpaces]+exportFileType
            df_row = {'Naam': studentNaam, 'Score': unweighted_totalScore, 
                        'Leerdoelenkaart': f"[leerdoelenkaart]({leerdoelenkaart_filenaam})", 
                        'Portfolio': f"[portfolio]({portfolio_filenaam})"}
        # Verander de laatste regels naar:
        if type(df_row) != type(None):
            overzicht_dataframe = pandas.concat([overzicht_dataframe, pandas.DataFrame([df_row])], ignore_index=True)

    semesteroverzichten_tabel_sorted_names_published_fullpath = Tools.get_full_path_from_script_path(f"{semester_output_folder}/{filenaam_semesteroverzichten_tabel_sorted_names}")
    df_sorted_name = overzicht_dataframe.sort_values(by='Naam', ascending=True)
    df_sorted_name.to_markdown(semesteroverzichten_tabel_sorted_names_published_fullpath, index=False)

    semesteroverzichten_tabel_sorted_scores_published_fullpath = Tools.get_full_path_from_script_path(f"{semester_output_folder}/{filenaam_semesteroverzichten_tabel_sorted_scores}")
    df_sorted_score = overzicht_dataframe.sort_values(by=['Score','Naam'], ascending=[False,True])
    df_sorted_score.to_markdown(semesteroverzichten_tabel_sorted_scores_published_fullpath, index=False)

    strLinkOverzichtOpNaam = f'[Sorteer op Score]({semesteroverzichten_tabel_sorted_scores_link})\n'
    strLinkOverzichtOpScore = f'[Sorteer op Naam]({semesteroverzichten_tabel_sorted_names_link})\n'

    # voeg headers en crosslinks toe aan beide files:
    # alleen header als resultaat in .md (door github pages naar html) 
    # bij resultaat in .html via pandoc niet, want pandoc voegt dan titel toe
    # (tenzij je die optie niet invult, maar dan wordt de console vervuild met warnings)
    strHeader = f"# Semesteroverzicht {semester_naam}\n" if useGithubPages else ""

    # markdown tables need a leading newline.
    strOverzichtOpNaam = strHeader + strLinkOverzichtOpNaam + '\n' + Tools.read_from_file(semesteroverzichten_tabel_sorted_names_published_fullpath).replace(':','')
    strOverzichtOpScore = strHeader + strLinkOverzichtOpScore + '\n' + Tools.read_from_file(semesteroverzichten_tabel_sorted_scores_published_fullpath).replace(':','') 

    Tools.write_to_file(strOverzichtOpNaam,semesteroverzichten_tabel_sorted_names_published_fullpath)
    Tools.write_to_file(strOverzichtOpScore,semesteroverzichten_tabel_sorted_scores_published_fullpath)

    gh_pages_startpagina_source_fullpath=Tools.get_full_path_from_script_path(semester_config_folder+'/gh-pages-startpagina.md')
    shutil.copy(gh_pages_startpagina_source_fullpath,Tools.get_full_path_from_script_path(pages_folder+'/README.md'))

    if not useGithubPages:
        # Convert all .md to .html using pypandoc
        print ("Export not for github pages, so converting all .md to .html ourselves (please wait)...")
        semester_output_folder_fullpath=Tools.get_full_path_from_script_path(semester_output_folder)
        github_markdown_css_fullpath=Tools.get_full_path_from_script_path('github-markdown.css')
        convert_md_to_html_and_update(semester_output_folder_fullpath, github_markdown_css_fullpath)

    from datetime import datetime
    current_time = datetime.now()
    print("\nJe kunt de disk cache en gpu errors van de de drawio naar svg export tool negeren.")
    print("\nCurrent Time:", current_time)
    Tools.write_to_file(str(current_time),Tools.get_full_path_from_script_path(pages_folder+'/timestamp.md'))

    Tools.write_to_file(strLogs,Tools.get_full_path_from_script_path(f"{semester_folder}/log.txt"))

# UITLEG EN VOORBEELD GEBRUIK van de functie genereerLeerdoelenkaarten:

# Onderstaande aanroep delete en hergenereert de map {Je semesterfolder}\leerdoelenkaarten en zijn submappen.
# De inputs die het daarvoor gebruikt zijn: de niet- "alleen-initiele" bestanddelen van de config map en de file "api_key.txt".
# Zet in laatstgenoemde file je API key van Canvas ()
#
# Met de parameter useIds=True, worden de links voor docenten en studenten geobfusceerd door een lange random postfix.
# Gebruik dat als je publiceert naar een publieke webserver, zoals github pages.
#
# Met de parameter useGithubPages=True, worden de textbestanden als .md gegenereerd, en wordt het converteren naar .html aan github pages overgelaten.
# Met de parameter useGithubPages=False, worden de textbestanden als .html gegenereerd, en wordt het converteren naar .html lokaal gedaan.
# De laatste optie is dus geschikt voor publicatie op een andere webserver dan github pages of naar (gesharede teams-) folders.
#
# Voorbeeld aanroep:
# api_key = read_api_key_from_file('api_key.txt')
# genereerLeerdoelenkaarten(semester_naam='S3_2024_c',canvas_course_id='39753', api_key=api_key,
#                           gitpageslink = "https://mavehu.github.io/semesteroverzichten",
#                           DebugMode=DebugMode, useIDs=False, useGithubPages=False)

# Uncomment the proper Debug Mode below:
#------------------------------------------------
# Load and store data from Canvas in pickle. After that, switch to Fast output debug mode, to reuse the stored pickle.
#DebugMode="Initial Debug: Store and Load pickle" 

# For developinging visualisation and output based on earlier extracted canvas data (to save time)
DebugMode="Fast output debug: Load pickle of earlier extracted Canvas data"

# Real usage of the software: extract latest data from Canvas.
#DebugMode="Release - field usage: No pickle buffering" 
#------------------------------------------------

api_key = read_api_key_from_file('api_key.txt')
genereerLeerdoelenkaarten(semester_naam='S3_2024_c',canvas_course_id='39753', api_key=api_key,
                          gitpageslink = "https://mavehu.github.io/semesteroverzichten",
                          DebugMode=DebugMode, useIDs=False, useGithubPages=False)

# Normaal bedrijf:
# Roep bovenstaande functie een keer aan voor elk semester.
#
# Nieuw semester toevoegen:
# 1. Na de eerste keer dat je het hebt aangeroepen voor een nieuw semester, wordt automatisch 
# in de semesters folder een subfolder aangemaakt met de naam van je semester, met daarin 
# de opzet van je semester.
# 2. Daarin kun je dan de leerdoelenkaart.drawio aanpassen. Na de aanpassing kun je de functie
# nogmaals aanroepen. Het bestand alleen-intieel/deelfactor-tabel-suggestie.md reflecteert dan
# alle leerdoelen die in de leerdoelenkaart.drawio staan. Daaruit kun je dan rijen kopieren en plakken
# in deelfactor-tabel.md (ook als je later leerdoelen toevoegt)
# 3 De keren daarna dat je de functie aanroept, worden de leerdoelenkaarten en de gekoppelde portfolio's
# en bewijzen proper gegenereerd naar de docs folder, welke dan gepubliceerd kan worden naar github pages.