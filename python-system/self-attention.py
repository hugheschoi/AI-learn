import math
def softmax(x):
    """Compute softmax values for each set of scores in x."""
    e_x = [math.exp(i) for i in x]
    sum_e_x = sum(e_x)
    return [i / sum_e_x for i in e_x]

def dot(a, b):
  return sum(x * y for x, y in zip(a, b))

words = ['猫', '追', '老鼠']
X = {
    '猫':   [1.0, 0.0, 1.0, 0.0],
    '追':   [0.0, 1.0, 0.0, 1.0],
    '老鼠': [1.0, 1.0, 0.0, 0.0],
}

d = 4
# 自注意力简化版：Q = K = V = X
# 第 1 步 + 第 2 步：计算点积分数并除以 sqrt(d) 缩放
score = {}
for wi in words:
    score[wi] = [dot(X[wi], X[wj]) / math.sqrt(d) for wj in words]

# 第 3 步：softmax 得到注意力权重（每行和为 1）
attn = {wi: softmax(score[wi]) for wi in words}

# 第 4 步：用权重加权求和 V，得到每个词的新表示
output = {}
for wi in words:
    output[wi] = [
        sum(attn[wi][k] * X[wj][j] for k, wj in enumerate(words))
        for j in range(d)
    ]

for wi in words:
    print(wi, '的注意力权重:',
          {wj: round(a, 3) for wj, a in zip(words, attn[wi])})