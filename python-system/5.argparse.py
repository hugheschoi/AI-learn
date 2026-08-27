import argparse

parser = argparse.ArgumentParser(description="我的命令行工具")
parser.add_argument("name")                    # 位置参数：必填
parser.add_argument("--age", type=int)         # 可选参数：--age 18
parser.add_argument("-v", "--verbose", action="store_true")  # 布尔开关
# 添加必需的位置参数 filename
parser.add_argument('filename', help='要处理的文件名')

args = parser.parse_args()
print(args.name, args.age, args.verbose, args.filename)

# uv run 5.argparse.py 张三 --age 18 -v