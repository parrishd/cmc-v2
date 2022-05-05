class Event:
    # Id = None
    # DateTime = None
    # Project = None
    # Comments = None
    # StationId = None
    # GroupId = None
    # CreatedBy = None
    # CreatedDate = None
    # ModifiedBy = None
    # ModifiedDate = None

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


def insert_event(db, event):
    sql = '''
            INSERT INTO dbo.Events (
                DateTime,
                Comments,
                StationId,
                GroupId,
                CreatedBy,
                CreatedDate,
                ModifiedBy,
                ModifiedDate
            ) VALUES(
                ?,
                ?,
                ?,
                ?,
                ?,
                ?,
                ?,
                ?
            )
        '''

    db.cursor.execute(
        sql,
        event.DateTime,
        event.Comments,
        event.StationId,
        event.GroupId,
        event.CreatedBy,
        event.CreatedDate,
        event.ModifiedBy,
        event.ModifiedDate)

    db.cursor.execute('SELECT IDENT_CURRENT(\'dbo.Events\')')
    return db.cursor.fetchone()[0]


def delete_event_by_id(db, id):
    sql = '''
            DELETE 
            FROM 
                dbo.Events
            WHERE
                Id = ?
        '''

    db.cursor.execute(sql, id)
    db.cursor.commit()
    return db.cursor.rowcount
