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
