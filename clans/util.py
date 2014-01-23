from hashlib import md5


def plans_md5(plan):
    """compute the md5 sum of a plan, for verification"""
    return md5(plan.encode('utf8')).hexdigest()
