class BenthicEvent:
    # Id = None
    # DateTime = None
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


def insert_benthic_event(db, event):
    sql = '''
            INSERT INTO dbo.BenthicEvents (
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

    db.cursor.execute('SELECT IDENT_CURRENT(\'dbo.BenthicEvents\')')
    return db.cursor.fetchone()[0]


def get_benthic_event_by_group_station_datetime(db, fields, gid, sid, datetime):
    sql = '''
            SELECT 
                {0}    
            FROM 
                dbo.BenthicEvents
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

    return BenthicEvent(**kwargs)


def get_benthic_event_by_eid(db, fields, by, value):
    sql = '''
              SELECT 
                  {0}
              FROM 
                  dbo.BenthicEvents
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

    return BenthicEvent(**kwargs)


def delete_benthic_event_by_id(db, id):
    sql = '''
            DELETE   
            FROM 
                dbo.BenthicEvents
            WHERE
                Id = ?
        '''

    db.cursor.execute(sql, id)
    db.cursor.commit()
    return db.cursor.rowcount
