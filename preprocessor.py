import pandas as pd
import re

def preprocess(data):
    lines = data.split('\n')
    messages = []

    patterns = {
        '12h_standard': r'(\d{2}/\d{2}/\d{2},\s\d{1,2}:\d{2}\s[APMapm]{2})\s-\s(.*?):\s?(.*)',
        '24h_standard': r'(\d{2}/\d{2}/\d{2},\s\d{1,2}:\d{2})\s-\s(.*?):\s?(.*)',
        '12h_bracketed': r'\[(\d{2}/\d{2}/\d{2},\s\d{2}:\d{2}:\d{2}\s[APMapm]{2})\]\s(.*?):\s(.*)',
        '24h_bracketed': r'\[(\d{2}/\d{2}/\d{2},\s\d{2}:\d{2}:\d{2})\]\s(.*?):\s(.*)'
    }

    for line in lines:
        line = line.strip()
        if not line:
            continue

        matched = False
        for pattern in patterns.values():
            match = re.match(pattern, line)
            if match:
                date_time, user, message = match.groups()
                messages.append([date_time, user.strip(), message.strip()])
                matched = True
                break

        if not matched and messages:
            messages[-1][2] += '\n' + line.strip()

    df = pd.DataFrame(messages, columns=['date', 'user', 'message'])

    date_formats = [
        '%d/%m/%y, %I:%M %p', '%d/%m/%y, %H:%M',
        '%d/%m/%y, %I:%M:%S %p', '%d/%m/%y, %H:%M:%S'
    ]

    def convert_datetime(date_series):
        for fmt in date_formats:
            try:
                return pd.to_datetime(date_series, format=fmt)
            except:
                continue
        return pd.to_datetime(date_series, errors='coerce')

    df['date'] = convert_datetime(df['date'])
    df = df.dropna(subset=['date'])

    if not df.empty:
        df['year'] = df['date'].dt.year
        df['month'] = df['date'].dt.month_name()
        df['month_num'] = df['date'].dt.month
        df['day'] = df['date'].dt.day
        df['day_name'] = df['date'].dt.day_name()
        df['hour'] = df['date'].dt.hour
        df['minute'] = df['date'].dt.minute

    return df
