from enum import Enum


class TaskStatus(str, Enum):

    TODO = "TODO"

    IN_PROGRESS = "IN_PROGRESS"

    REVIEW = "REVIEW"

    DONE = "DONE"

    FAILED = "FAILED"