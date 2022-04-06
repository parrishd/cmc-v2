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
