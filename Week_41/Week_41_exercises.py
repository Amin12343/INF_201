# Oppgave 1

def flatten(nested: list | tuple) -> list:
    """Gjør en nøstet liste om til en flat liste 

    Funksjonen kaller seg selv hver gang den finner en liste 
    eller tuple inni listen  

    Args: 
        nested: En liste (eller tuple) som kan inneholde int, float, 
            str, bool, None, lister og tupler. 

    Returns:
        En ny flat liste med alle elementene i samme rekkefølge. 
        Hvis listen er tom, får man en tom liste tilbake  
    """
    # lager en tom liste som skal fylles med de flate elementene
    flat = []
    # Her får jeg den til å gå igjennom hvert element i listen
    for element in nested:
        # Sjekker om elemntene slev er en liste eller tuple
        if type(element) is list or type(element) is tuple:
            # hvis ja, kaller funksjonen seg selv for å gjøre denne
            # listen flat også, og + setter sammen svaret på slutten
            # av flat.
            flat = flat + flatten(element)
        # hvis nei, så er det et vanlig element
        else:
            # og da legger jeg det bak listen
            flat.append(element)
    # returnerer den ferdige flate listen
    return flat


def run_tests():
    """her sjekker jeg at flatten fir riktig svar"""
    # bruker de tre eksemplene fra oppgaveteksten
    # assert stopper programmet hvis svaret ikke er riktig
    assert flatten([1, 2, [3, 4]]) == [1, 2, 3, 4]
    expected = ["this", "is", "a", "list"]
    assert flatten(["this", ["is", ["a", "list"]]]) == expected
    assert flatten([]) == []

    # her lager jeg min egen liste med typene som ikke er med i
    # eksemplene som jeg fikk i oppgaven
    mixed = [1.5, (True, None), [[["dypt"]]], "tekst"]
    assert flatten(mixed) == [1.5, True, None, "dypt", "tekst"]

    # hvis programmet kommer hit er alle testene fullført og korrekte
    print("Alle tester for oppgave 1 er korrekte.")


if __name__ == "__main__":
    run_tests()
