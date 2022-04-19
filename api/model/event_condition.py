class EventCondition:
    # Id = None
    # EventId = None
    # ConditionId = None
    # Value = None

    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)


def insert_event_condition(db, ec):
    sql = '''
            INSERT INTO dbo.EventConditions (
                EventId,
                ConditionId,
                Value
            ) VALUES(
                ?,
                ?,
                ?
            )
        '''

    db.cursor.execute(
        sql,
        ec.EventId,
        ec.ConditionId,
        ec.Value)

    return True
