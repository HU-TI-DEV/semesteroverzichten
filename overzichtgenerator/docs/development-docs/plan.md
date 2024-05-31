# Plan

Todo: maak demo-video ter verduidelijking

## Het plan in grote lijnen

- Docenten waarderen de portfolio item inleveringen per leerdoel.

- Een python applicatie update met die informatie (eens per dag, of op aanvraag) voor elke student de leerdoelenkaart, zodat deze reflecteert hoe de student ervoor staat.
  
  ### Bijzonderheden
  
  #### Score Tabel
  
  Alle vergaarde scores zijn door de student ook in tabelvorm te zien. Bij elk van de scores staat de link van de oorsprong. Zo kan bij twijfel altijd worden teruggekeken hoe een zeker scoretotaal voor een leerdoel tot stand komt.

## Waarderen / "raten" van inleveringen per leerdoel

Docenten "raten" ingeleverd materiaal op canvas per leerdoel:- Mogelijke scores:

- -1.0 (laagste mogelijke)
  
  - penalty : eerst liet je zien dat je het kon, maar nu laat je het versloffen.
  - Of: Je hebt echt een onacceptabel disrespect getoond naar je team.

- 0.5 :
  
  - Je hebt het onderwerp substantieel aangetikt, maar ik kan daaruit nog niet opmaken of je het in zijn geheel voldoende onder de knie hebt.

- 1.0 :
  
  - "Je lijkt uit deze inlevering het onderdeel aardig onder de knie te hebben."

- 2.0 (hoogst mogelijke):   
  
  - "Je hebt veel extra's gedaan. Je overtreft alle verwachtingen."

- .. en alle mogelijke waarden ertussen.
  
  ## Notatiewijze

- Bij een canvas-inlevering van een portfolio-item wordt bovenaan de feedback een oneliner gezet zoals deze:
  @32:1.0;@33:1.0;@71:0.5;@70:0.3

- Dat staat voor: 1.0 score toegekend aan Leerdoel32, 1.0 aan Leerdoel33, 0.5 aan leerdoel71 en 0.3 aan leerdoel 70.

## Ratings wegen met deelfactor: het nominaal aantal inleveringen voor het leerdoel

Voor sommige leerdoelen volstaat een enkele, goede inlevering (bijvoorbeeld een oefenopdracht electro). Voor andere verwacht je dat goede kwaliteit veelvuldig, keer op keer getoond wordt (zoals clean coding).
Om die reden worden de ingevoerde scores voor zo'n leerdoel door het systeem gesommeerd en gewogen door te delen door "het nominaal aantal inleveringen" voor het leerdoel:

- Bijvoorbeeld:   
  Het leerdoel L4_opamp-versterkertrappen. Dat zal naar verwachting tijdens het semester in de meeste gevallen alleen aan bod komen via het maken van de bijbehorende oefenopdracht. Het "nominaal aantal inleveringen" / de deelfactor voor dat leerdoel is dan 1. Een enkele goede inlevering volstaat dan om het betreffende leerdoel op de leerdoelenkaart groen te kleuren.

- Ander voorbeeld: het leedoel L70:clean-coding heeft als het goed is te maken met vele inleveringen. Het is van belang dat de student dat vaak en consequent laat zien met zijn portfolio items. Het "nominaal aantal inleveringen"/de deelfactor van dat leerdoel is dan 10.

- Die deelfactor is vast gespecificeerd per leerdoel terug te vinden in de tabel "leerdoelinfo.csv"
  
  ## Complete voorbeelden

- Voorbeeld 1: de student heeft de canvasopdracht "Opamps" ingeleverd.   
  
  - De opdracht dekt goed leerdoel L4: Opamp-versterkertrappen af.
  - De docent ziet dat de student de opdracht foutloos heeft gemaakt,
     maar verder geen extras.
  - Behalve zijn woordelijke feedback noteert hij op een regel van het 
    commentaar:    
    @4:1.0
  - De betekenis van 1.0 is dus: 
      "je lijkt dit onderdeel aardig onder de knie te hebben" 

- Voorbeeld 2: de student heeft een goed werkende IR-ontvanger ontvanger gemaakt. 
  
  - De STD ziet er goed uit. 
  - Er is netjes van STD naar code omgezet. 
  - Maar toch zijn er in de code verbeterpunten t.a.v. herbruikbaarheid en leesbaarheid.
  - Leerdoelen: (L32=STD, L33=STD_naar_Code, L71=IR_NEC, L70=CleanCoding)
  - De eerste regel van het commentaar wordt:  
    @32:1.0;@33:1.0;@71:1.0;@70:0.5

