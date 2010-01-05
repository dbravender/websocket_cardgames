import weakref

__objects = {}

def remember(obj):
    oid = id(obj)
    def remove(*args):
        del __objects[oid]
    __objects[oid] = weakref.ref(obj, remove)

def get_object(oid):
    return __objects[int(oid)]()
