def validate(roles, ur):
    print(roles)
    print(ur)

    if len(roles) == 0:
        return True

    for r in roles:
        if r == ur['name']:
            return True

    return False
