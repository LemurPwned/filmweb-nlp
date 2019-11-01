import os

import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import CountVectorizer, TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import precision_recall_fscore_support
from sklearn.model_selection import train_test_split


def load_dataset():
    filenames = os.listdir('.')
    filenames = filter(lambda x: x.endswith('.csv'), filenames)
    df = None
    for filename in filenames:
        tmp = pd.read_csv(filename)
        if df is None:
            df = tmp
        else:
            df = pd.concat([df, tmp])

    df.drop_duplicates(inplace=True)
    # suffle that shit
    df = df.sample(frac=1).reset_index(drop=True)
    return df


def tfidf_transformer(df):
    X_train, X_test, y_train, y_test = train_test_split(
        df['content'],
        df['rating'],
        test_size=0.3,
        random_state=1234,
    )

    tfidf_vectorizer = TfidfVectorizer(use_idf=True, max_df=0.95, sublinear_tf=True)
    tfidf_vectorizer.fit_transform(X_train)

    train_feature_set = tfidf_vectorizer.transform(X_train)
    test_feature_set = tfidf_vectorizer.transform(X_test)

    return train_feature_set, test_feature_set, y_train, y_test, tfidf_vectorizer


def logistic_regression_training(df):
    train_feature_set, test_feature_set, \
        y_train, y_test, tfidf_vectorizer = tfidf_transformer(
        df)

    log_reg = LogisticRegression(verbose=1,
                                #  solver='liblinear',
                                 random_state=123,
                                 C=5,
                                 penalty='l2',
                                 max_iter=20000)
    log_reg.fit(train_feature_set, y_train)
    score = log_reg.score(test_feature_set, y_test)
    print(score)

df = load_dataset()
logistic_regression_training(df)
