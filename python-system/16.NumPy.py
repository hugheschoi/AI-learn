"""
# 导入 NumPy，简写为 np
import numpy as np

# 用列表创建一维数组
arr = np.array([1, 2, 3, 4, 5])
# 计算数组的平均值
average = np.mean(arr)
# 打印数组内容
print(f"数组: {arr}")
# 打印平均值
print(f"平均值: {average}")
"""
"""
# 导入 NumPy
import numpy as np

# 用列表创建一维数组
a = np.array([1, 2, 3])
# 打印一维数组
print("一维:", a)

# 用嵌套列表创建二维数组（2 行 2 列）
b = np.array([[1, 2], [3, 4]])
# 打印二维数组
print("二维:\n", b)

# 创建数组时指定 dtype 为浮点数
c = np.array([1, 2, 3], dtype=float)
# 打印浮点数组
print("浮点数组:", c)
"""
"""
# 导入 NumPy
import numpy as np

# 创建整数数组
arr = np.array([1, 2, 3])
# 查看数组的 dtype 类型
print("dtype:", arr.dtype)

# 用 astype 把整数数组转为浮点数
float_arr = arr.astype(float)
# 打印转换后的数组及其类型
print("转浮点:", float_arr, float_arr.dtype)

# 创建数组时直接指定为 float32 类型
f = np.array([1, 2, 3], dtype=np.float32)
# 打印 float32 数组的 dtype
print("float32:", f.dtype)
"""
"""
# 导入 NumPy
import numpy as np

# 用 arange 创建 0~11 共 12 个元素的一维数组
arr = np.arange(12)
# 查看原数组的 shape
print("原形状:", arr.shape)

# 把一维数组 reshape 成 3 行 4 列的二维数组
mat = arr.reshape(3, 4)
# 打印 reshape 后的数组
print("reshape 后:\n", mat)
# 打印新形状
print("新形状:", mat.shape)
# 打印维度数量 ndim
print("维度数 ndim:", mat.ndim)
# 打印元素总个数 size
print("元素总数 size:", mat.size)
"""
"""
# 导入 NumPy
import numpy as np

# 创建 3 行 4 列的全零矩阵
zeros = np.zeros((3, 4))
# 打印全零矩阵
print("zeros:\n", zeros)

# 创建 2 行 3 列的全一矩阵，类型为整数
ones = np.ones((2, 3), dtype=int)
# 打印全一矩阵
print("ones:\n", ones)

# 创建 3 阶单位矩阵（对角线为 1）
eye = np.eye(3)
# 打印单位矩阵
print("eye:\n", eye)

# 创建 2×2 数组，所有元素填充为 7
full = np.full((2, 2), 7)
# 打印 full 数组
print("full:\n", full)
"""
"""
# 导入 NumPy
import numpy as np

# arange：从 0 到 10（不含 10），步长 2
seq = np.arange(0, 10, 2)
# 打印 arange 结果
print("arange:", seq)

# linspace：在 1~10 之间均匀取 10 个点
points = np.linspace(1, 10, 10)
# 打印 linspace 结果
print("linspace:", points)

# linspace：在 0~2π 之间取 5 个点，模拟 x 轴
x = np.linspace(0, 2 * np.pi, 5)
# 打印 x 轴采样点
print("x 轴采样:", x)
"""
"""
# 导入 NumPy
import numpy as np

# 固定随机种子，每次运行结果一致
np.random.seed(42)

# 生成 2 行 3 列的 [0,1) 均匀分布随机数
rand = np.random.rand(2, 3)
# 打印随机浮点数组
print("rand:\n", rand)

# 生成 5 个 [1, 100) 范围内的随机整数
ints = np.random.randint(1, 100, size=5)
# 打印随机整数数组
print("randint:", ints)
"""
"""
import numpy as np
original_array = np.array([1, 2, 3, 4, 5, 6])
view_like = np.asarray(original_array)
copy_arr = np.array(original_array)
original_array[0] = 0
print("Original array:", original_array)
print("View-like array:", view_like)
print("Copy array:", copy_arr)
"""
"""
import numpy as np
arr = np.array([0, 1, 2, 3, 4, 5, 6, 7])
print(arr[3])  # 输出: 3
print(arr[2:5])  # 输出: [2 3 4]
print("arr[::2]:", arr[::2])  #步长为 2，隔一个取一个  输出: [0 2 4 6]
# 步长 -1，反转整个数组
print("arr[::-1]:", arr[::-1])
"""
# 导入 NumPy
import numpy as np

# 创建 0~11 并 reshape 为 3 行 4 列
arr = np.arange(12).reshape(3, 4)
# 打印原二维数组
print("原数组:\n", arr)
# 取第 2 行（索引 1）的所有列
print("第 2 行:", arr[1, :])
# 取第 3 列（索引 2）的所有行
print("第 3 列:", arr[:, 2])
# 取子矩阵：行 0~1，列 1~2
print("子矩阵:\n", arr[0:2, 1:3])