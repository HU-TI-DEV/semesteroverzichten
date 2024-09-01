import os
import subprocess
import shutil
import xml.etree.ElementTree as ET
from pathlib import Path

# De klasse Tools bevat wat generieke tools
class Tools:
    # lerp weging met int als resultaat. 
    # alfa==0 resulteert in color1. alfa=1 resulteert in color2.
    @staticmethod
    def intLerp(color1,color2,alfa):
        resultColor = (int(color1[0]*(1-alfa) + color2[0]*alfa), 
                    int(color1[1]*(1-alfa) + color2[1]*alfa),
                    int(color1[2]*(1-alfa) + color2[2]*alfa))
        return resultColor
    
    # zelfde als range, maar dan voor floats
    @staticmethod
    def float_range(start, stop, step):
        while start < stop:
            yield round(start, 10)  # Rond af om nauwkeurigheidsproblemen met floats te vermijden
            start += step

    # Converteer (0xFF,0xF0,0xF0) naar de string "FFF0F0"
    @staticmethod
    def hexColorFromRGBColorTuple(colorTupleRGB):
        totaalKleurGetal = (colorTupleRGB[0]<<16)+(colorTupleRGB[1]<<8)+colorTupleRGB[2]
        strHexColor = f"{totaalKleurGetal:06x}"
        return strHexColor
    
    # Overschrijf een deel van een string op een positie met een replacement string.
    @staticmethod
    def replace_at_position(original, position, replacement):
        # Bepaal het einde van de te vervangen substring
        end_position = position + len(replacement)
        # Maak een nieuwe string door slicing en concatenatie
        new_string = original[:position] + replacement + original[position + len(replacement):]
        return new_string
    
    @staticmethod
    def read_drawio_file_into_tree(filename):
        # Parse the XML content into an ElementTree
        tree = ET.parse(filename)
        root = tree.getroot()
        return tree,root

    @staticmethod
    def save_tree_to_file(tree, filename):
        # Write the ElementTree to a file
        tree.write(filename, encoding='utf-8', xml_declaration=True)

    # Get the directory of the current script
    @staticmethod
    def get_full_path_from_script_path(local_filename):    
        script_dir = os.path.dirname(os.path.abspath(__file__))
        fullpath = os.path.join(script_dir, local_filename)
        return fullpath
    
    @staticmethod
    def read_from_file(file_path):
        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.read()
        return content
    
    @staticmethod
    def write_to_file(content, filename):
        with open(filename, 'w', encoding='utf-8') as file:
            file.write(content)
        
    @staticmethod
    def remove_directory(path):
        # Controleer of het pad bestaat
        if os.path.exists(path):
            try:
                # Verwijder de directory en alle inhoud
                shutil.rmtree(path)
                print(f"De map '{path}' is succesvol verwijderd.")
            except PermissionError as e:
                print(f"PermissionError: {e}")
            except Exception as e:
                print(f"Fout: {e}")
        else:
            print(f"De map '{path}' bestaat niet.")

    @staticmethod
    # Voordeel van remove_directory2 boven remove_directory():
    # Het legen van de directory en haar subfolders lukt wel.
    # Alleen het verwijderen van de topfolder lukt niet 
    # - bij mijn tests althans (door "access rights").
    # Nou goed, mocht de lege topfolder niet meer gebruikt worden, dan
    # kan ze altijd nog handmatig verwijderd worden.
    def remove_directory2(path):
        # Controleer of het pad bestaat
        if os.path.exists(path):
            # Loop door alle bestanden en submappen in de directory
            for root, dirs, files in os.walk(path, topdown=False):
                # Verwijder eerst alle bestanden
                for name in files:
                    file_path = os.path.join(root, name)
                    os.remove(file_path)
                # Verwijder vervolgens alle lege submappen
                for name in dirs:
                    dir_path = os.path.join(root, name)
                    os.rmdir(dir_path)
            # Verwijder uiteindelijk de hoofdmap
            try:
                os.rmdir(path)
                print(f"De map '{path}' is succesvol verwijderd.")
            except:
                print(f"[WinError 5] Access is denied: '{path}'")
        else:
            print(f"De map '{path}' bestaat niet.")

    def export_from_drawio(drawio_desktop_executable, input_path, output_path, exportFileType):
        """
        Converts a .drawio file to .html using the draw.io command line interface.

        Parameters:
        - input_path: str, path to the input .drawio file.
        - output_path: str, path to the output .html file.
        """
        exportFileType_without_dot=exportFileType.replace('.','')
        try:
            # C:\Program Files\draw.io\draw.io.exe" --export --output temp.pdf --format pdf Tjez_van_Tuijl.drawio
            # Call the draw.io CLI to convert the file
            subprocess.run([drawio_desktop_executable, '-x', '-o', output_path, '-f', exportFileType_without_dot, input_path], check=True)
            print(f"Successfully converted {input_path} to {output_path}")
        except subprocess.CalledProcessError as e:
            print(f"Error occurred while converting {input_path} to {output_path}: {e}")

    def leesTabelUitMarkdown(fileMetMarkdownTabel,lstKolomnamen):
        deelfactorTabel_fullpath = Tools.get_full_path_from_script_path(fileMetMarkdownTabel)
        strTabel = Tools.read_from_file(deelfactorTabel_fullpath)
        lines = strTabel.splitlines()
        deelfactorTabel=dict()
        bLineIsTableBody=False
        index=0
        for line in lines:
            if line.find('---')!=-1:      # this is part of the separator of the header
                bLineIsTableBody=True # from now on, the lines are in the table body
                continue
            if not bLineIsTableBody:
                continue
            splitLine=line.split('|')
            
            deelfactorTabel[index]={}
            kolomnummer=0
            for kolomnaam in lstKolomnamen:
                deelfactorTabel[index][kolomnaam]=splitLine[kolomnummer+1]
                kolomnummer+=1
            index+=1
        return deelfactorTabel

    @staticmethod
    def copy_source_to_target_with_base(source_path, target_path):
        source_path = Path(source_path).resolve()  # Zorg ervoor dat we met absolute paden werken
        target_path = Path(target_path).resolve()
        
        # Bepaal de naam van de source folder om die in de target folder op te nemen
        source_base_name = source_path.name
        target_base_path = target_path / source_base_name
        
        # Loop door alle bestanden en mappen in de bronmap
        for root, dirs, files in os.walk(source_path):
            # Bepaal het relatieve pad vanaf de bronmap
            relative_path = Path(root).relative_to(source_path)
            target_subdir = target_base_path / relative_path

            # Maak de target subdirectory aan als deze nog niet bestaat
            if not target_subdir.exists():
                target_subdir.mkdir(parents=True)

            # Verwijder alle bestanden in de target subdirectory die mogelijk al bestaan
            for file_name in files:
                target_file = target_subdir / file_name
                if target_file.exists():
                    target_file.unlink()

                # Kopieer het bestand van de bronmap naar de doellocatie
                shutil.copy2(Path(root) / file_name, target_file)
