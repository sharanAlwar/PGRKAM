import pandas as pd
df=pd.read_csv(r"C:\Users\subbu\Downloads\Feedbacks - Sheet1.csv")
import pandas as pd
import nltk
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords

nltk.download('punkt')
nltk.download('stopwords')
column_name = "Comment"
regex_pattern = "[^a-zA-Z0-9, ']"

df[column_name] = df[column_name].replace(regex_pattern, '', regex=True)
column_name = "Comment"
regex_pattern = "[^a-zA-Z0-9, ']"

df[column_name] = df[column_name].replace(regex_pattern, '', regex=True)
df['Comment'].fillna('', inplace=True)
df['preprocessed_comment'] = df['Comment'].str.lower().replace(r'[^\w\s]', '', regex=True)

df['comment_tokens'] = df['preprocessed_comment'].apply(word_tokenize)

stop_words = set(stopwords.words('english'))
df['filtered_comment_tokens'] = df['comment_tokens'].apply(lambda tokens: [word for word in tokens if word not in stop_words])
import nltk
from nltk.sentiment import SentimentIntensityAnalyzer
import pandas as pd

sid = SentimentIntensityAnalyzer()
df['comment_sentiment_score'] = df['preprocessed_comment'].apply(lambda x: sid.polarity_scores(x)['compound'])
df['emoji_score'] = 0.0
df.loc[df['Emoji'] == 'Sad', 'emoji_score'] = -1.0
df.loc[df['Emoji'] == 'Happy', 'emoji_score'] = 1.0
df.loc[df['Emoji'] == 'Neutral', 'emoji_score'] = 0.0
df['combined_sentiment_score'] = (df['comment_sentiment_score'] + df['emoji_score']) / 2
df['combined_sentiment_score']
df['sentiment'] = df['combined_sentiment_score'].apply(lambda x: 'Positive' if x > 0 else 'Negative' if x < 0 else 'Neutral')
df.to_csv('feedback.csv')
