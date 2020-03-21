## bag of words

## https://towardsdatascience.com/multi-class-text-classification-with-scikit-learn-12f1e60e0a9f
## wget https://files.consumerfinance.gov/ccdb/complaints.csv.zip
## unzip complaints.csv.zip

import pandas as pd
df = pd.read_csv('consumer_complaints.csv')
df.info ()
print (df.head())

from io import StringIO

col = ['product', 'consumer_complaint_narrative']
df = df[col]
df = df[pd.notnull(df['consumer_complaint_narrative'])]

df.columns = ['product', 'consumer_complaint_narrative']

df['category_id'] = df['product'].factorize()[0]
category_id_df = df[['product', 'category_id']].drop_duplicates().sort_values('category_id')
category_to_id = dict(category_id_df.values)
id_to_category = dict(category_id_df[['category_id', 'product']].values)
print (df.head())


import matplotlib.pyplot as plt
fig = plt.figure(figsize=(8,6))
df.groupby('product').consumer_complaint_narrative.count().plot.bar(ylim=0)
#plt.show() ## stops the program

# Term Frequency, Inverse Document Frequency, abbreviated to tf-idf.

from sklearn.feature_extraction.text import TfidfVectorizer
tfidf = TfidfVectorizer(sublinear_tf=True, min_df=5, norm='l2', encoding='latin-1', ngram_range=(1, 2), stop_words='english')
features = tfidf.fit_transform(df.consumer_complaint_narrative).toarray()
labels = df.category_id
features.shape
