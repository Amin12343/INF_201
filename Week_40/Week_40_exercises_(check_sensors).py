# Oppgave 2

import json
from pathlib import Path

import pandas as pd
import yaml

# her lager jeg en sti til YAML-filen med innstillingene
CONFIG_FILE = Path("config.yml")
# lager en sti til Excel-filen
SENSORS_FILE = Path("sensors.xlsx")
# her lager jeg en sti til CSV-filen
CALIBRATIONS_FILE = Path("calibrations.csv")


def read_config(config_path: Path) -> dict[str, str | int]:
    """Les innstillingene fra YAML-fil.

    Args:
        config_path: sti til YAML-filen 

    Returns: 
        En dictionary med innstillingene, f.eks.
        {"max_days_since_calibration": 180,
        "output_file": "calibration_alerts.json"}
    """
    # her sørger jeg for at filen åpnes og lukkes automatisk etterpå
    with open(config_path, encoding="utf-8") as f:
        # Her gjør yaml.safe_load innholdet i filen om til en
        #  vanlig python-dictionary
        config = yaml.safe_load(f)
    # returnerer dictionary-en med innstillingene
    return config


def read_sensors(sensors_path: Path) -> list[dict[str, str]]:
    """Les sensorinformasjon (lab og eier) fra en excel-fil 

    Args: 
        sensors_path: Sti til excel-filen med kolonnene 
            sensor_id, lab_room og owner 

    Returns: 
        En liste med en dictionary per sensor. 
    """
    # leser Excel-filen inn som en tabell (DataFrame) med pandas
    sensores_table = pd.read_excel(
        sensors_path)
    # her gjør jeg om hver rad i tabellen om til 
    # en dictionary og samler dem i en liste.
    # orient="records" betyr at jeg får en dictionary per rad
    sensors_rows = sensores_table.to_dict(orient="records")

    # jeg lager en tom liste som skal inneholde de ferdige ryddede radene
    sensors = []
    # går igjennom alle radene i listen en om gangen
    for row in sensors_rows:
        # her legger jeg en ny dictionary bakerst i listen
        sensors.append(
            # Henter ut sensor-ID-en. Str() gjør veriden om til tekst,
            # og strip() fjerner mellomrom mellom og bak
            {"sensor_id": str(row["sensor_id"]).strip(),
                # henter ut hvilket rom sensoren står i og rydder likt
                "lab_room": str(row["lab_room"]).strip(),
                # henter ut hvem som eier sensoren og rydder likt
                "owner": str(row["owner"]).strip(),
             }
        )
    # her får jeg den til å hente ut hele listen 
    # med sensorer når løkken er ferdig
    return sensors


def read_calibrations(calibrations_path: Path) -> dict[str, int]:
    """Les kalibreringsstatus fra en CSV-fil

    Args:
        calibrations_path: sti til CSV-filen med kolonnene 
            sensor_id og days_since_calibration. 

    Returns: 
        En dictionary som slår opp antall dager for hver sensor_id
    """

    # her leser jeg csv-filen inn som en tabell (DateFrame) ved hjelp av pandas
    calibrations_table = pd.read_csv(calibrations_path)
    # gjør hver rad i tabellen om til en dictionary og samler dem i en liste.
    calibration_rows = calibrations_table.to_dict(orient="records")

    # lager. en tom dictionary som skal fylles med sensor_id som nøkkel
    # og antall dager sin verdi
    calibrations = {}
    # her går den gjennom alle radene, en om gangen
    for row in calibration_rows:
        # henter ut sensor-ID-en og gjør den om til tekst og fjerner
        # mellomrom foran og bak
        sensor_id = str(row["sensor_id"]).strip()
        # sjekker om cellen med antall dager er tom
        if pd.isna(row["days_since_calibration"]):
            # skriver ut en advarsel i stedet for at programmet krasjer
            print(f"Advarsel: {sensor_id} mangler antall dager, hopp over ")
            continue
        # legger inn antall dager i dictionary-en med sensor_id som nøkkel. int() gjør
        # tallet om til et vanlig python-heltall, slik at det kan lagres
        # i json-filen senere
        calibrations[sensor_id] = int(row["days_since_calibration"])
    # returnerer hele dictionery-en når løkken er ferdig
    return calibrations


