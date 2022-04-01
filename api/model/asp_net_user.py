class AspNetUser:
    Id = None
    FirstName = None
    LastName = None
    Status = None
    VolunteerHours = None
    GroupUpdatedDateTime = None
    ProfileImage = None
    HomePhone = None
    CellPhone = None
    EmergencyPhone = None
    AddressFirst = None
    AddressSecond = None
    City = None
    State = None
    Zip = None
    GroupId = None
    Email = None
    EmailConfirmed = None
    PasswordHash = None
    SecurityStamp = None
    PhoneNumber = None
    PhoneNumberConfirmed = None
    TwoFactorEnabled = None
    LockoutEndDateUtc = None
    LockoutEnabled = None
    AccessFailedCount = None
    UserName = None
    Code = None
    CreatedBy = None
    CreatedDate = None
    ModifiedBy = None
    ModifiedDate = None
    CertificationDate = None
    HasBeenActivated = None

    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)


# gets a set of fields of a single group by a single where
def get_asp_net_user_by(db, fields, by, value):
    sql = '''
            SELECT 
                {0}
            FROM 
                dbo.AspNetUser
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

    return AspNetUser(**kwargs)

