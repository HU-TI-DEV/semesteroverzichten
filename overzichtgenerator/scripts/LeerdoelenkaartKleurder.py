import os
import xml.etree.ElementTree as ET
from Tools import Tools

class LeerdoelenkaartKleurder:
    

    # De functie kleurLeerdoelenKaart leest een compleet witte leerdoelenkaart in,
    # kleurt de leerdoelen-ellipsen naar de kleuren die behoren bij hun scores,
    # en schrijft de gekleurde leerdoelenkaart weer weg.
    #
    # Voorbeeld:
    # lstLeerdoelScores[5] bevat de float score van leerdoel 5.
    # De ellips van het leerdoel in de leerdoelenkaart welke begint met de 
    # prefix "L5_" krijgt een kleur die correspondeert met die score:
    # -1.0 = rood, 0.0 = wit, 0.5 = geel, 1.0 = groen, 2.0 = cyaan.
    # tussenliggende waarden resulteren in tussenliggende kleuren.
    # leerdoelScores is een dict die leerdoelindex mapt naar de bijbehorende totaalscore.
    # VB: leerdoelScores[33]=0.5
    @staticmethod
    def kleurLeerdoelenKaart(fullpath_uncolored_input_drawio, 
                             fullpath_colored_output_drawio,
                             leerdoelScores,leerdoelbewijslinks):
        # Get the directory of the current script
        #script_dir = os.path.dirname(os.path.abspath(__file__))
        #input_filename = "LeerdoelenKaart_S3.drawio"
        #input_fullpath = os.path.join(script_dir, input_filename)
        #tree, root = Tools.read_drawio_file_into_tree(input_fullpath)

        tree, root = Tools.read_drawio_file_into_tree(fullpath_uncolored_input_drawio)

        leerdoelKleuren = LeerdoelenkaartKleurder.__calcLeerdoelKleurenUitScores(leerdoelScores)
        
        # root is onderdeel van tree. indirect wordt dus ook tree aangepast.
        LeerdoelenkaartKleurder.__kleurLeerdoelen(root,leerdoelKleuren)
        LeerdoelenkaartKleurder.__updateLinks(root,leerdoelbewijslinks)

        #output_fullpath = os.path.join(script_dir, "out_"+input_filename)
        Tools.save_tree_to_file(tree,fullpath_colored_output_drawio)

     # Bereken een lijst met (leerdoelindex,score) tuples uit een lijst (leerdoelindex,score) tuples.
    @staticmethod
    def __calcLeerdoelKleurenUitScores(leerdoelScores):
        leerdoelKleuren=dict()
        
        for nLeerdoelIndex in leerdoelScores:
            rgbColorTuple = LeerdoelenkaartKleurder.__kleurUitScore(leerdoelScores[nLeerdoelIndex])
            hexColor = Tools.hexColorFromRGBColorTuple(rgbColorTuple)
            leerdoelKleuren[nLeerdoelIndex]=hexColor
        
        return leerdoelKleuren

    # (geclipt-) score bereik = -1.0 .. 2.0
    @staticmethod
    def __kleurUitScore(score):
        badColor = (0xFF,0x00,0x00)
        neutralColor = (0xFF,0xFF,0xFF)
        intermediateColor = (0xFF,0xFF,0x00)
        goodColor = (0x00,0xFF,0x00)
        topColor = (0x00,0xFF,0xFF)
        bad=-1.0
        neutral=0.0
        intermediate=0.5
        good=1.0
        top=2.0

        # clip score
        if score < bad:
            score=bad
        if score > top:
            score=top

        if score<neutral:
            resultColor=Tools.intLerp(badColor,neutralColor,(score-bad)/(neutral-bad)) #score--1.0 == score+1.0
        elif score<intermediate:
            resultColor=Tools.intLerp(neutralColor,intermediateColor,(score-neutral)/(intermediate-neutral)) 
        elif score<good:
            resultColor=Tools.intLerp(intermediateColor,goodColor,(score-intermediate)/(good-intermediate))    #score-0 == score
        elif score<top:
            resultColor=Tools.intLerp(goodColor,topColor,(score-good)/(top-good))
        else:
            resultColor=topColor
        return resultColor

    # voorbeeld lijnen die geupdate moet worden:
    # <UserObject label="&lt;font color=&quot;#999999&quot;&gt;L57_&lt;/font&gt;MongoDB" id="VXFz6mvKQ9PJlcC3uVo2-63">
    # <mxCell style="ellipse;whiteSpace=wrap;html=1;strokeWidth=1;fillColor=#FF00FF;" parent="VXFz6mvKQ9PJlcC3uVo2-1" vertex="1">
    # Aan het UserObject kan eventueel het attribuut link="..." worden toegevoegd.
    # De link wijst naar een .md file met links naar de gerelateerde bewijzen.
    # Aan het mxcell element erbinnen kan een fillcolor aan zijn stijlattribuut worden toegevoegd.

    # leerdoelenkleuren is een dict die een leerdoel index mapt naar de bijbehorende kleur
    @staticmethod
    def __kleurLeerdoelen(root,leerdoelenkleuren):
        for diagram in root.findall('.//diagram'):
            mxGraphModel = diagram.find('mxGraphModel')
            root_element = mxGraphModel.find('root')

            # update de mxcells binnen de UserObjects
            for userObject in root_element.findall('UserObject'):
                label = userObject.get('label')
                if type(label) is type(None):
                    continue
                posLeerdoel=label.find("L")
                if posLeerdoel == -1:
                    continue

                # verzamel cijfers van het leerdoelgetal
                leerdoelgetal=""
                posCijfer=posLeerdoel+1
                while(True):
                    cijfer = label[posCijfer]
                    if cijfer>='0'and cijfer <='9':
                        leerdoelgetal+=cijfer
                    else:
                        break
                    posCijfer+=1
                if leerdoelgetal == "":
                    continue
                leerdoelIndex = int(leerdoelgetal)

                mxCell = userObject.find('mxCell')
                if type(mxCell) is type(None):
                    continue
                
                if leerdoelIndex not in leerdoelenkleuren:
                    continue
                
                hexColorString=leerdoelenkleuren[leerdoelIndex]
                style = mxCell.get('style')
                if type(style) is type(None):
                    continue

                # fillColor kan zijn:
                # niet aanwezig: dan achteraan style toevoegen
                # aanwezig met kleur: fillColor=#FF00FF. Dan kleur vervangen.
                # aanwezig met none: fillColor=none. Dan none vervangen door kleur.
                posfillColor=style.find("fillColor=")
                if posfillColor == -1:
                    # niet aanwezig: achteraan style toevoegen
                    style+="fillColor=#"
                    style+=hexColorString
                elif style[posfillColor+len("fillColor=")]=="#":
                    # aanwezig met kleur: fillColor=#FF00FF. Dan kleur vervangen.
                    style=Tools.replace_at_position(style,posfillColor+len("fillColor=")+1,hexColorString)
                else:
                    # aanwezig met none: fillColor=none. Dan none vervangen door kleur.
                    posNone=posfillColor+len("fillColor=")
                    assert(style[posNone]=="n")# van none
                    # vervang none door #hexcolor 
                    style = style[:posNone] + "#" + hexColorString + style[posNone + len("none"):]
                mxCell.set('style',style)
    @staticmethod
    def __updateLinks(root,leerdoelbewijslinks):
        for diagram in root.findall('.//diagram'):
            mxGraphModel = diagram.find('mxGraphModel')
            root_element = mxGraphModel.find('root')

            # update de mxcells binnen de UserObjects
            for userObject in root_element.findall('UserObject'):
                label = userObject.get('label')
                if type(label) is type(None):
                    continue
                posLeerdoel=label.find("L")
                if posLeerdoel == -1:
                    continue

                # verzamel cijfers van het leerdoelgetal
                leerdoelgetal=""
                posCijfer=posLeerdoel+1
                while(True):
                    cijfer = label[posCijfer]
                    if cijfer>='0'and cijfer <='9':
                        leerdoelgetal+=cijfer
                    else:
                        break
                    posCijfer+=1
                if leerdoelgetal == "":
                    continue
                leerdoelIndex = int(leerdoelgetal)
                if leerdoelIndex in leerdoelbewijslinks:
                    userObject.set('link',leerdoelbewijslinks[leerdoelIndex])

    @staticmethod
    def genereer_initiele_deelfactortabel(input_drawio_fullpath,initieleDeelfactorTabel_fullpath):
        tree, root = Tools.read_drawio_file_into_tree(input_drawio_fullpath)
        setDeelfactorTabelEntries=set()
        for diagram in root.findall('.//diagram'):
            mxGraphModel = diagram.find('mxGraphModel')
            root_element = mxGraphModel.find('root')
            # parse de userObjects
            for userObject in root_element.findall('UserObject'):
                label = userObject.get('label')
                if type(label) is type(None):
                    continue
                posLeerdoel=label.find("L")
                if posLeerdoel == -1:
                    continue
                # verzamel cijfers van het leerdoelgetal
                leerdoelgetal=""
                posCijfer=posLeerdoel+1
                while(True):
                    cijfer = label[posCijfer]
                    if cijfer>='0'and cijfer <='9':
                        leerdoelgetal+=cijfer
                    else:
                        break
                    posCijfer+=1
                if leerdoelgetal == "":
                    continue
                leerdoelIndex = int(leerdoelgetal)
                defaultDeelfactor = 1
                setDeelfactorTabelEntries.add((leerdoelIndex,defaultDeelfactor,label))

        lstDeelfactorTabelEntries=list(setDeelfactorTabelEntries)
        lstDeelfactorTabelEntries.sort()
        # save to file as .md table
        initieleDeelfactorTabel="|Leerdoelnaam|Deelfactor|\n"
        initieleDeelfactorTabel+="|---|---|\n"
        for deelfactorTabelEntry in lstDeelfactorTabelEntries:
            initieleDeelfactorTabel+=f"|{deelfactorTabelEntry[2]}|{deelfactorTabelEntry[1]}|\n" #leerdoelnaam, deelfactor
        Tools.write_to_file(initieleDeelfactorTabel,initieleDeelfactorTabel_fullpath)

