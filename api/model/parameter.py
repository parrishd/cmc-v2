class Parameter:
    # Id = None
    # Name = None
    # Units = None
    # Method = None
    # Tier = None
    # Matrix = None
    # Tidal = None
    # NonTidal = None
    # AnalyticalMethod = None
    # ApprovedProcedure = None
    # Equipment = None
    # Precision = None
    # Accuracy = None
    # Range = None
    # QcCriteria = None
    # InspectionFreq = None
    # InspectionType = None
    # CalibrationFrequency = None
    # StandardOrCalInstrumentUsed = None
    # TierIIAdditionalReqs = None
    # HoldingTime = None
    # SamplePreservation = None
    # Code = None
    # Status = None
    # requiresSampleDepth = None
    # isCalibrationParameter = None
    # requiresDuplicate = None
    # Description = None
    # NonfatalUpperRange = None
    # NonfatalLowerRange = None

    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)


# gets a set of fields of a single station by a single where
def get_parameter_by(db, fields, by, value):
    sql = '''
             SELECT 
                 {0}
             FROM 
                 dbo.Parameters
             WHERE
                 {1} = ?;
         '''.format(', '.join(fields), by)

    db.cursor.execute(sql, value)
    q = db.cursor.fetchone()
    cols = db.cursor.description
    if q is None:
        return None

    kwargs = {}
    for (index, col) in enumerate(q):
        kwargs[cols[index][0]] = col

    return Parameter(**kwargs)


# get all parameters
def get_parameters(db, col, direction, offset, limit, search):
    # base SELECT
    sql = '''
            SELECT 
                *
            FROM 
                dbo.Parameters
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

    print(sql)

    db.cursor.execute(sql)
    rows = db.cursor.fetchall()
    cols = db.cursor.description

    params = []
    for r in rows:
        kwargs = {}
        for (index, col) in enumerate(r):
            kwargs[cols[index][0]] = col

        params.append(Parameter(**kwargs))

    return params


def count(db, search):
    sql = '''
            SELECT 
                COUNT(Id)
            FROM 
                dbo.Parameters
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


def insert(db, param):
    sql = '''
            INSERT INTO dbo.Parameters (
                {0}
            ) VALUES(
                {1}       
            )
        '''.format(','.join(param.keys()), ','.join(['?' for _ in param.values()]))
    print(sql)
    db.cursor.execute(sql, *param.values())

    db.cursor.execute('SELECT IDENT_CURRENT(\'dbo.Parameters\')')
    id = db.cursor.fetchone()[0]
    db.cursor.commit()

    return id


def update(db, pid, params):
    sql = '''
            UPDATE dbo.Parameters SET
                {0} = ?
            WHERE
                Id = ?
        '''.format(' = ?, '.join(params.keys()))

    db.cursor.execute(sql, *params.values(), pid)
    db.cursor.commit()

    return pid


def delete(db, cid):
    sql = '''
            DELETE FROM dbo.Parameters WHERE Id = ?
        '''
    db.cursor.execute(sql, cid)
    db.cursor.commit()
    return cid