def join_sensor_data(
        sensors: list[dict[str, str]], calibrations: dict[str, int]
) -> list[dict[str, str | int]]:
    """Kobler hver sensor sammen med kalibreringsstatusen sin 

    Args: 
        sensors: Listen med sensorer fra Excel-filen 
        calibrations: Dictionary med antall dager per sensor_id 

    Returns: 
        En liste med en samlet dictionary per sensor som finnes i begge filene 
    """
    # lager en tom liste som skal inneholde de sammenkoblede sensorene
    joined = []
    # her går jeg gjennom hver sensor fra excel-filen, en om gangen
    for sensor in sensors:
        # får den til å hente ut id-en til sensoren
        sensor_id = sensor["sensor_id"]
        # sjekker om sensoren mangler i dictionary-en med kalibreringsdata
        if sensor_id not in calibrations:
            # Og hvis det mangler så skriver jeg ut en advarsel i stedet for at
            # programmet krasjer
            print(f"Advarsel: {sensor_id} finnes ikke i kalibreringsloggen")
            continue
        # legger en ny, samlet ditionary bakerst i listen
        joined.append(
            {
                # sensorens id
                "sensor_id": sensor_id,
                # hvilket rom sensroen står i, hentet fra excel-filen
                "lab_room": sensor["lab_room"],
                # hvem som eier sensoren, hentet fra excel-filen
                "owner": sensor["owner"],
                # her får jeg den til å slå opp antall dager for akkurat denne sensoren i
                # dictionary-en fra CSV-filen
                "days_since_calibration": calibrations[sensor_id],
            }
        )
    # returnerer listen med sensorer når løkken er ferdig
    return joined


def find_overdue_sensors(
    sensors: list[dict[str, str | int]], max_days: int
) -> list[dict[str, str | int]]:
    """Finn sensorene som ikke er kalibrert innenfor fristen 

    Args:
        sensors: liste med sammenkoblede sensorer 
        max_days: Høyeste tillatte antall dager siden kalibrering 

    Returns: 
        en liste med sensorene der days_since_calibration > max_days.
        Listen er tom hvis ingen sensorer er over fristen 
    """
    # her bruker jeg list comprehension for å lage en ny liste med bare
    # sensorene som er over grensen, og returnere den med en gang
    return [
        sensor
        for sensor in sensors
        if sensor["days_since_calibration"] > max_days
    ]


def write_json(data: list[dict[str, str | int]], output_path: Path):
    """SKriv en liste med dictionaries tuil en formatert json-fil 

    Args:
        data: Listen som skal lagres 
        output_path: Stil til Json-filen som skal lagres 
    """
    # oppretter filen i skrivemodus ig sørger for at den lukkes
    # automatisk etterpå
    with open(output_path, "w", encoding="utf-8") as f:
        # her skriver jeg listen til filen som json. indent=2 gir to mellomrom slik
        # at det blir lettere å lese filen
        json.dump(data, f, indent=2)


def main():
    """Kjører hele programmet: leser, kobler sammen, filtrerer og skriver ut"""
    # her leser jeg innstillingene fra config.yml
    config = read_config(CONFIG_FILE)
    # henter ut grensen for antall dager
    max_days = config["max_days_since_calibration"]
    # henter ut filnavnet til resultatfilen og gjør det om til en sti
    output_path = Path(config["output_file"])

    sensors = read_sensors(SENSORS_FILE)
    calibrations = read_calibrations(CALIBRATIONS_FILE)
    joined = join_sensor_data(sensors, calibrations)

    # får den til å plukke ut sensorene som er over fristen
    overdue = find_overdue_sensors(joined, max_days)
    # får den til å skrive resultatene til json-fil
    write_json(overdue, output_path)

    print(f"Sjekket {len(joined)} sensorer mot en grense på {max_days} dager.")
    print(f"{len(overdue)} sensor(er) er over fristen.")
    print(f"Resultatet er lagret i '{output_path}'.")


if __name__ == "__main__":
    main()
