from datetime import datetime

def get_dates(params):
    before = None
    after = None
    try:
        if "after" in params.keys():
            after = datetime.fromtimestamp ( int(params ["after"]) )
        if "before" in params.keys():
            before = datetime.fromtimestamp ( int(params ["before"] ))

        return before, after
    except Exception as e:
        raise e


def get_beetween(data, before=None, after=None):
    if before and after:
        return [obj for obj in data if after < obj.start_date < before]
    if before:
        return [obj for obj in data if  obj.start_date < before]
    if after:
        return [obj for obj in data if  after < obj.start_date]
    return data

