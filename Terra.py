#!/usr/bin/env python
# coding: utf8

import re
import sys
import pdftotext

debug = True


def PDFtoText(pdf_file):

    pdf = pdftotext.PDF(pdf_file)
    # How many pages?
    print(len(pdf))

    # Iterate over all the pages
    for page in pdf:
        # print(page)
        pdf_text = page.split("\n")

    return pdf_text


class Mwst:
    """ Enthält die beiden Mehrwertsteuersätze, ermäßigt und normal
    """
    erm = 0.05
    norm = 0.16

    def berechnen(nettopreis, mwst):
        """ Funktion der Klasse Mwst zur Berechnung der aufgerundeten
            Mehrwertsteuer.

            Argumente:
                nettopreis pro Stück oder Kilo als float
                Mehrwertsteuersatz als float z.B. 0.19 für 19%

            Rückgabe:
                den Preis inklusive Mehrwertsteuer, wobei auf 5 cent aufgerundet
                wird, allerdings nur bis 0,1 cent. Kleinere Beträge werden
                abgerundet.
                Rückgabeformat string mit Komma als Dezimaltrenner und immer
                zwei Nachkommastellen

            Beispiele:
                mwst(1.0, 0.19) returns 1,20
        """
        return round(nettopreis*(1+mwst)*20+0.49)/20


class Artikel:
    """ Enthält die aus
    dem Lieferavis ausgelesenen Angaben zu den
        Artikelpositionen und eine Funktion zur Berechnung der aufgerundeten
        Mehrwertsteuersätze
    """
    def __init__(self, bestellnummer, bezeichnung, anzahl, gebindezahl, einheit,
                 gesamtpreis):
        self.bestellnummer = bestellnummer
        self.bezeichnung = bezeichnung
        self.gebindezahl = gebindezahl
        self.anzahl = anzahl
        self.einheit = einheit
        self.gesamtpreis = gesamtpreis
        self.grundpreis = gesamtpreis/gebindezahl/anzahl
        self.mwstErm = self.__mwst(self.grundpreis, Mwst.erm)
        self.mwstNorm = self.__mwst(self.grundpreis, Mwst.norm)

    def __mwst(self, nettopreis, mwst):
        """ private Funktion der Klasse Artikel zur Berechnung der aufgerundeten
            Mehrwertsteuer.

            Argumente:
                nettopreis pro Stück oder Kilo als float
                Mehrwertsteuersatz als float z.B. 0.19 für 19%

            Rückgabe:
                den Preis inklusive Mehrwertsteuer, wobei auf 5 cent aufgerundet
                wird, allerdings nur bis 0,1 cent. Kleinere Beträge werden
                abgerundet.
                Rückgabeformat string mit Komma als Dezimaltrenner und immer
                zwei Nachkommastellen

            Beispiele:
                mwst(1,0, 0,19) = 1,20
        """
        return round(nettopreis*(1+mwst)*20+0.49)/20


class Bestellung:
    def __init__(self, liste, datum):

        self.liste = liste
        self.datum = datum
        self.kommentar = "…………………………………………………\nKommentar:\n"

    def __make_outputstring(self):

        """
        setzt den String für das Speichern in Datei self.speichern()
        oder Druckausgabe self.drucken() zusammen
        return outputstring
        """
        outputstring = 'Terrabestellung vom ' + self.datum + '\n\n'
        outputstring += '{:^25}'.format('Artikelname')
        outputstring += '{:^8}'.format('  Netto')
        outputstring += '{:^8}'.format(' MwSt ' + str(Mwst.erm*100) + '%')
        outputstring += '{:>8}'.format('  ' + str(Mwst.norm*100) + '%')
        outputstring += '\n…………………………………………………………………………………………………………………………………\n'

        käse = False

        for i in range(len(self.liste)):
            artikel = self.liste[i]

            käse = 190000 > int(artikel.bestellnummer) > 130844

            outputstring += '{:.<25.25}'.format(artikel.bezeichnung)
            outputstring += '{:>8.2f}'.format(artikel.grundpreis).replace('.', ',')

            if käse:
                outputstring += '{:>8.2f}'.format(Mwst.berechnen(artikel.grundpreis, Mwst.erm)).replace('.', ',')
                outputstring += '     /100 Gramm'
            else:
                outputstring += '{:>8.2f}'.format(Mwst.berechnen(artikel.grundpreis, Mwst.erm)).replace('.', ',')
                outputstring += '{:>8.2f}'.format(Mwst.berechnen(artikel.grundpreis, Mwst.norm)).replace('.', ',')

            outputstring += '\n'

        outputstring += self.kommentar
        return outputstring

    def drucken(self):
        print(self.__make_outputstring())

    def speichern(self):
        outputfile_name = 'Preise_Terrabestellung_' + self.datum + '.txt'
        try:
            outputfile = open(outputfile_name, "x")
            outputfile.write(self.__make_outputstring())
            print(outputfile_name + ' wird angelegt.')
            outputfile.close()
        except:
            print("Datei schon vorhanden, kein Speichern erfolgt.")
            """
            TODO:
                Abfrage, ob Datei überschrieben werden soll oder unter
                anderem Namen gespeichert
            """


