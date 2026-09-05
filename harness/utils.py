from pathlib import Path
from config import WORKDIR
def assistant_message_dict(message) -> dict:
    # 使用model_dump方法转换message对象为字典，排除值为None的项
    data = message.model_dump(exclude_none=True)
    # 将字典中的'role'字段设置为'assistant'
    data['role'] = 'assistant'
    # 返回处理后的字典
    return data

def decode_subprocess_output(data: bytes |None) -> str:
    if not data:
        return ""
    for encoding in ('utf-8', 'gbk', 'cp936'):
        try:
            return data.decode(encoding)
        except UnicodeDecodeError:
            continue
    return data.decode("utf-8", error="replace")

def safe_path(p: str) -> Path:
    path = (WORKDIR / p).resolve()
    if not path.is_relative_to(WORKDIR):
        raise ValueError(f'路径超出工作区：{p}')
    return path