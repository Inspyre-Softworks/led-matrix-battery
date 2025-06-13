"""
Singleton Decorator for Python Classes.
Ensures that a class has only one instance and provides global access to it.

This implementation uses a dictionary to store instances and a lock for thread safety. The `singleton` function can be
used as a decorator on any class constructor to enforce this behavior.

Usage:
@singleton
class MyClass:
    pass
my_instance1 = MyClass()
my_instance2 = MyClass() # This will return my_instance1 instead of creating a new instance.

"""

import threading
from functools import wraps

def singleton(cls):
    """
    A thread-safe singleton decorator.
    Ensures only one instance of the class exists.
    """
    instances = {}
    lock = threading.Lock()

    @wraps(cls)
    def get_instance(*args, **kwargs):
        nonlocal instances
        with lock:
            if cls not in instances:
                instances[cls] = cls(*args, **kwargs)
        return instances[cls]

    return get_instance

