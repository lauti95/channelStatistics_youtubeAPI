import pandas as pd
import requests
from bs4 import BeautifulSoup
from googleapiclient.discovery import build

# Build API access
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
        return "URL not found"


# Assign any channel's URL to the "link" variable
link = 'https://www.youtube.com/@SupraPixel'
id_search = get_channel_id(link)
print("ID found: " + id_search + "\n")

# Enter ID of the channels you want to search in channel_ids
channel_ids = ['UCG5qGWdu8nIRZqJ_GgDwQ-w', 'UCwGX2cE21VPBEJ49hcprP9w', 'UC4rlAVgAK0SGk-yTfe48Qpw']


def get_channel_stats(youtube, channel_ids):

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
pd.set_option('display.max_columns', 6)
pd.set_option('display.width', 300)

channel_stats = get_channel_stats(youtube, channel_ids)

print(channel_stats)
