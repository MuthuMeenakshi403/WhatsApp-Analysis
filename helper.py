import pandas as pd
import numpy as np
import re
from collections import Counter
from wordcloud import WordCloud
from urlextract import URLExtract
import matplotlib.pyplot as plt
import seaborn as sns
from textblob import TextBlob

def fetch_stats(selected_user, df):
    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]

    num_messages = df.shape[0]
    words = []
    for msg in df['message']:
        words.extend(msg.split())

    media_count = df['message'].str.contains('<Media omitted>', case=False).sum()

    extractor = URLExtract()
    links = []
    for message in df['message']:
        links.extend(extractor.find_urls(str(message)))

    missed_calls = df['message'].str.contains('missed .* call', case=False, regex=True).sum()

    total_members = df['user'].nunique()
    chat_from = df['date'].min().strftime('%Y-%m-%d') if not df.empty else "N/A"
    chat_to = df['date'].max().strftime('%Y-%m-%d') if not df.empty else "N/A"

    return {
        'num_messages': num_messages,
        'num_words': len(words),
        'num_media': media_count,
        'num_links': len(links),
        'missed_calls': missed_calls,
        'total_members': total_members,
        'chat_from': chat_from,
        'chat_to': chat_to
    }

def monthly_timeline(selected_user, df):
    """Generates a monthly message activity timeline"""
    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]

    timeline = df.groupby(['year', 'month_num', 'month']).count()['message'].reset_index()
    timeline['time'] = timeline['month'] + '-' + timeline['year'].astype(str)
    return timeline

def week_activity_map(selected_user, df):
    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]
    return df['day_name'].value_counts()

def month_activity_map(selected_user, df):
    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]
    return df['month'].value_counts()

def create_wordcloud(selected_user, df):
    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]

    wc = WordCloud(width=500, height=500, min_font_size=10, background_color='white').generate(' '.join(df['message']))
    return wc

def most_common_words(selected_user, df):
    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]

    words = ' '.join(df['message'])
    words = re.findall(r'\w+', words)
    most_common = Counter(words).most_common(10)
    return pd.DataFrame(most_common, columns=['Word', 'Frequency'])

def emoji_helper(selected_user, df):
    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]

    emojis = df['message'].str.findall(r'[\U0001F600-\U0001F64F\U0001F300-\U0001F5FF]+')
    emojis = [item for sublist in emojis for item in sublist]
    emoji_counts = Counter(emojis).most_common(10)
    return pd.DataFrame(emoji_counts, columns=['Emoji', 'Count'])

def get_peak_activity_hours(selected_user, df):
    """Finds the top 3 peak activity hours"""
    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]

    hourly_activity = df.groupby('hour')['message'].count()
    peak_hours = hourly_activity.nlargest(3)
    return peak_hours

def get_response_patterns(df):
    """Analyzes response patterns between users"""
    df_sorted = df.sort_values('date')
    df_sorted['time_diff'] = df_sorted['date'].diff()

    response_times = []
    prev_user = None
    for idx, row in df_sorted.iterrows():
        if prev_user and prev_user != row['user']:
            response_times.append({
                'from_user': prev_user,
                'to_user': row['user'],
                'response_time': row['time_diff'].total_seconds() / 60
            })
        prev_user = row['user']

    return pd.DataFrame(response_times)
