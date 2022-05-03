# Available Roles
# Admin
# Coordinator
# Member
# Monitor
# Officer
# Integrator


class AspNetUserRole:
    # UserId = None
    # RoleId = None

    # joined with AspNetRoles
    # Id = None
    # Name = None

    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)


# gets a set of fields of a single group by a single where
def get_asp_net_user_roles_by_uid(db, user_id):
    fields = ['RoleId', 'Name']

    sql = '''
            SELECT 
                anur.RoleId,
                anr.Name
            FROM 
                dbo.AspNetUserRoles anur
            INNER JOIN
                dbo.AspNetRoles anr ON anr.Id = anur.RoleId 
            WHERE UserId = ?;
        '''

    db.cursor.execute(sql, user_id)
    q = db.cursor.fetchone()
    if q is None:
        return None

    idx = 0
    kwargs = {}
    for f in fields:
        kwargs[f] = q[idx]
        idx += 1

    return AspNetUserRole(**kwargs)

    # code to handle multiple roles
    # db.cursor.execute(sql, user_id)
    # q = db.cursor.fetchall()
    # if q is None:
    #     return None
    #
    # if len(q) == 0:
    #     return None
    #
    # roles = []
    # for r in q:
    #     idx = 0
    #     kwargs = {}
    #     for f in fields:
    #         kwargs[f] = r[idx]
    #         idx += 1
    #
    #     roles.append(AspNetUserRole(**kwargs))
    #
    # return roles
