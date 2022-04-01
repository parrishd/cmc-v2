class Station:
    Id = None
    Name = None
    NameLong = None
    Lat = None
    Long = None
    Cbseg = None
    WaterBody = None
    Description = None
    Datum = None
    CityCounty = None
    Tidal = None
    Comments = None
    Code = None
    Status = None
    CreatedBy = None
    CreatedDate = None
    ModifiedBy = None
    ModifiedDate = None
    StationSamplingMethodId = None
    Fips = None
    Huc12 = None
    State = None
    Huc6Name = None
    AltCode = None

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

