import os
import sys
import math
import json
import random
import numpy as np
import pandas as pd
import tomotopy as tp
import pyLDAvis
from collections import Counter
from tqdm import tqdm

def analyze_topic_for_dynasty(topic_k=100):
    res = {}
    model = tp.LDAModel.load(f'model/topic_model/lda_{topic_k}.bin')
    res_dict = {}
    for k in range(model.k):
        res_str = f'Topic #{k}: '
        for (w, prob) in model.get_topic_words(k, top_n=10):
            res_str += w + ' '
        res_dict[k] = res_str
    f = open('data/dynasty_top_topic.txt', 'w', encoding='utf-8')

    for csv_file in os.listdir('dataset/split_by_dynasty_csv_with_topic'):
        dynasty_res = []
        f.write(f'Top 5 topic of {csv_file[:-4]}:\n')
        topic_prob = [0.0 for i in range(topic_k)]
        topic_count = [0 for i in range(topic_k)]
        df = pd.read_csv(os.path.join('dataset/split_by_dynasty_csv_with_topic', csv_file))
        for row_index, row in tqdm(df.iterrows(), total=len(df)):
            topic_and_prob = row['topic_and_prob']
            if topic_and_prob == '-':
                continue
            topic_and_prob = eval(topic_and_prob)
            for (topic, prob) in topic_and_prob:
                topic_prob[topic] += prob
                topic_count[topic] += 1
        topic_score = [(topic_prob[i]/topic_count[i] if topic_count[i] > 0 else 0) for i in range(k)]
        ranked_topic = [(index, value) for index, value in sorted(list(enumerate(topic_score)), key=lambda x:x[1], reverse=True)]
        for i, score in ranked_topic[:20]:
            dynasty_res.append({
                'id': i,
                'score': score,
                'x': random.random(),
                'y': random.random()
            })
            f.write(f'[{i}] (score: {score}) {res_dict[i]}\n')
        # print(csv_file, ranked_topic_index[:5])
        res[csv_file[:-4]] = dynasty_res
    f.close()
    with open('data/bubble.json', 'w', encoding='utf-8') as f:
        json.dump(res, f, ensure_ascii=False, indent=4)

def tf_idf():
    tf_dict = {}
    df_dict = {}
    document_num = 0
    tf_idf_dict = {}
    for txt_file in os.listdir('dataset/segmented'):
        for line in tqdm(open(os.path.join('dataset/segmented', txt_file)).readlines()):
            document_num += 1
            line = line.strip().split()
            line = [w for w in line if '□' not in w]
            counter = Counter(line)
            for word, num in counter.items():
                tf_dict[word] = tf_dict.get(word, 0) + num/len(line)
                df_dict[word] = df_dict.get(word, 0) + 1
    for word in tf_dict.keys():
        tf_idf_dict[word] = tf_dict[word] * math.log(document_num / df_dict[word])
    tf_idf_dict_sorted = sorted(tf_idf_dict.items(), key=lambda kv:(kv[1], kv[0]), reverse=True)
    with open('data/keywords.txt', 'w', encoding='utf-8') as f:
        for word, tf_idf in tf_idf_dict_sorted[:500]:
            f.write(word+'\n')

def get_topic_data(topic_k=100):
    model = tp.LDAModel.load(f'model/topic_model/lda_{topic_k}.bin')
    #获取pyldavis需要的参数
    topic_term_dists = np.stack([model.get_topic_word_dist(k) for k in range(model.k)])
    # doc_topic_dists = np.stack([doc.get_topic_dist() for doc in model.docs])
    # doc_topic_dists /= doc_topic_dists.sum(axis=1, keepdims=True)
    doc_topic_dists = np.random.rand(100, 100)
    doc_lengths = np.array([len(doc.words) for doc in model.docs])
    vocab = list(model.used_vocabs)
    term_frequency = model.used_vocab_freq
    prepared_data = pyLDAvis.prepare(
        topic_term_dists, 
        doc_topic_dists, 
        doc_lengths, 
        vocab, 
        term_frequency,
        start_index=0, # tomotopy话题id从0开始，pyLDAvis话题id从1开始
        sort_topics=False #注意：否则pyLDAvis与tomotopy内的话题无法一一对应。 
    )
    print(prepared_data.keys())

analyze_topic_for_dynasty()
# tf_idf()
# get_topic_data()