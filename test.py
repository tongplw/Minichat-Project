from datetime import datetime, timedelta


def can_login(is_online, last_login):
    if last_login < datetime.now() - timedelta(hours=1) or not is_online:
        return True
    return False