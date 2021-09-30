from enum import Enum

class JobStatus(Enum):
    CREATED = 0
    STARTING = 1
    RUNNING = 2
    STOPPING = 3
    STOPPED = 4
    SUCCESS = 5
    FAIL = 6
