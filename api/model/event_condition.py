class EventCondition:
    # Id = None
    # EventId = None
    # ConditionId = None
    # Value = None

    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)


def get_event_condition_by_event_id(db, eid):
    sql = '''
            SELECT 
                *
            FROM 
                dbo.EventConditions
            JOIN  
                dbo.Conditions
            ON
                dbo.EventConditions.ConditionId = dbo.Conditions.Id
            WHERE
                EventId = ?
        '''

    db.cursor.execute(sql, eid)
    rows = db.cursor.fetchall()
    cols = db.cursor.description
    conditions = []
    for r in rows:
        kwargs = {}
        for (index, col) in enumerate(r):
            kwargs[cols[index][0]] = col

        conditions.append(EventCondition(**kwargs))

    return conditions


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
