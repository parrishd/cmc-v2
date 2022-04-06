class BenthicSample:
    # Id = None
    # Value = None
    # Comments = None
    # QaFlagId = None
    # CreatedBy = None
    # CreatedDate = None
    # ModifiedBy = None
    # ModifiedDate = None
    # BenthicEventId = None
    # BenthicParameterId = None

    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)


def insert_benthic_sample(db, bs):
    sql = '''
            INSERT INTO dbo.BenthicSamples (
                Value,
                Comments,
                QaFlagId,
                CreatedBy,
                CreatedDate,
                ModifiedBy,
                ModifiedDate,
                BenthicEventId,
                BenthicParameterId
            ) VALUES(
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
        bs.Value,
        bs.Comments,
        bs.QaFlagId,
        bs.CreatedBy,
        bs.CreatedDate,
        bs.ModifiedBy,
        bs.ModifiedDate,
        bs.BenthicEventId,
        bs.BenthicParameterId)

    return True

# gets a set of fields of a single station by a single where
def get_benthic_sample_by(db, fields, by, value):
    sql = '''
            SELECT 
                {0}
            FROM 
                dbo.BenthicSamples
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

    return BenthicSample(**kwargs)

