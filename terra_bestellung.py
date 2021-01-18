#!/usr/bin/env python
# coding: utf8

import unittest
import sys
from openpyxl import load_workbook
import pdb
import datetime
import pdftotext
from fpdf import FPDF
# import time
import os
import pdb
import pickle
from Artikel import Artikel
from mwst import Mwst
import bestellung

einheiten = ("KG", "KI", "GL", "KA", "DO", "BD", "BTL", "ST", "FL", "BE", "LT",
             "PA", "SC")
dateiname_preisliste = "Preislisten/terra-preisliste-2020-12-25.liste"



def PDFtoText(pdf_file):

    pdf = pdftotext.PDF(pdf_file)
    # How many pages?
    print(len(pdf))

    # Iterate over all the pages
    for page in pdf:
        # print(page)
        pdf_text = page.split("\n")

    return pdf_text


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


def oeffne_preisliste(dateiname_preisliste):
    f = open(dateiname_preisliste, "rb")
    return      pickle.load(f)


def parse_textdatei(input_file):
    if debug:
        print("*** parse_textdatei aufgerufen")
        input_text = []
        for line in input_file:
            input_text.append(line.split("  "))
            print(line)
        bestellungliste = []

        # Das Datum sollte in der ersten Zeile an vierter Stelle stehen
        # Übernahme von Tag, Monat und Jahr
        try:
            datum = Datum(input_text[0][0].split()[3].split(".")[0],
                          input_text[0][0].split()[3].split(".")[1],
                          input_text[0][0].split()[3].split(".")[2])

            if debug:
                print("*** Datum: " + datum.get_datum_string())

        except:
            eingabe = input("*** Datum nicht erkannt, bitte Datum eingeben im Format dd.mm.jjjj: ").split(".")
            datum = Datum(eingabe[0], eingabe[1], eingabe[2])

        for zeile in input_text:
            if zeile[0].isnumeric():
                while "" in zeile:
                    zeile.remove("")

                try:
                    anzahl = 4 # int(zeile[3].split("/")[0])
                    menge = 4.4
                    # print(zeile)
                    # print(zeile[4].split()[0].replace(",", "."))
                    einheit = zeile[3].split("/")[1]
                    preis_feld = zeile[len(zeile)-1].split()
                    if len(preis_feld) == 2:
                        preis = float(preis_feld[0].replace(",", "."))
                    elif len(preis_feld) == 3:
                        preis = 34.2 # float(preis_feld[1].replace(",", "."))
                    else:
                        print("Preis konnte nicht erkannt werden:")
                        print(preis_feld)

                except:
                    print("Zeile konnte nicht geparst werden:")
                    print(zeile)
                    print(f"Anzahl: {anzahl}", f"   Menge: {menge}", f"   Einheit: {einheit}", f"   Preis: {preis}")
                    print("-------")

                try:
                    artikel = Artikel(
                        zeile[0],   # artikelnummer
                        zeile[1],   # Artikelbezeichnung
                        anzahl,  # Anzahl der Gebinde
                        menge,    # Menge pro Gebinde
                        einheit,      # Eineit
                        preis/menge/anzahl  # Nettopreis
                    )     # print(zeile)
                    # print("Artikel angelegt")

                    bestellungliste.append(artikel)

                except:
                    print("Artikel konnte nicht angelegt werden")
                # Erzeugen des Artikel-Objekts aus einer Zeile
                #

    # Bestellungobjekt zur Rückgabe, in der Datei 2. Zeile sollte Datum stehen
    # print(input_text[4])
    bestellung = Bestellung(bestellungliste, datum)

    return bestellung


def get_inputfilename():
    # falls Programm mit Argument aufgerufen wurde, versuche diese Datei zu
    # öffnen. falls nicht möglich, öffne Dialog
    input_file_name = "Terra 51.KW"
    input_file_typ = "xlsx"
    input_file = {"name": input_file_name, "typ": input_file_typ}
    return input_file


def open_inputfile(filename):
    if isinstance(filename, dict):
        filename = filename["name"] + "." + filename["typ"]
    else:
        error = "openinputfile() muss mit einemString oder dict['name','typ']"
        + "aufgerufen werden. Datei konnte nicht geöffnet werden!"
        assert isinstance(filename, str), error

    try:
        return open(filename)
    except:
        print("Die Datei '", filename, "' konnte nicht geöffnet werden")
        sys.exit()


