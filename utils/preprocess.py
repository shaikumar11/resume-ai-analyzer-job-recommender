import re
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.stem import WordNetLemmatizer

# Download required NLTK data (only runs once, then cached)
nltk.download("punkt", quiet=True)
nltk.download("punkt_tab", quiet=True)
nltk.download("stopwords", quiet=True)
nltk.download("wordnet", quiet=True)

lemmatizer = WordNetLemmatizer()
stop_words = set(stopwords.words("english"))


def clean_text(text):
    """Lowercase, remove special characters, tokenize, remove stopwords, lemmatize."""
    # Lowercase
    text = text.lower()

    # Remove emails, URLs, phone numbers
    text = re.sub(r"\S+@\S+", " ", text)
    text = re.sub(r"http\S+|www\S+", " ", text)
    text = re.sub(r"\+?\d[\d\s\-()]{7,}\d", " ", text)

    # Remove special characters, keep letters only
    text = re.sub(r"[^a-zA-Z\s]", " ", text)

    # Tokenize
    tokens = word_tokenize(text)

    # Remove stopwords and short tokens, then lemmatize
    cleaned_tokens = [
        lemmatizer.lemmatize(word)
        for word in tokens
        if word not in stop_words and len(word) > 1
    ]

    return " ".join(cleaned_tokens)