def get_name_inputfile():
    try:
        return 'neu'
        if len(sys.argv) > 1:
            return sys.argv[1]
        else:
            print('Aufruf des Programms mit einer zu lesenden Textdatei, z.B.:')
            print('>>>python3 Terra.py lieferavis.txt')
            print('Programm wird beendet')
            return ""
        if debug:
            print("*** get_name_inputfile() aufgerufen")
    except:
        print('Fehler in Funktion "get_name_inputfile()"')


def parse_druckdatei(input_text):
    if debug:
        print("*** parse_druckdatei(" + inputfile.name + ") ")
    bestellungliste = []
    print(len(input_text))
    for j in range(10):
        print(input_text[j])

    # Iteration über die Zeilen des input_texts beginnend ab 8
    for i in range(7, len(input_text)):
        zeile = input_text[i].split("  ")
        # print(zeile)

        # durch split("  ") erzeugte leere Strings entfernen
        while "" in zeile:
            zeile.remove("")

        print(len(zeile))
        print(zeile)

        if len(input_text[i]) == 8:

            gebinde = input_text[i][3].split(" x ")
            # print(gebinde)
            artikel = Artikel(
                input_text[i][0],
                input_text[i][1],
                int(input_text[i][2]),
                float(gebinde[0].replace(',', '.')),
                gebinde[1],
                float(input_text[i][4].replace(',', '.'))
            )
            # print(artikel)

            bestellungliste.append(artikel)

    # Bestellungobjekt zur Rückgabe, in der Datei 2. Zeile sollte Datum stehen
    bestellung = Bestellung(bestellungliste, input_text[4])
    return bestellung


def parse_lieferavis(inputfile):
    bestellungliste = []
    bestellnummer = bezeichnung = ""
    kommentar = ""
    for i in inputfile:
        line = i

        # die Datei wird zeilenweise eingelesen in line. string1 nimmt die
        # Bestellnummer auf
        try:
            string1 = re.split("\s", line, 1)[0]   # einlesen bis zum 1. WS

            # Bestellnummer enthält mind. 6 Zahlen
            if re.findall("[0-9]{6}", string1):
                bestellnummer = string1

                # nur Zeilen mit erkannter Bestellnummer werden weiter
                # untersucht, Bezeichnung ist ab dem 4. Leerzeichen
                try:
                    string2 = re.split("\s", line, 3)[3]
                    # print('String2: ' + string2)
                    bezeichnung = string2

                except:
                    bezeichnung = "??????"
                    kommentar += "\nKeine Artikelbezeichnung erkannt in Zeile: "
                    kommentar += i

        except:
            bestellnummer = "??????"
            kommentar += "\nKeine Bestellnummer erkannt in Zeile: " + i

        if bestellnummer.strip():
            a = Artikel(bestellnummer,  # bestellnummer
                        bezeichnung,  # bezeichnung
                        4,              # gebindezahl
                        2,              # anzahl
                        "Einheit",      # einheit
                        11.2            # gesamtpreis
                        )

            bestellungliste.append(a)

    datum = 'Datum muss noch gesucht werden'
    bestellung = Bestellung(bestellungliste, datum)
    if kommentar:
        bestellung.kommentar += kommentar

    return bestellung


try:
    inputfile = open(get_name_inputfile())   # Datei öffnen
    if debug:
        print("*** Datei geöffnet")
    if not inputfile:
        sys.exit()
except:
    print("Die Datei konnte nicht geöffnet werden.")
    sys.exit()

pdftext = PDFtoText(open(r"2020_terra_bestellung_kw45.pdf", 'rb'))
# print(pdftext)
bestellung = parse_druckdatei(pdftext)
# bestellung = parse_druckdatei(inputfile)
# bestellung.drucken()

inputfile.close()

# if __name__ == "__main__":
#    main()
