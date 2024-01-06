from enum import Enum


class ServiceName(str, Enum):
    auth = "auth"
    params = "params"
    project = "project"
    tiktok = "tiktok"
    google = "google"
    twitter = "twitter"
    facebook = "facebook"
    instagram = "instagram"
