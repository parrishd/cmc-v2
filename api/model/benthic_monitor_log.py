class BenthicMonitorLog:
    # Id = None
    # UserId = None
    # Hours = None
    # BenthicEventId = None
    # CreatedBy = None
    # CreatedDate = None
    # ModifiedBy = None
    # ModifiedDate = None

    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)


def insert_benthic_monitor_log(db, ml):
    sql = '''
            INSERT INTO dbo.BenthicMonitorLogs (
                UserId,
                Hours,
                BenthicEventId,
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


# gets a set of fields of a single station by a single where
def get_benthic_monitor_log(db, eid):
    sql = '''
            SELECT 
                *
            FROM 
                dbo.BenthicMonitorLogs
            JOIN 
                dbo.AspNetUsers   
            ON
                dbo.BenthicMonitorLogs.UserId = dbo.AspNetUsers.Id
            WHERE
                BenthicEventId = ?;
        '''

    db.cursor.execute(sql, eid)
    rows = db.cursor.fetchall()
    cols = db.cursor.description
    monitors = []
    for r in rows:
        # print('row tho: ', {r})
        kwargs = {}
        for (index, col) in enumerate(r):
            kwargs[cols[index][0]] = col

        monitors.append(BenthicMonitorLog(**kwargs))

    return monitors
