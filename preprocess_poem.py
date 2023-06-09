import os, sys
import re
import json
from tqdm import tqdm
import pandas as pd

def split_json():
    data = open('./dataset/poem/souyun_cleaned.json', 'r', encoding='utf-8').readlines()
    data = "".join(data)
    data = json.loads(data)
    for dynasty in data.keys():
        f = open(f'dataset/poem/split_by_dynasty/{dynasty}.json', 'w', encoding='utf-8')
        f.write(json.dumps(data[dynasty], ensure_ascii=False))
        f.close()
        
def is_chinese_char(origin_cp):
    cp = ord(origin_cp)
    if ((cp >= 0x4E00 and cp <= 0x9FFF) or  #
        (cp >= 0x3400 and cp <= 0x4DBF) or  #
        (cp >= 0x20000 and cp <= 0x2A6DF) or  #
        (cp >= 0x2A700 and cp <= 0x2B73F) or  #
        (cp >= 0x2B740 and cp <= 0x2B81F) or  #
        (cp >= 0x2B820 and cp <= 0x2CEAF) or
        (cp >= 0xF900 and cp <= 0xFAFF) or  #
        (cp >= 0x2F800 and cp <= 0x2FA1F) or  #
        (cp in [9633, 12289, 59482, 59457, 59433, 59434, 59439, 59449]) or  # '□', '、', '', '', '', '', '', ''
        (origin_cp in ['。', '，', '；', '：', '？', '！', '、'])):
        return True
    return False

def parse_json_to_table(input_path, output_path):
    output_data = {
        "writer": [],
        "label": [],
        "title": [],
        "content": [],
        "other": []
    }
    remove_chars = ['「', '“', '”', '」', '《', '》', '〃', '〔', '〕', '…', '○']
    to_square_chars = ['', '々', '', '◇', '●', 'ゼ', 'и', 'ね', 'Ё', 'び', '〇', 'ㄝ']
    def process_line(line):
        remark_pattern_1 = r'（([\s\S]+?)）'
        remark_pattern_2 = r'\(([\s\S]+?)\)'
        split_pattern = r'([。，；：？！])'
        for char in remove_chars:
            if char in line:
                # print(line)
                line = line.replace(char, '')
                # print(line)
        for char in to_square_chars:
            if char in line:
                line = line.replace(char, '□')
        for char in line:
            if not is_chinese_char(char):   # '□'算中文字符
                line = line.replace(char, '□')
        line = re.sub(pattern=remark_pattern_1, repl='', string=line)
        line = re.sub(pattern=remark_pattern_2, repl='', string=line)
        split_line = re.split(split_pattern, line)
        split_line = [l for l in split_line if l]
        # 把标点符号贴在后面
        split_line_stick_sep = [''.join(i) for i in zip(split_line[0::2], split_line[1::2])]
        return split_line_stick_sep
    def process_title(title):
        origin_title = title
        remark_pattern = r'（([^（）·]+?)）'
        dynasty_writer_pattern = r'（([^）]+?)·([^（]+?)）'
        for char in remove_chars:
            if char in title:
                title = title.replace(char, '')
        for char in to_square_chars:
            if char in title:
                title = title.replace(char, '□')
        title = re.sub(pattern=remark_pattern, repl='', string=title)
        m = re.search(pattern=dynasty_writer_pattern, string=title)
        if not m:
            print(origin_title)
        title_end, other_start = m.span()
        other_start += 1
        real_title = title[:title_end]
        other = ''
        if other_start < len(title):
            other = title[other_start:]
        return real_title, other
    
    data = open(input_path, 'r', encoding='utf-8').readlines()
    data = "".join(data)
    data = json.loads(data)
    for writer in tqdm(data.keys()):
        for poem in data[writer]:
            output_data['writer'].append(writer)
            output_data['label'].append(poem['label'])
            title = poem['title']
            title, other = process_title(title)
            output_data['title'].append(title)
            output_data['other'].append(other)
            content = []
            for line in poem['content']:
                content += process_line(line)
            output_data['content'].append(content)
    df = pd.DataFrame(output_data)
    df.to_csv(output_path)
        
def main():
    json_dir = 'dataset/split_by_dynasty_json'
    csv_dir = 'dataset/split_by_dynasty_csv'
    dynasty_names = os.listdir(json_dir)
    for n in dynasty_names:
        dynasty = n[:-5]
        parse_json_to_table(
            input_path=os.path.join(json_dir, n),
            output_path=os.path.join(csv_dir, f'{dynasty}.csv')
        )

if __name__ == '__main__':
    main()

