class Group:
    # Id = None
    # Name = None
    # ContactName = None
    # ContactEmail = None
    # ContactCellPhone = None
    # ContactOfficePhone = None
    # ParametersSampled = None
    # Description = None
    # Url = None
    # Logo = None
    # AddressFirst = None
    # AddressSecond = None
    # City = None
    # State = None
    # Zip = None
    # Code = None
    # Status = None
    # CreatedBy = None
    # CreatedDate = None
    # ModifiedBy = None
    # ModifiedDate = None
    # BenthicMethod = None
    # CmcMember = None
    # CmcMember2 = None
    # CmcMember3 = None
    # CmcMember4 = None
    # CmcMember5 = None
    # cmcQapp = None
    # coordinatorCanPublish = None
    # DataUseDate = None

    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)


def cmc_members_to_array(g):
    cmc = []
    if hasattr(g, 'CmcMember') and g.CmcMember is not None:
        cmc.append(g.CmcMember)
    if hasattr(g, 'CmcMember2') and g.CmcMember2 is not None:
        cmc.append(g.CmcMember2)
    if hasattr(g, 'CmcMember3') and g.CmcMember3 is not None:
        cmc.append(g.CmcMember3)
    if hasattr(g, 'CmcMember4') and g.CmcMember4 is not None:
        cmc.append(g.CmcMember4)
    if hasattr(g, 'CmcMember5') and g.CmcMember5 is not None:
        cmc.append(g.CmcMember5)
    return cmc


# gets a set of fields of a single group by a single where
def get_group_by(db, fields, by, value):
    sql = '''
            SELECT 
                {0}
            FROM 
                dbo.Groups
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

    return Group(**kwargs)


# get all groups paginated
def get_groups(db, col, direction, offset, limit, search):
    # base SELECT
    sql = '''
            SELECT 
                *
            FROM 
                dbo.Groups
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

    groups = []
    for r in rows:
        kwargs = {}
        for (index, col) in enumerate(r):
            kwargs[cols[index][0]] = col

        groups.append(Group(**kwargs))

    return groups


# group count
def count(db, search):
    sql = '''
            SELECT 
                COUNT(Id)
            FROM 
                dbo.Groups
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


def insert(db, group):
    sql = '''
            INSERT INTO dbo.Groups (
                {0}
            ) VALUES(
                {1}       
            )
        '''.format(','.join(group.keys()), ','.join(['?' for _ in group.values()]))

    print(sql)

    db.cursor.execute(sql, *group.values())

    db.cursor.execute('SELECT IDENT_CURRENT(\'dbo.Groups\')')
    id = db.cursor.fetchone()[0]
    db.cursor.commit()

    return id


def delete(db, gid):
    sql = '''
            DELETE FROM dbo.Groups WHERE Id = ?
        '''
    db.cursor.execute(sql, gid)
    db.cursor.commit()
    return gid
