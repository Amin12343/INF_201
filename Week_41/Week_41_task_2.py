# oppgave 2 

from pathlib import Path

#mappen der loggfilene ligger. "." betyr mappen jeg står i 
#terminalen når jeg kjører skriptet 
LOG_FOLDER = Path(".")
#navnet på filen som alle logglinjene skal skrives til 
OUTPUT_FILE = Path("combined_log.txt")

#her lager jeg BOM-ene. b forran betyr at det er 
# bytes og ikke vanlig tekst 
# BOM for UTF-8 
UTF8_BOM = b"\xef\xbb\xbf"
#BOM for UTF-16 little-endian 
UTF16_LE_BOM = b"\xff\xfe"
#BOM for UTF-16 big endian 
UTF16_BE_BOM = b"\xfe\xff"


def detect_encoding(raw_bytes: bytes) -> str:
    """Finner ut hvilken tegnkoding en fil har 

    Args: 
        raw_bytes: Hele innholdet i filen som bytes 

    Returns: 
        navnet på tegnkodingen som for eksempel "utf-8"    
    """
    #sjekker om filen startet med UTF-8 sin BOM 
    if raw_bytes.startswith(UTF8_BOM):
        #her får jeg filen lest også fjerner BOM-en automatisk 
        return "utf-8-sig"
    #sjekker om filen starter med den første UTF-16 BOM-en
    if raw_bytes.startswith(UTF16_LE_BOM):
        # utf-16 bruker BOM-en til å lese byten i riktig rekkefølge
        return "utf-16"
    #hcis filen ikke har BOM, prøver jeg å lese den som UTF-8
    try:
        # decode() gjør bytes om til tekst 
        raw_bytes.decode("utf-8")
        return "utf-8"
    # sjekker om utf-8 funker, hvis ikke får jeg en UnicodeDecodeError
    except UnicodeDecodeError:
        return "cp1252"


def read_log_lines(file_path: Path) -> list[str]:
    """Leser en loggfil og henter ut linjen som starter med "["

    Args: 
        file_path: stien til loggfilen 

    Returns:
        en liste med de riktige logglinjene. listen er tom hvis
        filen ikke har noen linjer som starter med "["
    """
    #her leser jeg hele filen som bytes slik at jeg kan 
    #se etter bom 
    raw_bytes = file_path.read_bytes()
    #finner hvilken tegnkoding filen har 
    encoding = detect_encoding(raw_bytes)
    # skriver ut filnavnet og tegnkodingen, så jeg kan se at 
    # programmet valgte riktig 
    print(f"{file_path}: leses som {encoding}")

    #her får jeg den til å gjøre bytes om til vanlig tekst 
    # med riktig tegnkoding 
    text = raw_bytes.decode(encoding)
    #split("\n") deler teksten opp i linjer, strip() fjerner usynlige 
    #tegn på slutten og behokder bare linjene som starer med "["
    return [
        line.strip()
        for line in text.split("\n")
        if line.startswith("[")
    ]

#her lager jeg en funskjon som samler linjene fra alle loggfilene 
#i en mappe til en stor liste 
def collect_log_lines(log_folder: Path) -> list[str]:
    """Samler logglinjene fra alle loggfilene i en mappe 

    Args:
        Log_folder: Mappen der filene ligger 
    
    Retuns:
        En liste med alle logglinjene fra alle filene
    """
    #lager en tom liste som skal fylles med linjer fra alle filene 
    all_lines = []
    #glob finner alle filer som heter log_"noe".txt, og sirted()
    #sørger for at de alltid leses i samme rekkefølge 
    for file_path in sorted(log_folder.glob("log_*.txt")):
        #leser linjene fra denne filen og legger dem bakersy i listen 
        all_lines = all_lines + read_log_lines(file_path)
    #returnerer listen med linjer fra alle filene 
    return all_lines


#her lager jeg en funksjon som skriver linjen til en ny fil 
def write_lines(lines: list[str], output_path: Path):
    """Skriver linjen til en tekstfil med UTF-8 og BOM

    Args: 
        lines: Linjene som skal skrives 
        outputh_path: Stien til filen som skal lages     
    """
    #åpner filen i skrivemodus ("w"). utf-8-sig legger automatisk 
    #til BOM-en først i filen
    with open(output_path, "w", encoding="utf-8-sig") as f:
        #får den til å gå gjennom linjene en om gangen 
        for line in lines: 
            f.write(line + "\n")


# her lager jeg en funskjon som kjører hele programmet 
def main():
    """Leser alle loggfilene og skriver logglinjen til en fil"""
    #her samler jeg linjene fra alle loggfilene 
    lines = collect_log_lines(LOG_FOLDER)

    #sjekker om listen er tom, så å programmet ikke lager en tom fil
    #uten å si fra 
    if len(lines) == 0:
        print("Fant ingen linjer.")

    #skriver alle linjene til den nye filen 
    write_lines(lines, OUTPUT_FILE)
    # skriver ut hvor mange linjer som ble skrevet og hvilke fil 
    print(f"Skrev {len(lines)} linjer till '{OUTPUT_FILE}'.")



if __name__ == "__main__":
    main()
