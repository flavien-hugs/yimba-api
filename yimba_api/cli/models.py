from enum import Enum


class ServiceName(str, Enum):
    auth = "auth"
    params = "params"
    project = "project"
    facebook = "facebook"
