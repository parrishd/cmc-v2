class ConditionCategory:
    # Id = None
    # ConditionId = None
    # Category = None
    # Comments = None
    # CategoryText = None
    # Order = None
    # cedrCode = None

    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)


# gets a set of fields of a single station by a single where
def get_condition_category_by(db, fields, by, value):
    sql = '''
            SELECT 
                {0}
            FROM 
                dbo.ConditionCategories
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

    return ConditionCategory(**kwargs)


# gets a set of fields of a single station by a single where
def get_condition_category_by_condition_id_category(db, fields, cid, cat):
    sql = '''
            SELECT 
                {0}
            FROM 
                dbo.ConditionCategories
            WHERE
                ConditionId = ? AND
                Category = ?;
        '''.format(', '.join(fields))

    db.cursor.execute(sql, cid, cat)
    q = db.cursor.fetchone()
    if q is None:
        return None

    idx = 0
    kwargs = {}
    for f in fields:
        kwargs[f] = q[idx]
        idx += 1

    return ConditionCategory(**kwargs)
