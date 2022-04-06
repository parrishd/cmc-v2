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
