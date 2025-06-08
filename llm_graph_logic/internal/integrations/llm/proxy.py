import uuid

import openai

from llm_graph_logic.internal.enum import NodeType
from llm_graph_logic.internal.graph import Node


class PromptNode(Node):
    def __init__(
        self,
        nodeID: str,
        text: str,
        score: int = 0,
        error_comment: str = "",
        summary: str = "",
        prompt: str = "",
    ):
        nodeID = nodeID
        data = {
            "node_id": nodeID,
            "score": score,
            "error_comment": error_comment,
            "summary": summary,
            "prompt": prompt,
            "text": text,
        }
        super().__init__(nodeID, NodeType.GENERATED_PROMPT, "", data)

    def getScore(self) -> float:
        return self.getData().get("score", 0.0)
    
    def getText(self) -> str:
        return self.getData().get("text", "")

    def getPrompt(self) -> str:
        return self.getData().get("prompt", "")

    def getUpdated(self, resp: str) -> "PromptNode":
        return PromptNode(
            nodeID=self.getID(),
            text=resp,
            prompt=self.getPrompt(),
        )
    

class PromptNodeNop(PromptNode):
    def __init__(self) -> None:
        super().__init__(str(uuid.uuid4()), "")


class LLMProxy:

    def __init__(self) -> None:
        self.baseUrl = "http://localhost:8101/v1"
        self.modelName = "gpt4o"
        self.temperature = 0.8
        self.topP = 0.95
        self.maxTokens = 128
        self.secretKey = ""
        self.isAutoFix = False

    def setSecretKey(self, secretKey: str) -> "LLMProxy":
        self.secretKey = secretKey
        self.client = openai.AsyncOpenAI(api_key=self.secretKey, base_url=self.baseUrl)
        return self

    def setBaseURL(self, baseUrl: str) -> "LLMProxy":
        self.baseUrl = baseUrl
        self.client = openai.AsyncOpenAI(api_key=self.secretKey, base_url=self.baseUrl)
        return self

    def setModel(self, modelName: str) -> "LLMProxy":
        self.modelName = modelName
        return self

    def setTemperature(self, temperature: int) -> "LLMProxy":
        self.temperature = temperature
        return self

    def setTopP(self, topP: int) -> "LLMProxy":
        self.topP = topP
        return self

    def setMaxTokens(self, maxTokens: int) -> "LLMProxy":
        self.maxTokens = maxTokens

        return self

    async def callLLM(self, promptNode: PromptNode) -> PromptNode:
        response = await self.client.chat.completions.create(
            model=self.modelName,
            messages=[{"role": "user", "content": promptNode.getPrompt()}],
            temperature=self.temperature,
            top_p=self.topP,
            max_tokens=self.maxTokens,
        )
        content = response.choices[0].message.content

        return promptNode.getUpdated(content)