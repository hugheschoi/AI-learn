# 导入 glob 模块
import glob

# 查找当前目录下所有 .txt 文件
files = glob.glob("*.txt")
# 打印匹配结果列表，如 ['notes.txt', 'data.txt']
print(files)


# iglob 返回迭代器，适合文件数量很多时逐条处理
for path in glob.iglob("**/*.py", recursive=True):
    print(path)