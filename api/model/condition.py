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

    print(sql)

    db.cursor.execute(sql, value)
    q = db.cursor.fetchone()
    cols = db.cursor.description
    if q is None:
        return None

    kwargs = {}
    for (index, col) in enumerate(q):
        kwargs[cols[index][0]] = col

    return Condition(**kwargs)


# get all groups paginated
def get_conditions(db, col, direction, offset, limit, search):
    # base SELECT
    sql = '''
            SELECT 
                *
            FROM 
                dbo.Conditions
        '''

    # WHERE clause for searching
    if search != '':
        like = '''
            WHERE
                Name Like '%{0}%'
        '''.format(search)
        sql = f'{sql} {like}'

    # ORDER BY
    sql = f'{sql} ORDER BY {col} {direction}'

    # OFFSET and LIMIT
    if offset >= 0 and limit > 0:
        sql = f'{sql} OFFSET {offset} ROWS FETCH NEXT {limit} ROWS ONLY'

    db.cursor.execute(sql)
    rows = db.cursor.fetchall()
    cols = db.cursor.description

    groups = []
    for r in rows:
        kwargs = {}
        for (index, col) in enumerate(r):
            kwargs[cols[index][0]] = col

        groups.append(Condition(**kwargs))

    return groups


# conditions count
def count(db, search):
    sql = '''
            SELECT 
                COUNT(Id)
            FROM 
                dbo.Conditions
        '''

    if search != '':
        like = '''
            WHERE
                Name Like '%{0}%'
        '''.format(search)
        sql = f'{sql} {like}'

    db.cursor.execute(sql)
    q = db.cursor.fetchone()

    if q is None:
        return None

    return q[0]


def insert(db, condition):
    sql = '''
            INSERT INTO dbo.Conditions (
                {0}
            ) VALUES(
                {1}       
            )
        '''.format(','.join(condition.keys()), ','.join(['?' for _ in condition.values()]))

    db.cursor.execute(sql, *condition.values())

    db.cursor.execute('SELECT IDENT_CURRENT(\'dbo.Conditions\')')
    id = db.cursor.fetchone()[0]
    db.cursor.commit()

    return id


def update(db, cid, group):
    sql = '''
            UPDATE dbo.Conditions SET
                {0} = ?
            WHERE
                Id = ?
        '''.format(' = ?, '.join(group.keys()))

    db.cursor.execute(sql, *group.values(), cid)
    db.cursor.commit()

    return cid


def delete(db, cid):
    sql = '''
            DELETE FROM dbo.Conditions WHERE Id = ?
        '''
    db.cursor.execute(sql, cid)
    db.cursor.commit()
    return cid
