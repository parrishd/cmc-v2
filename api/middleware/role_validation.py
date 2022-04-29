def validate(roles, user_roles):
    if len(roles) == 0:
        return True

    for r in roles:
        for ur in user_roles:
            if r == ur['name']:
                return True

    return False
