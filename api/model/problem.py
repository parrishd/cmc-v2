class Problem:
    # Id = None
    # Code = None
    # Description = None
    # Order = None
    # ApplicationText = None

    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)


def get_problem_by(db, fields, by, value):
    sql = '''
            SELECT 
                {0}
            FROM 
                dbo.Problems
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

    return Problem(**kwargs)
