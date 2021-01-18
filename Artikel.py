#!/usr/bin/env python
# coding: utf8
import mwst


class Artikel:
    """ Enthält die aus
    dem Lieferavis ausgelesenen Angaben zu den
        Artikelpositionen und eine Funktion zur Berechnung der aufgerundeten
        Mehrwertsteuersätze
    """
    def __init__(self, artikelnummer, bezeichnung, anzahl, menge_pro_gebinde,
                 einheit, gesamtpreis):
        self.artikelnummer = artikelnummer
        self.bezeichnung = bezeichnung
        self.menge_pro_gebinde = menge_pro_gebinde
        self.anzahl = anzahl
        self.einheit = einheit
        self.gesamtpreis = gesamtpreis
        self.grundpreis = gesamtpreis/menge_pro_gebinde/anzahl
        self.mwstErm = mwst.Mwst.berechnen(self.grundpreis, mwst.Mwst.erm)
        self.mwstNorm = mwst.Mwst.berechnen(self.grundpreis, mwst.Mwst.norm)

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
