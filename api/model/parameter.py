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
    if q is None:
        return None

    idx = 0
    kwargs = {}
    for f in fields:
        kwargs[f] = q[idx]
        idx += 1

    return Parameter(**kwargs)

