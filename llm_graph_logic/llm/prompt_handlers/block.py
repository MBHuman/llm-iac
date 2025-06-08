
from llm_graph_logic.internal import Node, NodeType
from llm_graph_logic.internal.integrations.llm import NodePromptHandler, PromptNode


class BlockPromptHandler(NodePromptHandler):
    async def build_prompt(self, node: Node, related: list[Node], sub: list[Node]) -> PromptNode:
        processed = self.processor.getProcessedSubNodes(sub)
        promptNodes = related + processed
        prompt = f"""
You are acting as a **senior DevOps engineer** with deep expertise in Terraform and infrastructure-as-code validation.

Your task is to review a **Terraform block configuration** and:
- Identify **misconfigurations**, **bad practices**, or **risky patterns**
- Validate it against **provider requirements** and **business rules**
- Write ONLY about BAD practices you have seen

❗️Do not copy or restate the block as-is.  
Instead, analyze it like a real code review: look for **missing fields**, **risky values**, **non-scalable structures**, **security issues**, etc.

You can skip validation only if the block is clearly metadata (e.g., only `description` and `type` present). Otherwise, assume this block may affect production.

---

NOW DESCRIBE THE FOLLOWING BLOCK:

Block ID: {node.getID()}

"""
        promptNodes.sort(key=lambda n: str(n.getType()))
        prev = NodeType.EMPTY
        for pn in promptNodes:
            match pn.getType():
                case NodeType.TERRAFORM_PROVIDER_ATTRIBUTE:
                    if prev != NodeType.TERRAFORM_PROVIDER_ATTRIBUTE:
                        prompt += "\nTerraform provider documentation:\n"
                    prompt += f"- {pn.getID()} (required: {pn.getData().get('required', False)})\n"
                    prev = NodeType.TERRAFORM_PROVIDER_ATTRIBUTE
                case NodeType.BUSINESS_REQUIREMENT:
                    if prev != NodeType.BUSINESS_REQUIREMENT:
                        prompt += "\nBusiness requirements:\n"
                    prompt += f"- {pn.getData().get('description', '')}\n\n"
                    prev = NodeType.BUSINESS_REQUIREMENT
                case NodeType.ATTRIBUTE:
                    if prev != NodeType.ATTRIBUTE:
                        prompt += "\nRelated attributes:\n"
                    prompt += f"    Attribute ID: {pn.getID()}\n"
                    prompt += f"    Attribute Content: {pn.getData()}\n"
                    prev = NodeType.ATTRIBUTE
                case NodeType.BLOCK:
                    if prev != NodeType.BLOCK:
                        prompt += "\nRelated blocks:\n"
                    prompt += f"    Block ID {pn.getID()}\n"
                    prev = NodeType.BLOCK
                case NodeType.GENERATED_PROMPT:
                    if prev != NodeType.GENERATED_PROMPT:
                        prompt += "\nRelated prompts:\n"
                    if isinstance(pn, PromptNode):
                        prompt += f"   Node ID : {pn.getID()}"
                        prompt += f"   Response Text : {pn.getText()}\n\n"
                    prev = NodeType.GENERATED_PROMPT
        return PromptNode(node.getID(), "", prompt=prompt)