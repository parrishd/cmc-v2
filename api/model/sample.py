class Sample:
    # Id = None
    # Value = None
    # Depth = None
    # SampleId = None
    # Comments = None
    # EventId = None
    # ParameterId = None
    # QaFlagId = None
    # QualifierId = None
    # CreatedBy = None
    # CreatedDate = None
    # ModifiedBy = None
    # ModifiedDate = None

    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)


# gets a set of fields of a single group by a single where
def get_sample_by(db, fields, by, value):
    sql = '''
            SELECT 
                {0}
            FROM 
                dbo.Samples
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

    return Sample(**kwargs)


def insert_sample(db, wqs):
    sql = '''
            INSERT INTO dbo.Samples (
                Value,
                Depth,
                SampleId,
                Comments,
                EventId,
                ParameterId,
                ProblemId,
                QaFlagId,
                QualifierId,
                CreatedBy,
                CreatedDate,
                ModifiedBy,
                ModifiedDate
            ) VALUES(
                ?,
                ?,
                ?,
                ?,
                ?,
                ?,
                ?,
                ?,
                ?,
                ?,
                ?,
                ?,
                ?
            )
        '''

    db.cursor.execute(
        sql,
        wqs.Value,
        wqs.Depth,
        wqs.SampleId,
        wqs.Comments,
        wqs.EventId,
        wqs.ParameterId,
        wqs.ProblemId,
        wqs.QaFlagId,
        wqs.QualifierId,
        wqs.CreatedBy,
        wqs.CreatedDate,
        wqs.ModifiedBy,
        wqs.ModifiedDate)

    return True
