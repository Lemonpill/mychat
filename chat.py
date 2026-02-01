from time import time
from enum import StrEnum
from openai import OpenAI
from dotenv import load_dotenv


END_WORD = "end"


class OpenAIModel(StrEnum):
    gpt_4o_mini = "gpt-4o-mini"


def ts():
    return int(time())


class OpenAIMessage:
    def __init__(self, role: str, content: str):
        self.role = role
        self.content = content
        self.time = ts()

    def to_dict(self):
        return {"role": self.role, "content": self.content}

    def to_text(self):
        return f"[{self.time}] {self.role}:\n{self.content}"


class OpenAIChat:
    def __init__(self, client: OpenAI):
        self.client: OpenAI = client
        self.converstation: list[OpenAIMessage] = []
        self.model: OpenAIModel | None = None

    def new(self, model: OpenAIModel):
        print(f"OpenAIChat.new: model={model}")
        self.converstation = []
        self.model = model

    def say(self, thing: str):
        print(f"OpenAIChat.say: thing={thing}")
        if self.model is None:
            raise RuntimeWarning("must define a model")
        user_message = OpenAIMessage(role="user", content=thing)
        self.converstation.append(user_message)
        resp = self.client.chat.completions.create(model=self.model, messages=[m.to_dict() for m in self.converstation])
        resp_text = resp.choices[0].message.content
        chat_message = OpenAIMessage(role="assistant", content=resp_text)
        self.converstation.append(chat_message)
        return resp_text

    def end(self):
        with open(f"{ts()}.chat.log", "w") as f:
            f.write("\n\n".join([m.to_text() for m in self.converstation]))
        print("OpenAIChat.end")


def main():
    load_dotenv()
    chat = OpenAIChat(OpenAI())
    chat.new(model=OpenAIModel.gpt_4o_mini)
    while True:
        thing = input("user said:\n")
        if thing == END_WORD:
            chat.end()
            break
        compl = chat.say(thing)
        print(f"chat said:\n{compl}")


if __name__ == "__main__":
    main()
