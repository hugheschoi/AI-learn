from agent import agent_loop
from hooks import trigger_user_prompt_hooks


def main():
    print("输入问题，回车发送，输入q退出")
    history = []
    while True:
        try:
            query = input(">>")
        except (EOFError, KeyboardInterrupt):
            break
        if query.strip().lower() in ["q", "quit", "exit"]:
            break
        # 触发 UserPromptSubmit 钩子，进行前置处理，返回处理后的用户输入
        query = trigger_user_prompt_hooks(query)
        history.append({"role": "user", "content": query})
        agent_loop(history)
        final = history[-1]
        if final.get("role") == "assistant" and final.get("content") is not None:
            print(final["content"])

if __name__ == "__main__":
    main()