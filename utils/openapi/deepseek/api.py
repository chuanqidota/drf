from openai import OpenAI


# pip3 install openai

class DeepSeekApi:
    def __init__(self, api_key, system):
        self.base_url = "https://api.deepseek.com"  # deepseek的ip地址
        self.messages = self.__set_system(system)  # 系统的能力
        self.client = OpenAI(api_key=api_key, base_url=self.base_url)

    @staticmethod
    def __set_system(system):
        """
            设置第一次的信息
        :param system:
        :return:
        """
        messages = [{"role": "system", "content": system}]
        return messages

    def chat(self):
        """
            聊天
        :return:
        """
        print("欢迎使用,退出输入: exit")
        while True:
            # 获取用户输入
            user_input = input("你: ")
            if user_input.lower() == "exit":  # 如果用户输入 "exit"，结束对话
                print("感谢使用再见!")
                break

            # 将用户输入添加到对话历史
            self.messages.append({"role": "user", "content": user_input})

            # 调用 API 获取助手回复（流式）
            response = self.client.chat.completions.create(
                model="deepseek-chat",
                messages=self.messages,
                stream=True  # 启用流式响应
            )

            # 逐步打印助手回复
            print("助手: ", end="", flush=True)  # 打印前缀，不换行
            assistant_reply = ""
            for chunk in response:
                if chunk.choices[0].delta.content:  # 检查是否有内容
                    content = chunk.choices[0].delta.content
                    print(content, end="", flush=True)  # 逐步打印内容
                    assistant_reply += content  # 将内容拼接到完整回复中
            print()
            # 将助手回复添加到对话历史
            self.messages.append({"role": "assistant", "content": assistant_reply})


if __name__ == '__main__':
    apikey = "sk-9b1b34a012174a39b1159524632be9ce"
    system = "擅长各类编程语言，能快速解决各种编程问题"
    api = DeepSeekApi(apikey, system)
    api.chat()
