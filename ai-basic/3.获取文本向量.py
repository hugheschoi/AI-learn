# 导入 os，用于设置环境变量
import os
# 从 sentence_transformers 导入 SentenceTransformer
from sentence_transformers import SentenceTransformer

# model_name = "all-MiniLM-L6-v2"

# 加载本地 Embedding 模型（首次运行会自动下载）
model = SentenceTransformer('/Users/caizhuangbing/.cache/huggingface/hub/models--sentence-transformers--paraphrase-multilingual-MiniLM-L12-v2')

# 指定要转成向量的文本
text = "苹果是一种甜甜的水果"

# 编码为向量（numpy 数组）
vector = model.encode(text)

# 打印文本、向量维度和前 5 个数字
print(f"文本: {text}")
print(f"向量维度: {len(vector)}")
print(f"前 5 维: {vector[:5].tolist()}")