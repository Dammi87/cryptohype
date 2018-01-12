# Returns a flow that will prompt for offline access, thus receiving
# a refresh_token in the auth object that gets returned

from oauth2client.client import OAuth2WebServerFlow
from oauth2client import tools
from oauth2client.file import Storage
from googleapiclient.discovery import build
import json
import pickle
import os
SCOPES = ['https://www.googleapis.com/auth/youtube.force-ssl']
API_SERVICE_NAME = 'youtube'
API_VERSION = 'v3'


def prepare_flow(secrets_path, scope):
    # Grab settings from the client_secrets.json file provided by Google
    with open(secrets_path, 'r') as fp:
        obj = json.load(fp)

    # The secrets we need are in the 'web' node
    secrets = obj['installed']

    # Return a Flow that requests a refresh_token
    return OAuth2WebServerFlow(
        client_id=secrets['client_id'],
        client_secret=secrets['client_secret'],
        scope=scope,
        redirect_uri=secrets['redirect_uris'][0],
        access_type='offline',
        prompt="consent")


def get_credentials():
    storage = Storage('creds.data')
    return tools.run_flow(prepare_flow('client_secret.json', SCOPES), storage)


def get_service():
    credentials = get_credentials()
    return build(API_SERVICE_NAME, API_VERSION, credentials=credentials)


def remove_empty_kwargs(**kwargs):
    good_kwargs = {}
    if kwargs is not None:
        for key in kwargs:
            if kwargs[key]:
                good_kwargs[key] = kwargs[key]
    return good_kwargs


def get_channel_id_kwarg(client, **kwargs):
    # See full sample for function
    kwargs = remove_empty_kwargs(**kwargs)

    response = client.search().list(
        **kwargs
    ).execute()

    return response


def get_channel_id(client, channel_name):
    return get_channel_id_kwarg(client, part="snippet", type="channel", q=channel_name)["items"][0]["id"]["channelId"]


def get_uploads_playlist_raw(client, **kwargs):
    # See full sample for function
    kwargs = remove_empty_kwargs(**kwargs)

    response = client.channels().list(
        **kwargs
    ).execute()

    return response


def get_uploads_playlist(client, channel_name):
    channel_id = get_channel_id(client, channel_name)
    r = get_uploads_playlist_raw(
        client,
        part='snippet,contentDetails,statistics',
        id=channel_id
    )
    return r["items"][0]["contentDetails"]["relatedPlaylists"]["uploads"]


def get_videos_in_channel_raw(client, **kwargs):
    # See full sample for function
    kwargs = remove_empty_kwargs(**kwargs)

    response = client.playlistItems().list(
        **kwargs
    ).execute()

    return response


def get_videos_in_channel(client, channel_name):
    def get_vid_dict(_id, publish_time, title, desc):
        return {
            "id": _id,
            "publish_time": publish_time,
            "title": title,
            "desc": desc
        }

    video_info = []
    playlist_id = get_uploads_playlist(client, channel_name)
    r = get_videos_in_channel_raw(
        client,
        part='snippet,contentDetails',
        playlistId=playlist_id
    )

    while "nextPageToken" in r:
        for item in r["items"]:
            info = item["contentDetails"]
            snipp = item["snippet"]

            video_info.append(get_vid_dict(
                info["videoId"],
                info["videoPublishedAt"],
                snipp["title"],
                snipp["description"]
            ))

        r = get_videos_in_channel_raw(
            client,
            maxResults=None,
            part='snippet,contentDetails',
            playlistId=playlist_id,
            pageToken=r["nextPageToken"]
        )

    return video_info


def get_comment_in_video_raw(client, **kwargs):
    # See full sample for function
    kwargs = remove_empty_kwargs(**kwargs)

    response = client.commentThreads().list(
        **kwargs
    ).execute()

    return response


def get_comment_in_video(client, video_id):
    r = get_comment_in_video_raw(
        client,
        part='snippet,replies',
        videoId=video_id)

    comments = {"text": [], "publish_time": []}
    while "nextPageToken" in r:
        for item in r["items"]:
            comments["text"].append(
                item["snippet"]["topLevelComment"]["snippet"]["textDisplay"])
            comments["publish_time"].append(
                item["snippet"]["topLevelComment"]["snippet"]["publishedAt"])

        r = get_comment_in_video_raw(
            client,
            part='snippet,replies',
            videoId=video_id,
            pageToken=r["nextPageToken"])

    return comments


def get_video_viewcount_raw(client, **kwargs):
    kwargs = remove_empty_kwargs(**kwargs)
    response = client.videos().list(
        **kwargs
    ).execute()
    return response


def get_video_stats(client, video_id):
    r = get_video_viewcount_raw(
        client,
        part='snippet,contentDetails,statistics',
        id=video_id
    )

    stats = {
        "views": int(r["items"][0]["statistics"]["viewCount"]),
        "likes": int(r["items"][0]["statistics"]["likeCount"]),
        "dislikes": int(r["items"][0]["statistics"]["dislikeCount"])
    }

    return stats


def get_all_info(client, channel):
    videos = get_videos_in_channel(client, channel)
    for video in videos:

        folderpath = os.path.abspath(os.path.join("./data", ''.join(channel.split(' '))))
        filepath = os.path.join(folderpath, "%s.pickle" % video["id"])

        if os.path.isfile(filepath):
            continue

        stats = get_video_stats(client, video["id"])
        comments = get_comment_in_video(client, video["id"])

        # Add
        video["stats"] = stats
        video["comments"] = comments

        if not os.path.isdir(folderpath):
            os.makedirs(folderpath)

        with open(filepath, 'wb') as fp:
            pickle.dump(video, fp)


if __name__ == "__main__":
    service = get_service()
    get_all_info(service, "Altcoin Buzz")
