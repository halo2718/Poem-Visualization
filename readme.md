# 中国古代诗词数据可视化

## 数据预处理
### 主题提取
对应`preprocess_poem.py`和`lda.py`。
1. 将json数据提取为csv
2. 使用[DeepTHULAC](https://github.com/thunlp/DeepTHULAC)对古诗词数据进行分词
3. 使用[tomotopy](https://bab2min.github.io/tomotopy/v0.12.2/en/)基于分词后的数据学习LDA主题模型
	* 由于不同朝代诗词数量差距较大（例如明代诗词有26余万首，而大部分朝代的诗词数量都在几千、几万首量级），为了避免某个年代对主题有过大的影响，我们对于存在超过6万首诗词的朝代随机抽取其中的6万首诗词
4. 使用学到的LDA主题模型对每首诗词进行分析，获得其对应的top-3主题及对应概率
### 意象抽取
按词频？