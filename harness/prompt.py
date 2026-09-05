PROMPT_SECTION = {
  "identity": (
    f"你的一个编程Agent，直接行动，不要解释"
    f'所有破坏性操作需要用户批准。'
    f'开始多步骤任务前，先用 todo_write 规划步骤；执行过程中及时更新状态。'
  )
}
def get_system_prompt()->str:
    return PROMPT_SECTION["identity"]