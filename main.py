from matplotlib import pyplot as plt
import pandas as pd
import requests
from bs4 import BeautifulSoup
from googleapiclient.discovery import build

# Build API access (YouTube Data API v3). See README file for install instructions
api_key = ''
youtube = build('youtube', 'v3', developerKey=api_key)


# Function to get the channel's ID using the channel URL
def get_channel_id(url):
    # Try a GET request to the URL
    try:
        r = requests.get(url)
        # Parse the source page
        page_parse = BeautifulSoup(r.text, 'html.parser')
        # Find the channel ID by searching for the channelID object
        channel_id_obj = page_parse.find('meta', attrs={'itemprop': 'channelId'})
        if channel_id_obj:
            return channel_id_obj['content']
        else:
            return "ID not found"
    except:
        return "URL not found or blank"


# Assign any channel's URL to the "link" variable
link = 'https://www.youtube.com/@LuchoMellera'
id_search = get_channel_id(link)
print("ID for the entered URL: " + id_search + "\n")

# Enter ID of the channels you want to search in channel_ids
channel_ids = ['UCG5qGWdu8nIRZqJ_GgDwQ-w', 'UCwGX2cE21VPBEJ49hcprP9w', 'UC4rlAVgAK0SGk-yTfe48Qpw',
               'UC7nJPTy93mf0i_dmLZ9EN7A']


def get_channel_stats(channel_ids):
    all_data = []

    # Request channel's info to the API
    request = youtube.channels().list(
        part="snippet, contentDetails, statistics",
        id=','.join(channel_ids)
    )
    response = request.execute()

    # Loop through items to get the specific data we want to use
    for item in response['items']:
        data = {'channelName': item['snippet']['title'],
                'subscribers': item['statistics']['subscriberCount'],
                'views': item['statistics']['viewCount'],
                'totalVideos': item['statistics']['videoCount'],
                'playlistId': item['contentDetails']['relatedPlaylists']['uploads']
                }
        all_data.append(data)

    data_chart = pd.DataFrame(all_data)

    # Turn specific columns to numeric and add new 'avgViewsPerVideo' column
    data_chart['views'] = pd.to_numeric(data_chart['views'])
    data_chart['subscribers'] = pd.to_numeric(data_chart['subscribers'])
    data_chart['totalVideos'] = pd.to_numeric(data_chart['totalVideos'])
    data_chart['avgViewsPerVideo'] = data_chart['views'] / data_chart['totalVideos']
    data_chart['avgViewsPerVideo'] = data_chart['avgViewsPerVideo'].round().astype(int)

    return data_chart


# Fix pandas display size to fit IDE
pd.set_option('display.max_columns', 10)
pd.set_option('display.width', 300)

channel_stats = get_channel_stats(channel_ids)

print("General channel stats for all IDs entered \n", channel_stats, "\n")

# Using playlistId from the dataframe to get data on a specific channel's videos (previous function only retrieves
# total stats)

playlist_id = 'UU7nJPTy93mf0i_dmLZ9EN7A'


def get_video_ids(playlist_id):
    video_ids = []

    request = youtube.playlistItems().list(
        part="snippet, contentDetails",
        playlistId=playlist_id,
        maxResults=50
    )
    response = request.execute()

    for item in response['items']:
        video_ids.append(item['contentDetails']['videoId'])

    # The API request can return up to 50 video ids MAX, so we create a while loop

    next_page_token = response.get('nextPageToken')

    while next_page_token is not None:
        request = youtube.playlistItems().list(
            part="snippet, contentDetails",
            playlistId=playlist_id,
            maxResults=50,
            pageToken=next_page_token
        )
        response = request.execute()

        for item in response['items']:
            video_ids.append(item['contentDetails']['videoId'])

        next_page_token = response.get('nextPageToken')

    return video_ids


video_ids = get_video_ids(playlist_id)


def get_video_details(video_ids):
    all_video_info = []

    # Split video_ids into batches of 50 or less, since that is the APIs max
    id_batches = [video_ids[i:i + 50] for i in range(0, len(video_ids), 50)]

    for id_batch in id_batches:
        request = youtube.videos().list(
            part="snippet,contentDetails,statistics",
            id=id_batch
        )
        response = request.execute()

        for video in response['items']:
            stats_to_keep = {'snippet': ['channelTitle', 'title', 'publishedAt'],
                             'statistics': ['viewCount', 'likeCount', 'commentCount'],
                             'contentDetails': ['duration']
                             }
            video_info = {'video_id': video['id']}

            for k in stats_to_keep.keys():
                for v in stats_to_keep[k]:
                    try:
                        video_info[v] = video[k][v]
                    except:
                        video_info[v] = None

            all_video_info.append(video_info)

    all_video_data = pd.DataFrame(all_video_info)

    all_video_data['viewCount'] = pd.to_numeric(all_video_data['viewCount'])
    all_video_data['likeCount'] = pd.to_numeric(all_video_data['likeCount'])
    all_video_data['commentCount'] = pd.to_numeric(all_video_data['commentCount'])

    return all_video_data


video_df = get_video_details(video_ids)
print("Video statistics for ID " + playlist_id + ":\n", video_df)

# Find and show best performing videos by views

top_videos = video_df.nlargest(10, 'viewCount')
plt.bar(top_videos['title'], top_videos['viewCount'], color="navy")
plt.xticks(rotation=90)
plt.xlabel('Video Title')
plt.ylabel('View Count (M)')
plt.title('Top 10 Videos by View Count')
plt.show()

# Find and show correlation between likes and views

plt.scatter(video_df['viewCount'], video_df['likeCount'])
plt.title('Likes to views ratio')
plt.ylabel('Likes')
plt.xlabel('Views (M)')
plt.show()