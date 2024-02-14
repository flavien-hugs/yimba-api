from enum import Enum


class ServiceName(str, Enum):
    auth = "auth"
    params = "params"
    project = "project"
    tiktok = "tiktok"
    google = "google"
    analyse = "analyse"
    twitter = "twitter"
    youtube = "youtube"
    rapport = "rapport"
    facebook = "facebook"
    instagram = "instagram"
    cloudtags = "cloudtags"
