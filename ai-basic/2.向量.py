# 导入numpy库，用于数值计算
import numpy as np

# 定义计算两个向量欧几里得距离的函数
def euclidean_distance(a, b):
    # """多行注释，描述函数功能"""
    """
    计算两个向量的欧几里得距离
    :param a: 一维list或numpy数组
    :param b: 一维list或numpy数组
    :return: 距离（float）
    """
    # 将输入a转换为numpy数组
    a = np.array(a)
    # 将输入b转换为numpy数组
    b = np.array(b)
    # 计算欧几里得距离并返回
    return np.sqrt(np.sum((a - b)**2))

# 示例

# 定义第一个向量
vec1 = [0,0]
# 定义第二个向量
vec2 = [3,4]
# 调用函数计算两个向量的欧几里得距离
distance = euclidean_distance(vec1, vec2)
# 打印欧几里得距离的结果
print(f"欧几里得距离: {distance}")



# 定义第一个向量
vec3 = np.array([1, 2])
# 定义第二个向量
vec4 = np.array([2, 3])

# 定义计算余弦相似度的函数
def cosine_similarity(a, b):
    # 计算两个向量的点积
    dot_product = np.dot(a, b)
    # 计算第一个向量的范数
    norm_a = np.linalg.norm(a)
    # 计算第二个向量的范数
    norm_b = np.linalg.norm(b)
    # 返回余弦相似度的计算结果 点积 ÷ (长度A × 长度B)
    return dot_product / (norm_a * norm_b)

# 调用余弦相似度函数计算vec3和vec4的相似度
similarity = cosine_similarity(vec3, vec4)
# 打印余弦相似度结果
print(f"余弦相似度: {similarity}")