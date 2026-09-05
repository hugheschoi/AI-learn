# -*- coding: utf-8 -*-
# 说明：从 collections 导入 defaultdict，用于统计字符对频率
from collections import defaultdict


# 定义SimpleBPE类
class SimpleBPE:
    # 构造函数
    def __init__(self):
        # 初始化词表，为字典类型（字符到id的映射）
        self.vocab = {}
        # 初始化合并规则，存储相邻字符对到新token的映射
        self.merges = {}
        # 初始化反向映射，token_id到token文本
        self.id_to_token = {}
        # 定义特殊结束标记
        self.end_token = "<|endoftext|>"

    # 训练BPE分词器的方法，参数为文本和合并次数
    def train(self, text, num_merges=100):
        """
        训练BPE分词器：学习合并频率最高的相邻字符对
        """
        print(f"\n【训练开始】语料: {text!r}，计划合并 {num_merges} 轮")

        # 从文本中提取所有唯一字符并排序（排除空格），作为初始字符集
        chars = sorted(c for c in set(text) if c != " ")

        # 初始化词表，将所有字符映射为id，然后加上特殊结束标记
        self.vocab = {i: char for i, char in enumerate(chars)}
        # 为特殊结束标记分配一个id
        self.vocab[len(self.vocab)] = self.end_token
        # 下一个可用的token id
        next_id = len(self.vocab)

        print(f"初始词表 (共 {len(self.vocab)} 项):")
        for token_id, token_str in self.vocab.items():
            print(f"  ID {token_id:>2} -> {token_str!r}")

        # 将每个单词拆成字符，作为 BPE 训练的初始 token 序列
        word_tokens = [self._tokenize_word(word) for word in text.split()]

        # 进行多次合并迭代
        merge_round = 0
        for _ in range(num_merges):
            # 统计所有词的相邻字符对出现频率
            pair_counts = defaultdict(int)
            # 遍历所有token序列
            for token_list in word_tokens:
                # 遍历当前token序列中的所有相邻对
                for i in range(len(token_list) - 1):
                    # 取相邻两个token组成pair
                    pair = (token_list[i], token_list[i + 1])
                    # 该pair对应频次加1
                    pair_counts[pair] += 1

            # 如果没有可统计的pair，提前结束
            if not pair_counts:
                print(f"【合并轮次 {merge_round + 1}】无可合并的字符对，训练提前结束")
                break

            merge_round += 1

            # 找出出现频率最高的pair
            best_pair = max(pair_counts, key=pair_counts.get)
            best_count = pair_counts[best_pair]

            # 生成一个新token，为best_pair两个字符串拼接
            new_token = best_pair[0] + best_pair[1]
            # 新token分配新id，并写入vocab
            self.vocab[next_id] = new_token
            # 新合并规则写入merges
            self.merges[best_pair] = next_id

            print(
                f"【合并轮次 {merge_round}】"
                f" {best_pair[0]!r}+{best_pair[1]!r} -> {new_token!r}"
                f" (ID: {next_id}, 频次: {best_count})"
            )

            # 用新token替换word_tokens中所有best_pair出现的位置
            new_word_tokens = []
            for token_list in word_tokens:
                # 新的token序列
                new_list = []
                # 遍历token_list中的元素
                i = 0
                while i < len(token_list):
                    # 如果当前位置和下一个正好是best_pair
                    if i < len(token_list) - 1 and (token_list[i], token_list[i + 1]) == best_pair:
                        # 合并到新token
                        new_list.append(new_token)
                        # 跳过合并的两个位置
                        i += 2
                    else:
                        # 否则，正常加入该token
                        new_list.append(token_list[i])
                        i += 1
                new_word_tokens.append(new_list)
            # 更新word_tokens为本轮后的结果
            word_tokens = new_word_tokens

            # 新的id自增
            next_id += 1

        # 训练结束后，构建反向映射：token文本->token_id
        self.id_to_token = {v: k for k, v in self.vocab.items()}

        print(f"\n【训练结束】实际合并 {len(self.merges)} 轮，最终 token 序列: {word_tokens}")
        print(f"最终词表 (共 {len(self.vocab)} 项):")
        for token_id in sorted(self.vocab.keys()):
            print(f"  ID {token_id:>2} -> {self.vocab[token_id]!r}")

    # 编码函数，将文本转为token id序列
    def encode(self, text):
        """
        编码：将文本转换为token IDs
        """
        print(f"\n【编码】文本: {text!r}")

        # 将文本按照空格分割为单词
        words = text.split()
        # 结果token id列表
        result = []

        # 遍历所有单词
        for word in words:
            # 把单词拆为字符序列
            token_list = list(word)

            # 应用所有合并规则直到不能再合并
            changed = True
            while changed:
                # 先假定本轮没有变化
                changed = False
                i = 0
                # 新的token序列
                new_list = []
                # 遍历当前token_list
                while i < len(token_list):
                    # 如果当前和下一个字符组成的pair在合并规则中
                    if i < len(token_list) - 1:
                        pair = (token_list[i], token_list[i + 1])
                        if pair in self.merges:
                            merged_token = self.vocab[self.merges[pair]]
                            # 用合并生成的新token替换
                            new_list.append(merged_token)
                            # 跳过两个字符
                            i += 2
                            # 本次有合并，改为True
                            changed = True
                            # 跳到下一轮
                            continue
                    # 否则，正常加入当前字符
                    new_list.append(token_list[i])
                    i += 1
                # 更新token_list为本轮合并后的结果
                token_list = new_list

            # 把最终token序列转为id
            for token in token_list:
                # 遍历词表，找到token对应的id
                for token_id, token_str in self.vocab.items():
                    if token_str == token:
                        result.append(token_id)
                        break

        # 加入结束标记id
        end_id = self.id_to_token.get(self.end_token, -1)
        result.append(end_id)

        print(f"Token IDs: {result}")

        # 返回token id列表
        return result

    # 解码函数，将token id列表还原为字符串
    def decode(self, token_ids):
        """
        解码：将token IDs还原为文本
        """
        print(f"\n【解码】输入 IDs: {token_ids}")

        # 用于存放解码后的token字符串
        tokens = []
        # 遍历输入的token id
        for token_id in token_ids:
            # 保证id在词表中
            if token_id in self.vocab:
                # 获取对应token文本
                token_str = self.vocab[token_id]
                # 跳过特殊结束标记
                if token_str != self.end_token:
                    tokens.append(token_str)

        # 拼接返回最终字符串
        decoded = "".join(tokens)
        print(f"解码结果: {decoded!r}")
        return decoded

    # 把单词拆分成字符数组的辅助方法
    def _tokenize_word(self, word):
        """将单词拆分为字符"""
        # 直接按字符转为列表
        return list(word)


# ===================== 使用示例 =====================

# 定义demo方法进行功能演示
def main():
    bpe = SimpleBPE()

    corpus = "hello world hello hello world"
    bpe.train(corpus, num_merges=50)

    text = "hello world"
    token_ids = bpe.encode(text)

    tokens = [
        bpe.vocab[token_id]
        for token_id in token_ids
        if token_id in bpe.vocab and bpe.vocab[token_id] != "<|endoftext|>"
    ]
    decoded = bpe.decode(token_ids)

    print("\n【汇总结果】")
    print(f"文本: {text!r}")
    print(f"Token IDs: {token_ids}")
    print(f"Token 字符串: {tokens}")
    print(f"解码后: {decoded!r}")
    print(f"\n全部 {len(bpe.merges)} 条合并规则:")
    for (left, right), token_id in bpe.merges.items():
        print(f"  {left!r} + {right!r} -> {bpe.vocab[token_id]!r} (ID: {token_id})")


# 说明：判断是否以主程序方式运行
if __name__ == "__main__":
    # 说明：调用演示函数
    main()
