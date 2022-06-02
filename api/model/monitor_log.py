class MonitorLog:
    # Id = None
    # UserId = None
    # Hours = None
    # EventId = None
    # CreatedBy = None
    # CreatedDate = None
    # ModifiedBy = None
    # ModifiedDate = None

    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)


# gets a set of fields of a single station by a single where
def get__monitor_log_by_event_id(db, eid):
    sql = '''
            SELECT 
                *
            FROM 
                dbo.MonitorLogs
            JOIN
                 dbo.AspNetUsers
            ON
                 dbo.MonitorLogs.UserId = dbo.AspNetUsers.Id
            WHERE
                EventId = ?;
        '''

    db.cursor.execute(sql, eid)
    rows = db.cursor.fetchall()
    cols = db.cursor.description
    monitors = []
    for r in rows:
        kwargs = {}
        for (index, col) in enumerate(r):
            kwargs[cols[index][0]] = col

        monitors.append(MonitorLog(**kwargs))

    return monitors


def insert_monitor_log(db, ml):
    sql = '''
            INSERT INTO dbo.MonitorLogs (
                UserId,
                Hours,
                EventId,
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
                ?
            )
        '''

    db.cursor.execute(
        sql,
        ml.UserId,
        ml.Hours,
        ml.BenthicEventId,
        ml.CreatedBy,
        ml.CreatedDate,
        ml.ModifiedBy,
        ml.ModifiedDate)

    return True