def select_parser(inputfile):
    name = inputfile["name"]
    typ = inputfile["typ"]

    if typ == "xlsx":
        parse_excel(name + "." + typ)

    else:
        print("Kein passender Parser für diesen Dateityp gefunden")


def parse_excel(filename):
    workbook = load_workbook(filename=filename)
    sheet = workbook.active # hat in der Regel nur ein Arbeitsblatt
    bestellungsliste = [] # leere Liste zum Befüllen und Rückgeben

    for row in range(len(sheet['A'])):  # Durchlaufen der Zeilen der Tabelle, solange in Spalte A etwas steht
        art = sheet[row+1]      # art ist ein Feld, dass die Zellen einer Zeile enthält
        zelle1 = art[0].value
        if isinstance(zelle1, int): # wenn die erste Zelle eine Bestellnummer ist
            try: # parsen der einzelnen Felder des Artikels/der Zeile
                artikelnummer = int(art[0].value)
                bezeichnung = art[2].value[0:40]
                menge_pro_gebinde = float(art[3].value.split("/")[0].replace(",", "."))
                anzahl = int(art[4].value)
                einheit = art[3].value.split("/")[1]
                grundpreis = float(art[5].value.split("/")[0].replace(",", "."))
                zelle6 = art[6].value
                if zelle6 != None:
                    gesamtpreis = float(zelle6.split()[0].replace(",", "."))
                    fehler = gesamtpreis - round(menge_pro_gebinde * anzahl * grundpreis, 2)
                    if fehler > 0.02:
                        print(f"Preise in Zeile {row} nicht richtig erkannt!:")
                        print(f"  Gesamtpreis: {gesamtpreis} = {preis}, Grundpreis: {grundpreis} * {menge_pro_gebinde} * {anzahl}")
                else:
                    print(f"In Zeile {row} kein Gesamtpreis gefunden.")
                    print(art[2].value)

                # Anlegen des Artikels
                try:
                    artikel = Artikel(
                        artikelnummer,   # artikelnummer
                        bezeichnung,   # Artikelbezeichnung
                        anzahl,  # Anzahl der Gebinde
                        menge_pro_gebinde,    # Menge pro Gebinde
                        einheit,      # Eineit
                        gesamtpreis  # Nettopreis
                    )
                    # print(f"Zelle: {art[5].value}, Grundpreis: {grundpreis}")
                    bestellungsliste.append(artikel)

                except:
                    print("Artikel konnte nicht angelegt werden")

                if einheit not in einheiten:
                    print(f"Die Einheit {einheit} ist unbekannt.")

            # Fehlermeldung, falls eine Zeile nicht geparst werden kann
            except:
                print(f"Der Artikel in Zeile {row} konnte nicht erkannt werden:")
                for bezeichnung in art:
                    print(bezeichnung.value)

    # Rückgabe der ausgefüllten Bestellungsliste
    return bestellungsliste


print(f"Die Datei {get_name_inputfile()} wird eingelesen...")

#select_parser(get_inputfilename())
# preisliste = oeffne_preisliste(dateiname_preisliste)
# print(preisliste[1])
liste = parse_excel(get_name_inputfile())
# pdb.set_trace()
bestellung = bestellung.Bestellung(liste, datetime.date(2021,1,19))
bestellung.auf_konsole_drucken()
bestellung.als_pdf_speichern()

# print("Heutiges Datudm:", datetime.date.today())


class Test(unittest.TestCase):

    def test_get_inputfile(self):
        test_var = get_inputfilename()

        # überprüft den Rückgabetyp der Funktion
        self.assertTrue(isinstance(test_var, dict),
                        msg="get_inputfile() liefert kein Tupel zurück"
                        )
        # Überprüft Konsistenz des Rückgabewertes
        self.assertTrue(isinstance(test_var["name"], str),
                        msg="input_file['name'] ist kein String"
                        )
        self.assertTrue(test_var["name"],
                        msg="input_file['name'] ist leer, sollte aber den" +
                        "Dateinamen enthalten"
                        )
        self.assertTrue(isinstance(test_var["typ"], str),
                        msg="input_file['typ'] ist kein String"
                        )
        self.assertTrue(test_var["typ"],
                        msg="input_file['typ'] ist leer, sollte aber den" +
                        "Dateitypn enthalten"
                        )

        def test_open_inputfile(self):
            pass

        def test_select_parser(self):
            pass
