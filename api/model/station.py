class Station:
    # Id = None
    # Name = None
    # NameLong = None
    # Lat = None
    # Long = None
    # Cbseg = None
    # WaterBody = None
    # Description = None
    # Datum = None
    # CityCounty = None
    # Tidal = None
    # Comments = None
    # Code = None
    # Status = None
    # CreatedBy = None
    # CreatedDate = None
    # ModifiedBy = None
    # ModifiedDate = None
    # StationSamplingMethodId = None
    # Fips = None
    # Huc12 = None
    # State = None
    # Huc6Name = None
    # AltCode = None

    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)


# gets a set of fields of a single station by a single where
def get_station_by(db, fields, by, value):
    sql = '''
            SELECT 
                {0}
            FROM 
                dbo.Stations
            WHERE
                {1} = ?;
        '''.format(', '.join(fields), by)

    db.cursor.execute(sql, value)
    q = db.cursor.fetchone()
    if q is None:
        return None

    idx = 0
    kwargs = {}
    for f in fields:
        kwargs[f] = q[idx]
        idx += 1

    return Station(**kwargs)


# get all groups paginated
def get_stations(db, col, direction, offset, limit, search):
    # base SELECT
    sql = '''
            SELECT 
                *
            FROM 
                dbo.Stations
        '''

    # WHERE clause for searching
    if search != '':
        like = '''
            WHERE
                Name Like '%{0}%'
        '''.format(search)
        sql = f'{sql} {like}'

    # ORDER BY
    sql = f'{sql} ORDER BY {col} {direction}'

    # OFFSET and LIMIT
    if offset >= 0 and limit > 0:
        sql = f'{sql} OFFSET {offset} ROWS FETCH NEXT {limit} ROWS ONLY'

    print(sql)

    db.cursor.execute(sql)
    rows = db.cursor.fetchall()
    cols = db.cursor.description

    stations = []
    for r in rows:
        kwargs = {}
        for (index, col) in enumerate(r):
            kwargs[cols[index][0]] = col

        stations.append(Station(**kwargs))

    return stations


# station count
def count(db, search):
    sql = '''
            SELECT 
                COUNT(Id)
            FROM 
                dbo.Stations
        '''

    if search != '':
        like = '''
            WHERE
                Name Like '%{0}%'
        '''.format(search)
        sql = f'{sql} {like}'

    db.cursor.execute(sql)
    q = db.cursor.fetchone()

    if q is None:
        return None

    return q[0]
