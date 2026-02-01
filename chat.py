from time import time
from enum import StrEnum
from openai import OpenAI
from dotenv import load_dotenv


class OpenAIModel(StrEnum):
    gpt_4o_mini = "gpt-4o-mini"


class OpenAIRole(StrEnum):
    user = "user"
    assistant = "assistant"
    system = "system"


def ts():
    return int(time())


class OpenAIMessage:
    def __init__(self, role: OpenAIRole, content: str | None = None):
        self.role = role
        self.content = content
        self.time = ts()

    def to_chat(self) -> dict:
        return {"role": self.role, "content": self.content}

    def to_text(self) -> str:
        return f"[{self.time}] {self.role}:\n{self.content}"


class OpenAIChat:
    def __init__(self, client: OpenAI):
        self.client: OpenAI = client
        self.history: list[OpenAIMessage] = []
        self.model: OpenAIModel | None = None

    def start(self, model: OpenAIModel):
        self.history = []
        self.model = model

    def push(self, message: OpenAIMessage):
        self.history.append(message)

    def send(self, message: OpenAIMessage):
        if self.model is None:
            raise RuntimeError("must define a model")
        self.history.append(message)
        resp = self.client.chat.completions.create(model=self.model, messages=[m.to_chat() for m in self.history])
        resp_text = resp.choices[0].message.content
        chat_message = OpenAIMessage(role=OpenAIRole.assistant, content=resp_text)
        self.history.append(chat_message)
        return chat_message

    def end(self, dump: bool = False):
        if not dump:
            return
        with open(f"{ts()}.chat.log", "w") as f:
            f.write("\n\n".join([m.to_text() for m in self.history]))


def main():
    load_dotenv()
    dump_on_end = True
    chat = OpenAIChat(OpenAI())
    chat.start(model=OpenAIModel.gpt_4o_mini)
    system_input = input("system message:\n")
    if system_input:
        chat.push(OpenAIMessage(role=OpenAIRole.system, content=system_input))
    print("\n\n")
    while True:
        user_input = input("user message:\n")
        print("\n\n")
        if user_input:
            user_message = OpenAIMessage(role=OpenAIRole.user, content=user_input)
            chat_message = chat.send(user_message)
            print(f"assistant message:\n{chat_message.content}\n\n")
        else:
            chat.end(dump=dump_on_end)
            break


if __name__ == "__main__":
    main()
