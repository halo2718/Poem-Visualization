import os
import pandas as pd
from tqdm import tqdm
import json


dynasties = ['XianQin', 'Qin', 'Han', 'WeiJin', 'NanBei', 'Sui', 'Tang',
             'Song', 'Liao', 'Jin', 'Yuan', 'Ming', 'Qing', 'Jindai', 'Dangdai']

def dynasty2Index(dynasty):
    return dynasties.index(dynasty)

def get_data():
    topic_dic = []
    for csv_file in os.listdir('dataset/split_by_dynasty_csv_with_topic'):
        dynasty = csv_file[:-4]
        print('--------', dynasty, '--------')
        df = pd.read_csv(os.path.join('dataset/split_by_dynasty_csv_with_topic', csv_file))
        for row_index, row in tqdm(df.iterrows(), total=len(df)):
            topic_and_prob = row['topic_and_prob']
            if topic_and_prob == '-':
                continue
            topic_and_prob = eval(topic_and_prob)
            for (topic, prob) in topic_and_prob:
                if topic not in topic_dic:
                    topic_dic[topic] = {'XianQin': 0, 'Qin': 0, 'Han': 0, 'WeiJin': 0, 'NanBei': 0,
                                         'Sui': 0, 'Tang': 0, 'Song': 0, 'Liao': 0, 'Jin': 0, 
                                         'Yuan': 0, 'Ming': 0, 'Qing': 0, 'Jindai': 0, 'Dangdai': 0}
                topic_dic[topic][dynasty] += prob
        for topic in topic_dic:
            if topic != 'dynasty':
                topic_dic[topic][dynasty] /= len(df)

    # print(topic_dic)
    with open('data/topic_trend.json', 'w') as f:
        f.write(json.dumps(topic_dic))

get_data()