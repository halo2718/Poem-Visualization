import os
import sys
import random
import numpy as np
import tomotopy as tp
import pandas as pd
from tqdm import tqdm
from deepthulac import LacModel
import pyLDAvis

def get_stopwords():
    stopwords_file = 'dataset/stopwords.txt'
    stopwords = []
    for line in open(stopwords_file, 'r', encoding='utf-8'):
        stopwords.append(line.strip())
    return stopwords

def seg_word_and_train_topic_model(topic_k=100):
    model = tp.LDAModel(k=topic_k, min_cf=50)
    stopwords = get_stopwords()

    lac = LacModel.load(path='../deepthulac-seg-model', device='mps')
    csv_path = 'dataset/split_by_dynasty_csv'
    for csv_file in os.listdir(csv_path):
        if os.path.exists(f'dataset/segmented/{csv_file[:-4]}.txt'):
            lines = open(f'dataset/segmented/{csv_file[:-4]}.txt', 'r', encoding='utf-8').readlines()
            if len(lines) > 60000:
                lines = random.sample(lines, 60000)
            for line in lines:
                line = line.strip().split()
                line = [w for w in line if '□' not in w]
                model.add_doc(line)
            continue
        print(f'Segmenting {csv_file}...')
        f = open(f'dataset/segmented/{csv_file[:-4]}.txt', 'w', encoding='utf-8')
        df = pd.read_csv(os.path.join(csv_path, csv_file))
        for row_index, row in tqdm(df.iterrows(), total=len(df)):
            content = eval(row['content'])
            content = [l[:-1] for l in content if len(l)>1] # 去掉句尾标点符号
            # print(content)
            result = lac.seg(content, show_progress_bar=False)['seg']['res']
            seg_result = []
            for sent in result:
                seg_result += [word for word in sent if (word not in stopwords and '□' not in word)]
            f.write(' '.join(seg_result))
            f.write('\n')
            model.add_doc(seg_result)
        f.close()
    model.train(0)
    print('Num docs:', len(model.docs), ', Vocab size:', len(model.used_vocabs), ', Num words:', model.num_words, file=sys.stderr, flush=True)
    for i in range(0, 200, 10):
        model.train(10)
        print('Iteration: {}\tLog-likelihood: {}'.format(i, model.ll_per_word), file=sys.stderr, flush=True)

    for k in range(model.k):
        res_str = f'Topic #{k}: '
        for (w, prob) in model.get_topic_words(k, top_n=10):
            res_str += w + ' '
        print(res_str)

    #获取pyldavis需要的参数
    topic_term_dists = np.stack([model.get_topic_word_dist(k) for k in range(model.k)])
    doc_topic_dists = np.stack([doc.get_topic_dist() for doc in model.docs])
    doc_topic_dists /= doc_topic_dists.sum(axis=1, keepdims=True)
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
    #可视化结果存到html文件中
    pyLDAvis.save_html(prepared_data, 'data/ldavis.html')

    print('saving model...', file=sys.stderr, flush=True)
    model.save(f'model/topic_model/lda_{model.k}.bin', full=False)
    print('model saved!', file=sys.stderr, flush=True)
    

def inference(topic_k=100):
    print('loading model...', file=sys.stderr, flush=True)
    model = tp.LDAModel.load(f'model/topic_model/lda_{topic_k}.bin')
    print('model loaded!', file=sys.stderr, flush=True)
    
    # topic_word_dict = {}
    # for k in range(model.k):
    #     res_str = f'Topic #{k}: '
    #     for (w, prob) in model.get_topic_words(k, top_n=10):
    #         res_str += w + ' '
    #     topic_word_dict[k] = res_str
    

    def single_infer(doc):  # doc: list of words
        doc_inst = model.make_doc(doc)
        topic_dist, ll = model.infer(doc_inst)
        # print("".join(doc))
        # print('--------')
        top_3_topic = [(index, prob) for index, prob in sorted(list(enumerate(topic_dist)), key=lambda x:x[1], reverse=True)][:3]
        return top_3_topic

    for csv_file in os.listdir('dataset/split_by_dynasty_csv'):
        if os.path.exists(f'dataset/split_by_dynasty_csv_with_topic/{csv_file}'):
            continue
        lines = open(f'dataset/segmented/{csv_file[:-4]}.txt', 'r', encoding='utf-8').readlines()
        df = pd.read_csv(f'dataset/split_by_dynasty_csv/{csv_file}')
        topic_col = []
        assert len(lines) == len(df)
        for row_index, row in tqdm(df.iterrows(), total=len(df)):
            line = lines[row_index]
            line = line.strip().split()
            line = [w for w in line if '□' not in w]
            if not line:
                topic_col.append('-')
                continue
            top_3_topic = single_infer(doc=line)
            topic_col.append(str(top_3_topic))
        df['topic_and_prob'] = topic_col
        df.to_csv(f'dataset/split_by_dynasty_csv_with_topic/{csv_file}')


if __name__ == '__main__':
    # seg_word_and_train_topic_model()
    inference()