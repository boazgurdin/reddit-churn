import nltk
from sklearn.base import TransformerMixin
import string, re
import numpy as np

class PostStemmer(TransformerMixin):

    punc_re = re.compile('[%s]$' % re.escape(string.punctuation))
    stemmer = nltk.stem.SnowballStemmer('english', ignore_stopwords=True) #don't stem stopwords

    # is_word = re.compile('[A-Za-z]')

    # @classmethod
    # def is_punc(word): #returns true if word is all punctuation or numbers
    #     return not is_word.search(word)

    @classmethod
    def trim_punc(cls, word):
        return cls.punc_re.sub('', word)

    @classmethod
    def clean_tweet(cls, tweet):
        try:
            tweet = unicode(tweet, 'utf8')
            words = tweet.split()
            clean_words = []
            for word in words:
                # remove @user, #hashtag, :P smileys, -- dashes
                if word[0] in string.punctuation:
                    continue
                # remove URLs
                if word.startswith('http'):
                    continue
                # keep clean words
                else:
                    word = cls.trim_punc(word)
                    word = cls.stemmer.stem(word) #Unicode errors
                    clean_words.append(word)
            clean_tweet = u' '.join(clean_words)
            return clean_tweet
        except UnicodeDecodeError:
            return u''

    def fit(self, x, y=None):
        return self

    def transform(self, tweets):
        clean_tweets = np.vectorize(self.clean_tweet)
        return clean_tweets(tweets)
