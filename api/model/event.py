class Event:
    Id = None
    DateTime = None
    Project = None
    Comments = None
    StationId = None
    GroupId = None
    CreatedBy = None
    CreatedDate = None
    ModifiedBy = None
    ModifiedDate = None

    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)


def get_event_by_group_station_datetime(db, fields, gid, sid, datetime):
    sql = '''
            SELECT 
                {0}    
            FROM 
                dbo.Events
            WHERE
                DateTime = ? AND
                StationId = ? AND
                GroupId = ?
        '''.format(', '.join(fields))

    db.cursor.execute(sql, datetime, sid, gid)
    q = db.cursor.fetchone()
    if q is None:
        return None

    idx = 0
    kwargs = {}
    for f in fields:
        kwargs[f] = q[idx]
        idx += 1

    return Event(**kwargs)
