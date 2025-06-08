import json

from llm_graph_logic.internal import Node, NodeType
from llm_graph_logic.internal.integrations.llm import NodePromptHandler, PromptNode


class AttributePromptHandler(NodePromptHandler):
    async def build_prompt(self, node: Node, related: list[Node], sub: list[Node]) -> PromptNode:
        processed = self.processor.getProcessedSubNodes(sub)
        promptNodes = related + processed
        prompt = f"""
You are a senior DevOps engineer auditing Terraform infrastructure.

Your current task is to review a **single attribute** inside a resource or block.  
⚠️ You must analyze this attribute **in isolation** — do not assume the presence of other fields or external resources.

- Write ONLY about BAD practices you have seen

✅ Focus on:
- Hardcoded values
- Missing validation
- Use of variables or outputs
- Potential security issues in this specific attribute

🚫 Avoid:
- Assuming full resource structure
- Making guesses about unrelated fields
- Repeating the input

---

**Attribute to review** 
NOW DESCRIBE THE FOLLOWING ATTRIBUTE:

Attribute ID: {node.getID()}
Attribute Content: {json.dumps(node.getData())}

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
                    prompt += f"- {pn.getData().get('description', '')}\n"
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