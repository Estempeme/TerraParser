#!/usr/bin/env python
# coding: utf8

import re
import sys
import pdftotext
from fpdf import FPDF

debug = True


def schreibe_pdf(bestell_liste, datum):
    pdf = FPDF(orientation='P', unit='mm', format='A4')

    pdf.add_page()
    try:
        pdf.image('logo-fcn.jpg', x=160, y=8, w=30)
    except:
        print("Logo nicht gefunden")

    pdf.set_font("Times", size=14)
    pdf.cell(180, 20, txt="Terrabestellung vom " + datum, ln=1, align="C")
    # pdf.line(10, 10, 10, 100)
    pdf.set_line_width(.5)
    # pdf.set_draw_color(255, 0, 0)

    pdf.line(10, 37, 190, 37)
    pdf.ln(20)  # move 20 down

    pdf.set_font("Times", size=12)
    pdf.cell(45, 8, txt="Bezeichnung", align="C")
    pdf.cell(20, 8, txt="Grundpreis", align="C")
    pdf.cell(20, 8, txt=f"{Mwst.erm*100} %", align="C")
    pdf.cell(20, 8, txt=f"{Mwst.norm*100} %", ln=1, align="C")

    pdf.set_font("Times", size=10)

    for artikel in bestell_liste:
        # zeile = 0
        pdf.cell(40, 8, txt=artikel.bezeichnung, align="L")
        pdf.cell(20, 8, txt=f"{artikel.grundpreis:.2f}".replace('.',','), align="R")
        pdf.cell(20, 8, txt=f"{artikel.mwstErm:.2f}".replace('.',','),  align="R")
        pdf.cell(20, 8, txt=f"{artikel.mwstNorm:.2f}".replace('.',','), ln=1, align="R")
        # zeile += 10

    try:
        tag = datum.split(".")[0]
        monat = datum.split(".")[1]
        jahr = datum.split(".")[2]
        pdf.output(jahr + "-" + monat + "-" + tag + "-Terrabestellung.pdf")
    except:
        pdf.output("Terrabestellung.pdf")



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
        self.mwstErm = Mwst.berechnen(self.grundpreis, Mwst.erm)
        self.mwstNorm = Mwst.berechnen(self.grundpreis, Mwst.norm)

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
        # return "2020_terra_bestellung_kw45.pdf"

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

    # Iteration über die Zeilen des input_texts beginnend ab 8
    for i in range(7, len(input_text)):
        zeile = input_text[i].split("  ")

        # durch split("  ") erzeugte leere Strings entfernen
        while "" in zeile:
            zeile.remove("")

        if len(zeile) > 6:  # kurze Zeilen mit z.B. der Seitennummer ignorieren

            # Auftrennen von [1 3,5 x 1 KG] anhand des x, wobei
            # die erste Ziffer die Anzahl der Gebinde,
            # die zweite die Menge pro Gebinde und
            # die dritte die Einheit der Gebinde widergibt

            # ergibt gebinde Liste [' 1 3,5', '1 KG]
            gebinde = zeile[2].split(" x ")

            # anzahl ist erste Ziffer des ersten Strings von Gebinde nach
            # erneuter Auftrennung
            anzahl = int(gebinde[0].split()[0])

            # menge der zweite Teil des ersten Strings
            menge = float(gebinde[0].split()[1].replace(',', '.'))

            # einheit des Gebindes im zweiten Teil der Liste nach dem ersten
            # split(" x ")
            einheit = gebinde[1]

            # Erzeugen des Artikel-Objekts aus einer Zeile
            artikel = Artikel(
                zeile[0],   # Bestellnummer
                zeile[1],   # Artikelbezeichnung
                anzahl,  # Anzahl der Gebinde
                menge,    # Menge pro Gebinde
                einheit,      # Eineit
                float(zeile[3].replace(',', '.'))  # Nettopreis
            )

            bestellungliste.append(artikel)

    # Bestellungobjekt zur Rückgabe, in der Datei 2. Zeile sollte Datum stehen
    # print(input_text[4])
    bestellung = Bestellung(bestellungliste, input_text[4].split()[0])

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
    inputfile = open(get_name_inputfile(), 'rb')   # Datei öffnen
    if debug:
        print("*** Datei geöffnet")
    if not inputfile:
        sys.exit()
except:
    print("Die Datei '" + get_name_inputfile() + "' konnte nicht geöffnet werden.")
    sys.exit()

pdftext = PDFtoText(inputfile)
# print(pdftext)
bestellung = parse_druckdatei(pdftext)
# bestellung.drucken()
schreibe_pdf(bestellung.liste, bestellung.datum)

inputfile.close()


# if __name__ == "__main__":
#    main()
