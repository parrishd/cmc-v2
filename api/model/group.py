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
    if q is None:
        return None

    idx = 0
    kwargs = {}
    for f in fields:
        kwargs[f] = q[idx]
        idx += 1

    return Group(**kwargs)

