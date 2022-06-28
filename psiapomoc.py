# -*- coding: utf-8 -*-
import pandas as pd
import folium
from folium import plugins
from adresy_mesto import lokaciaUlica, lokacieMesta
from numpy import mean
import numpy as np
import pickle


def nacitajPsov(mesto='presov', bezmedzier=False):
    Psi_ukec = pd.read_json('data/Psi_%s.json' % mesto, orient='records')
    Psi = Psi_ukec[['Ulica', 'Orient._č.', 'Plemeno']].rename(columns={'Orient._č.': 'Číslo'})
    Psi = Psi[(Psi['Ulica'] != '') & (Psi['Číslo'] != '')]  # niektori maju ulicu ale nie cislo
    if bezmedzier:
        Psi["Ulica"] = Psi['Ulica'].str.replace(". ", ".", regex=False)
    return Psi

Psi_dict = {mesto: nacitajPsov(mesto, True) for mesto in ['martin', 'zilina', 'presov']}


def psiNaUlici(mesto, ulica, mapa=False):
    Psi = Psi_dict[mesto]
    try:
        C, Polohy = lokaciaUlica(mesto, ulica)  # cisla, polohy
    except (ValueError, TypeError):
        return "nieulica"
    if mapa:
        Lat, Lon = zip(*Polohy)
        Lat_s, Lon_s = mean(Lat), mean(Lon)
        ul_map = folium.Map(location=(Lat_s, Lon_s), height="100%", width="100%", zoom_start=17)
    PsieDomy = Psi[Psi['Ulica'] == ulica]
    if len(PsieDomy) == 0:
        return "niepsi"
    Pv = PsieDomy['Číslo'].values
    Pv = [p.strip() for p in Pv]
    Pp = list(PsieDomy['Plemeno'].values)
    Pdata = {}
    for cislo in Pv:
        Pdata[cislo] = []
    for cislo, plem in zip(Pv,Pp):
        Pdata[cislo].append(plem)
    if mapa:
        for p, c in zip(Polohy, C):
            if c in Pdata:
                tip = ",".join(Pdata[c])
                folium.CircleMarker(location=p, radius=6, color='red', fill_color='green', fill=True,
                                    opacity=0.3, tooltip="č. %s, %s" % (c, tip)).add_to(ul_map)
        return ul_map
    return Pdata


def psiMesta(mesto, plemeno, mapa=False):
    Psi = Psi_dict[mesto]
    Udict = lokacieMesta(mesto)
    Ulice = psieUlice(mesto,Psi)
    Lat_all, Lon_all = [],[]
    Cdict = {}
    for ulica in Ulice:
        C, Lat, Lon = zip(*Udict[ulica])
        if not C:
            continue
        Lat_all.extend(Lat)
        Lon_all.extend(Lon)
        PsiUlice = Psi[Psi['Ulica'] == ulica]
        if len(PsiUlice):
            Pcisla = [p.strip() for p in PsiUlice['Číslo'].values]
            Pplem = list(PsiUlice['Plemeno'].values)
            CPlem = zip(Pcisla,Pplem)
            Pcisla = [p[0] for p in CPlem if p[1] == plemeno] # cisla pre plemeno
            if Pcisla:
                psiecisla = [p for p in Udict[ulica] if p[0] in Pcisla]
                if psiecisla:
                    Cdict[ulica] = psiecisla
    if mapa:
        ul_map = folium.Map(location=(mean(Lat_all), mean(Lon_all)), height="100%", width="100%", zoom_start=12)
    Polohy, Popy = [],[]
    for ulica in Cdict:
        for p in Cdict[ulica]:
            c, lat, lon = p
            Polohy.append([lat,lon])
            Popy.append(ulica + "," + c)
    if mapa and Polohy:
        plugins.MarkerCluster(Polohy, popups=Popy).add_to(ul_map)
    return ul_map



def psiPlemena(mesto,Psi):
    plem = sorted(list(set(Psi["Plemeno"])))
    return plem if plem[0] != "" else plem[1:]


def psieUlice(mesto,Psi):
    Ulice_loc = set(lokacieMesta(mesto).keys())
    Ulice_psi = set(Psi["Ulica"].values)
    Spolocne = Ulice_loc.intersection(Ulice_psi)
    return sorted(list(Spolocne))


def data_mesta(mesto):
    Psi = Psi_dict[mesto]
    Plemena = psiPlemena(mesto, Psi)
    Ulice = psieUlice(mesto, Psi)
    return {"psi": Psi, "plemena": Plemena, "ulice": Ulice}

# mesta = {mesto: data_mesta(mesto) for mesto in ['martin', 'zilina', 'presov']}
# len raz, potom ulozit cez:
# with open('mesta.pickle', 'wb') as mesta_file:
#     pickle.dump(mesta, mesta_file)

with open('mesta.pickle', 'rb') as mesta_file:
    mesta = pickle.load(mesta_file)