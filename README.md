# Semesteroverzichten

## Leerdoelenkaart + Portfolio overzichten van het semester
Het script overzichtgenerator/LeerdoelenkaartGenerator.py kan worden aangeroepen om van de gekoppelde semesters overzichten te genereren. Die overzichten komen als volgt terecht in een docs folder:

docs

    semesters   

        S3_2024   

            semesteroverzicht_S3_2024.html    
            Pietje_Puk   
                index.html   
                portfolio.html   
                leerdoelenkaart.html   
                bewijsmappen   
                    bewijs_leerdoel_L2.html   
                    bewijs_leerdoel_L3.html   
                    bewijs_leerdoel_L7.html   
            Jan_Klaassen   
                 index.html   
                 etc ....   

De gebruiksaanwijzing is onderaan het script zelf te vinden.   

Docenten krijgen via teams/onedrive toegang tot de S3_2024 folder, en daarmee tot    

semesteroverzicht_S3_2024.html
Studenten krijgen via teams/onedrive toegang tot hun persoonlijke folder, welke eenvoudig gebrowsed kan worden via de persoonlijke index.html.

## Nakijk overzicht
Zodra een docent tijd heeft om feedback te geven op canvas inleveringen, kan een docent met zijn canvas-api-key
met het script overzichtgenerator/GetReportLatestUploadsAndComments.py een nakijkoverzicht.html genereren.

Die bevat een lijst van links naar inleverentries op de canvas waar een student iets nieuws heeft geupload dat nog niet van 
commentaar is voorzien of waar een student een commentaar heeft toegevoegd waar een docent nog niet op heeft gereageerd.
Dankzij die tool is het niet meer nodig om handmatig de cijferlijsten op canvas door te ziften, op zoek naar studenten die nog
op een reactie wachten. Je kunt direct op de links klikken.
