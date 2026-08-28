# 导入 Pandas，简写为 pd
import pandas as pd

# 用字典创建 DataFrame（键是列名，值是列数据）
df = pd.DataFrame({
    '姓名': ['小明', '小红', '小刚'],
    '数学': [85, 92, 78],
    '英语': [90, 88, 95]
})
# 打印整个表格
print(df)
# 计算数学列平均分
print("数学平均分:", df['数学'].mean())