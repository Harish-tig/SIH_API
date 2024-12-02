import uuid

def userIdGen():
    return uuid.uuid4().hex[:12]