## Kleuring van de leerdoelenkaart

Voor de gewogen somscores geldt dat ze hetzelfde numerieke bereik hebben als de indididuele scores. Ze worden op de leerdoelenkaart als kleuren getoond:

- Rood: -1.0 (laagste mogelijke)
  - Je hebt flink wat onacceptabels goed te maken
- Wit: 0.0
  - Er is nog geen voortgang op het leerdoel.
- Geel: 0.5
  - Je hebt het onderwerp substantieel aangetikt, maar ik kan daaruit nog niet opmaken of je het in zijn geheel voldoende onder de knie hebt.
- Groen: 1.0
  - "Je lijkt het onderdeel aardig onder de knie te hebben."
- Cyaan: 2.0 (hoogst mogelijke):   
  - "Je hebt veel extra's gedaan. Je overtreft alle verwachtingen."
- .. en alle mogelijke waarden ertussen.

## Implementatie van de software

- Ophalen van can canvas:    
  per studentnummer: 
  
      lijst met tuples: (LeerdoelIndex, score, linkVanCanvasInleverEntry)

- Dan omrekenen naar totaalscores per leerdoel via de gewichten in het bestand leerdoelinfo.csv

- Voor de resulterende totaalscores per student(-nummer) een .csv tabel schrijven. Bijvoorbeeld "leerdoelenoverzicht_542342566.csv".

- Die totaalscores per leerdoel reflecteren door de bijbehorende kleuren in te vullen op de leerdoelenkaart.

- De leerdoelenkaart opslaan als .drawio

- De .drawio leerdoelenkaart converteren naar .html.
  Bijvoorbeeld "leerdoelenkaart_542342566.html
### Verbergen   
Aanpassing van het plan, zodat studenten niet elkaars leerdoelenkaart kunnen zien (tenzij ze dat willen).  

- Generereer een tabel waarin elke student email gekoppeld wordt aan een random-id. Die random-id wordt als postfix van de studentnaam gebruikt als foldernaam voor zijn leerdoelenkaarten. 
- Deel hem de link naar zijn leerdoelenkaart via canvas opdracht "Leerdoelenkaart".
- Maak een .md met deze links voor docenten.

## Uitvoeren van het leerdoelenkaart-generator script

- Tier 1: een docent voert eens per week het script uit, waarbij in een folder op git de leerdoelenkaarten en leerdoelenoverzichten worden geupdate en het resultaat gecommit (via bijvoorbeeld een batch file).
- Tier 2: een script op een server doet dat automatisch, een keer per dag 's nachts.
- Tier 3: een aangepaste versie van het script op een flask server kan worden gegenereerd voor een enkele student door het studentnummer in te typen. Daarop kan een .html of .png van de leerdoelenkaart worden gedownload.
  (kan dat efficient genoeg?)

## Uitvoerbaar maken van het leerdoelenkaart-generator script

- Ga in bash of commandline naar de betreffende folder.

- Voeg een api_key.txt document toe met daarin je persoonlijke canvas api-key.
  
  Zo kom je aan die api-key:   
  canvas -> account -> druk op de knop "+nieuw toegangstoken"

- Creëer en activeer de virtual environment folder voor python:
  
  python -m venv venv
  source venv/bin/activate  # Voor Unix/macOS
  .\venv\Scripts\activate      # Voor Windows
  pip install -r requirements.txt

- Voortaan kun je het script starten door:   
  source venv/bin/activate # Voor Unix/macOS
  .\venv\Scripts\activate # Voor Windows
  python3 LeerdoelenkaartenGenerator.py # voor Unix/macOS
  python LeerdoelenkaartenGenerator.py # voor Windows

- Voor een grote Canvas site (S2) kan het een kwartier oid in beslag nemen.

## Maken van de Leerdoelenkaart

- in drawio-desktop

- prefix de leerdoelnaam met L en leerdoelnummer.
  Bijvoorbeeld: "L5_FIR filter"

- Voeg aan elke ellips met zo'n leerdoel een lege link toe (die <u>niet</u> opent "in new window" (ALT+SHIFT+L, ENTER)) (werkt alleen een voor een)

- Met de functie testKleuring kan snel worden gecheckt of er geen link ontbreekt.
