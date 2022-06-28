import sqlite3.dbapi2 as sqlite

zname_mesta = {"presov","zilina","martin"}

def conn_open(mesto):
    if not mesto in zname_mesta:
        raise ValueError("Nemáme také mesto.")
    dbname= "data/" + mesto + '.sqlite'
    conn = sqlite.connect(dbname)
    curs = conn.cursor()
    return curs,conn

def conn_close(curs,conn):
    curs.close()
    conn.close()

def lokaciaUlica(mesto,ulica):
    curs,conn = conn_open(mesto)
    curs.execute("select c.CisloDomu, c.Latitude, c.Longitude from ulice u, popcisla c \
                  where c.IdUlice=u.IdUlice and u.MenoUlice = ?", (ulica,))
    res = curs.fetchall()
    conn_close(curs,conn)
    try:
        C,Lat,Lon = zip(*res)
        Polohy = list(zip(Lat,Lon))
        return C, Polohy
    except TypeError:
        return None

def uliceMesta(mesto):
    curs,conn = conn_open(mesto)
    curs.execute("select distinct MenoUlice from ulice")
    res = curs.fetchall()
    conn_close(curs,conn)
    return sorted([p[0] for p in res])

def lokacieMesta(mesto):
    curs,conn = conn_open(mesto)
    Ulice = uliceMesta(mesto)
    Udict = {}
    for ulica in Ulice:
        curs.execute("select c.CisloDomu, c.Latitude, c.Longitude from ulice u, popcisla c \
                      where c.IdUlice=u.IdUlice and u.MenoUlice = ?", (ulica,))
        res = curs.fetchall()
        if res:
            Udict[ulica] = res   # C, Lat, Lon
    conn_close(curs,conn)
    return Udict
