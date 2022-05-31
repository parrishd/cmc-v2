class BenthicEventCondition:
    # Id = None
    # BenthicEventId = None
    # BenthicConditionId = None
    # Value = None

    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)


def insert_benthic_event_condition(db, ec):
    sql = '''
            INSERT INTO dbo.BenthicEventConditions (
                BenthicEventId,
                BenthicConditionId,
                Value
            ) VALUES(
                ?,
                ?,
                ?
            )
        '''

    db.cursor.execute(
        sql,
        ec.BenthicEventId,
        ec.BenthicConditionId,
        ec.Value)

    return True


def get_benthic_event_condition(db, value):
    sql = '''
            SELECT 
                *
            FROM 
                dbo.BenthicEventConditions
            JOIN  
                dbo.BenthicConditions
            ON
                dbo.BenthicEventConditions.BenthicConditionId = dbo.BenthicConditions.Id
            WHERE
                BenthicEventId = ?;
        '''

    db.cursor.execute(sql, value)
    rows = db.cursor.fetchall()
    cols = db.cursor.description
    conditions = []
    for r in rows:
        kwargs = {}
        for (index, col) in enumerate(r):
            kwargs[cols[index][0]] = col

        conditions.append(BenthicEventCondition(**kwargs))

    return conditions
