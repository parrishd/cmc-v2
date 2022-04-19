from datetime import datetime


def getdatetime(dt):
    dateTime = None

    formats = [
        '%m/%d/%Y %I:%M %p',  # current format 1
        '%m/%d/%Y %H:%M %p',  # current format 2
        '%Y-%m-%d %H:%M:%S',  # iso8601 formats
        '%Y-%m-%d %H:%M:%S.%f',  # iso8601 formats
        '%Y-%m-%dT%H:%M:%S.%f',  # iso8601 formats
        '%Y-%m-%dT%H:%M:%S.%f',  # iso8601 formats
        '%Y-%m-%dT%H:%M:%S.%f%z',  # iso8601 formats
    ]

    for f in formats:
        try:
            dateTime = datetime.strptime(dt, f)
            break
        except ValueError:
            pass

    return dateTime
