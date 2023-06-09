import os
import sys
import random
import numpy as np
import pandas as pd
import tomotopy as tp
from tqdm import tqdm

def analyze_topic_for_dynasty(topic_k=100):
    model = tp.LDAModel.load(f'model/topic_model/lda_{topic_k}.bin')
    res_dict = {}
    for k in range(model.k):
        res_str = f'Topic #{k}: '
        for (w, prob) in model.get_topic_words(k, top_n=10):
            res_str += w + ' '
        res_dict[k] = res_str
    f = open('data/dynasty_top_topic.txt', 'w', encoding='utf-8')

    for csv_file in os.listdir('dataset/split_by_dynasty_csv_with_topic'):
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
        ranked_topic_index = [index for index, value in sorted(list(enumerate(topic_score)), key=lambda x:x[1], reverse=True)]
        for i in ranked_topic_index[:5]:
            f.write(f'[{i}] {res_dict[i]}\n')
        print(csv_file, ranked_topic_index[:5])
    f.close()

analyze_topic_for_dynasty()