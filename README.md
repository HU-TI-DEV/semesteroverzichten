# semesteroverzichten

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

Eigenlijk zouden de resulterende docs dus niet op deze git gepubliceerd hoeven worden (kan in .gitignore).
Het is puur even voor iemand die nieuw is, en resultaten wil kunnen bekijken: die kan de git clonen en op 
de eigen pc door de geproduceerde folders browsen.
