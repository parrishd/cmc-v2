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
    cols = db.cursor.description
    if q is None:
        return None

    kwargs = {}
    for (index, col) in enumerate(q):
        kwargs[cols[index][0]] = col

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


def insert(db, group):
    sql = '''
            INSERT INTO dbo.Stations (
                {0}
            ) VALUES(
                {1}       
            )
        '''.format(','.join(group.keys()), ','.join(['?' for _ in group.values()]))

    db.cursor.execute(sql, *group.values())

    db.cursor.execute('SELECT IDENT_CURRENT(\'dbo.Stations\')')
    id = db.cursor.fetchone()[0]
    db.cursor.commit()

    return id


def update(db, gid, group):
    sql = '''
            UPDATE dbo.Stations SET
                {0} = ?
            WHERE
                Id = ?
        '''.format(' = ?, '.join(group.keys()))

    print(sql)

    db.cursor.execute(sql, *group.values(), gid)
    db.cursor.commit()

    return gid


def delete(db, gid):
    sql = '''
            DELETE FROM dbo.Stations WHERE Id = ?
        '''
    db.cursor.execute(sql, gid)
    db.cursor.commit()
    return gid
