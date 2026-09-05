from collections import defaultdict
# 定义语料，每个句子中的词和标点由空格分隔
corpus = [
    "天气 预报 说 长沙 明天 有 暴雨 。",
    "出门 请 携带 雨具 。",
    "这里 是 一座 历史悠久 的 美丽 城市 。",
    "大雨 在 下午 停了 ， 太阳 出来 了 。",
    "后天 大部分 地区 晴朗 温暖 。",
    "强降雨 可能 造成 低洼 地区 洪涝 。",
    "国王 的 女儿 善良 勇敢 。",
    "公主 住 在 森林 附近 的 城堡 里 。",
    "很久 以前 一位 国王 住 在 遥远 的 国度 。",
    "她 每天 喜欢 读书 和 学习 新 知识 。",
]

# 定义分词函数，用于将句子按空格分割为词列表
def split_words(sentence):
    # 按空格分割句子，返回词列表
    return sentence.split()

words_per_sentence = [split_words(sentence) for sentence in corpus]

# print("分词结果:", words_per_sentence)

# 构建一个集合，用于收集语料中出现过的所有词（去除重复）
vocabulary = set()
for sentence in words_per_sentence:
    for word in sentence:
        vocabulary.add(word)

# print("词汇表:", vocabulary)

# 构建相邻词出现次数统计：pair_count[当前词][下一个词] = 出现次数
pair_count = defaultdict(lambda: defaultdict(int))

# 遍历所有分词句子
for words in words_per_sentence:
    # 遍历句子中的每对相邻词
    for i in range(len(words) - 1):
        # 取出当前词
        current_word = words[i]
        # 取出下一个词
        next_word = words[i + 1]
        # 当前词到下一个词的转移次数加一
        pair_count[current_word][next_word] += 1


# 构建下一个词的条件概率表：next_word_prob[当前词][下一个词]=概率
next_word_prob = {}
# 遍历每个当前词及其统计映射
for current_word, count_map in pair_count.items():
    print(f"当前词: {current_word}")
    print(f"下一个词的出现次数: {count_map}")
    # 统计所有下一个词的出现次数之和
    total = sum(count_map.values())
    # 计算各下一个词的概率，组成一个新的字典
    next_word_prob[current_word] = {
        word: count / total for word, count in count_map.items()
    }

# print("下一个词的条件概率表:", next_word_prob)

def predict_next_word(current_word):
     prob_map = next_word_prob.get(current_word)
     if not prob_map:
          return None
    #  返回概率最高的下一个词
     return max(
         prob_map.items(),
         key=lambda item: -item[1]
      )[0]
def join_words(words):
    return " ".join(words)

def complete_sentence(first_word):
    if first_word not in vocabulary:
        raise ValueError(f"首词「{first_word}」不在语料词表中")
    generated_words = [first_word]
    current_word = first_word
    while True:
        # 预测下一个词
        next_word = predict_next_word(current_word)
        if next_word is None:
            break
        # 将下一个词加入已生成词列表
        generated_words.append(next_word)
        # 更新当前词为刚刚得到的下一个词
        current_word = next_word
    return join_words(generated_words)

first_word = "后天"
result_sentence = complete_sentence(first_word)
print(f"生成文本: {result_sentence}")