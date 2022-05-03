class FlaskUser:
    # Id = None
    # Email = None
    # PasswordHash = None

    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)


# gets a set of fields of a single group by a single where
def get_flask_user_by(db, fields, by, value):
    sql = '''
            SELECT 
                {0}
            FROM 
                dbo.FlaskUsers
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

    return FlaskUser(**kwargs)


def insert_flask_user(db, fu):
    sql = '''
            INSERT INTO dbo.FlaskUsers 
                (Id, Email, PasswordHash)
            VALUES
                (?, ?, ?)
        '''
    db.cursor.execute(sql, fu.Id, fu.Email, fu.PasswordHash)
    db.cursor.commit()
    return db.cursor.rowcount
