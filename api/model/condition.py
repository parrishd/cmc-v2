class Condition:
    # Id = None
    # Code = None
    # Name = None
    # Description = None
    # Status = None
    # isCategorical = None
    # Order = None

    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)


# gets a set of fields of a single station by a single where
def get_condition_by(db, fields, by, value):
    sql = '''
            SELECT 
                {0}
            FROM 
                dbo.Conditions
            WHERE
                {1} = ?;
        '''.format(', '.join(fields), by)

    db.cursor.execute(sql, value)
    q = db.cursor.fetchone()
    if q is None:
        return None

    idx = 0
    kwargs = {}
    for f in fields:
        kwargs[f] = q[idx]
        idx += 1

    return Condition(**kwargs)

