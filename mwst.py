#!/usr/bin/env python
# coding: utf8

import unittest
import sys
from openpyxl import load_workbook
import pdb
import datetime
import pdftotext
from fpdf import FPDF
import time
import os
import pdb
import pickle


class Mwst:
    """ Enthält die beiden Mehrwertsteuersätze, ermäßigt und normal
    """
    erm = 0.07
    norm = 0.19

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

    def aus_datei_lesen(dateiname):
        if dateiname == "":
            dateiname = "settings.set"
        try:
            fobj = open(dateiname, "r")
            # pdb.set_trace()
            for zeile in fobj:
                if "mwst.erm" in zeile:
                    Mwst.erm = float(zeile.split("=")[1].split()[0])
                    print(f"Ermäßigte Mehrwertsteuersatz ist jetzt {Mwst.erm}.")
                print(zeile)
                if "mwst.norm" in zeile:
                    Mwst.norm = float(zeile.split("=")[1].split()[0])
                    print(f"Normaler Mehrwertsteuersatz ist jetzt {Mwst.neu}.")
            fobj.close()
        except:
            print("Mwst kann nicht aus Datei gelesen werden!")

    def in_datei_schreiben(dateiname):
        if dateiname == "":
            dateiname = "settings.set"
        try:
            datei_obj = open(dateiname, "w")
            datei_obj.write(f"mwst.erm={Mwst.erm}\nmwst.norm={Mwst.norm}\n")
            datei_obj.close
        except:
            print(f"Datei {dateiname} zur Speicherung der Mehrwertsteuersätze konnte nicht geschrieben werden.")


def test():
    print(Mwst.erm)
