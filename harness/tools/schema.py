def _fn_tool(
  name: str, description:str,properties:dict,requried: list[str]
)-> dict:
  return {
    "type": "function",
    "function": {
      "name": name,
      "description": description,
      "parameters": {
        "type": "object",
        "properties": properties,
        "requried": requried,
      }
    }
  }

TOOLS = [
  _fn_tool("bash", "执行一条shell命令", { "command": { "type": "string" } }, ["command"]),
  _fn_tool('read_file', '读取文件内容。', {'path': {'type': 'string'}, 'limit': {'type': 'integer'}}, ['path']),
  _fn_tool('write_file', '将内容写入文件。', {'path': {'type': 'string'}, 'content': {'type': 'string'}}, ['path', 'content']),
  _fn_tool('edit_file', '在文件中精确替换一段文本（仅替换一次）。', {'path': {'type': 'string'}, 'old_text': {'type': 'string'}, 'new_text': {'type': 'string'}}, ['path', 'old_text', 'new_text']),
  _fn_tool('glob', '按 glob 模式查找文件。', {'pattern': {'type': 'string'}}, ['pattern']),
  _fn_tool('todo_write', '创建并管理当前编码会话的任务列表。', {'todos': {'type': 'array', 'items': {'type': 'object', 'properties': {'content': {'type': 'string'}, 'status': {'type': 'string', 'enum': ['pending', 'in_progress', 'completed']}}, 'required': ['content', 'status']}}}, ['todos']),
]