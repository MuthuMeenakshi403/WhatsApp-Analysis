import streamlit as st
import preprocessor
import helper
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd

# Set page config for better appearance
st.set_page_config(page_title="WhatsApp Chat Analyzer", layout="wide")

# Custom CSS for enhanced UI
st.markdown(
    """
    <style>
    .main {background-color: #f0f2f6;}
    .stButton>button {border-radius: 10px; font-size: 18px; padding: 10px 20px;}
    .stSidebar {background-color: #2c3e50; color: white;}
    .stDataFrame {border-radius: 10px;}
    .stTextInput>div>div>input {border-radius: 10px;}
    .metric-box {background-color: white; padding: 10px; border-radius: 10px; text-align: center;}
    </style>
    """,
    unsafe_allow_html=True,
)

st.sidebar.title('📊 WhatsApp Chat Analysis')
st.sidebar.image('https://upload.wikimedia.org/wikipedia/commons/thumb/6/6b/WhatsApp.svg/479px-WhatsApp.svg.png', width=100)

st.sidebar.caption(
    'Analyze WhatsApp conversations comprehensively with charts, metrics, and insights.')
st.title('🚀 WhatsApp Chat Analyzer')

with st.expander('ℹ️ How it works?'):
    st.subheader('Steps to Analyze:')
    steps = [
        "📥 Export chat from WhatsApp (without media).",
        "📂 Upload the chat text file.",
        "👤 Select a user or analyze overall chat.",
        "📊 Click 'Show Analysis' to generate insights.",
        "🔎 Explore statistics, activity patterns, and word clouds!"
    ]
    for step in steps:
        st.markdown(f"- {step}")

uploaded_file = st.sidebar.file_uploader("📂 Upload Chat File (.txt)", type=["txt"])
if uploaded_file is not None:
    bytes_data = uploaded_file.getvalue()
    data = bytes_data.decode("utf-8")
    df = preprocessor.preprocess(data)

    user_list = df['user'].unique().tolist()
    if 'group_notification' in user_list:
        user_list.remove('group_notification')
    user_list.sort()
    user_list.insert(0, "Overall")

    selected_user = st.sidebar.selectbox("👤 Select User", user_list)

    if st.sidebar.button("📊 Show Analysis"):
        stats = helper.fetch_stats(selected_user, df)

        st.title("📈 Chat Statistics")
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("📅 Chat From", stats['chat_from'])
        with col2:
            st.metric("📅 Chat To", stats['chat_to'])
        with col3:
            st.metric("👥 Total Members", stats['total_members'])

        col1, col2, col3, col4, col5 = st.columns(5)
        with col1:
            st.metric("💬 Messages", stats['num_messages'])
        with col2:
            st.metric("📝 Words", stats['num_words'])
        with col3:
            st.metric("📸 Media Shared", stats['num_media'])
        with col4:
            st.metric("🔗 Links Shared", stats['num_links'])
        with col5:
            st.metric("📞 Missed Calls", stats['missed_calls'])

        with st.expander("👥 Most Active Users"):
            st.bar_chart(df['user'].value_counts())

        st.title("📆 Monthly Timeline")
        timeline = helper.monthly_timeline(selected_user, df)
        fig, ax = plt.subplots()
        ax.plot(timeline['time'], timeline['message'], color='green', marker="o")
        plt.xticks(rotation='vertical')
        st.pyplot(fig)

        st.title("📊 Activity Map")
        col1, col2 = st.columns(2)
        with col1:
            st.header("📅 Most Active Days")
            busy_day = helper.week_activity_map(selected_user, df)
            fig, ax = plt.subplots()
            ax.bar(busy_day.index, busy_day.values, color='purple')
            plt.xticks(rotation='vertical')
            st.pyplot(fig)

        with col2:
            st.header("📆 Most Active Months")
            busy_month = helper.month_activity_map(selected_user, df)
            fig, ax = plt.subplots()
            ax.bar(busy_month.index, busy_month.values, color='orange')
            plt.xticks(rotation='vertical')
            st.pyplot(fig)

        st.title("🔥 Word Cloud")
        df_wc = helper.create_wordcloud(selected_user, df)
        fig, ax = plt.subplots()
        ax.imshow(df_wc, interpolation='bilinear')
        ax.axis('off')
        st.pyplot(fig)

        st.title("📊 Most Common Words")
        most_common_df = helper.most_common_words(selected_user, df)
        fig, ax = plt.subplots(figsize=(10, 6))
        sns.barplot(x='Frequency', y='Word', data=most_common_df, palette="rocket", ax=ax)
        st.pyplot(fig)

        st.title("😀 Emoji Analysis")
        emoji_df = helper.emoji_helper(selected_user, df)
        col1, col2 = st.columns(2)
        with col1:
            st.dataframe(emoji_df)
        with col2:
            fig, ax = plt.subplots()
            ax.pie(emoji_df['Count'].head(), labels=emoji_df['Emoji'].head(), autopct="%0.2f")
            st.pyplot(fig)

        try:
            response_patterns = helper.get_response_patterns(df)
            if not response_patterns.empty:
                st.subheader("⏳ Response Time Patterns")
                avg_response_times = response_patterns.groupby(['from_user', 'to_user'])['response_time'].mean()
                st.dataframe(avg_response_times.reset_index())

            peak_hours = helper.get_peak_activity_hours(selected_user, df)
            if not peak_hours.empty:
                st.subheader("⏰ Peak Activity Hours")
                fig, ax = plt.subplots()
                peak_hours.plot(kind='bar', ax=ax)
                plt.title('Peak Activity Hours')
                plt.xlabel('Hour of Day')
                plt.ylabel('Number of Messages')
                st.pyplot(fig)
        except Exception as e:
            st.error(f"Error in advanced analytics: {str(e)}")
