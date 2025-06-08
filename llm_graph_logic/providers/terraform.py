import asyncio
import json
import re
from pathlib import Path
from typing import Any

from llm_graph_logic.internal.enum import EdgeType, InfoType, NodeType
from llm_graph_logic.internal.graph import Edge, Graph, Node, NodeNop
from llm_graph_logic.internal.info_provider import InfoProvider

semaphore = asyncio.Semaphore(5)
TERRAFORM_INIT_CMD = ["terraform", "init"]
TERRAFORM_PROVIDERS_SCHEMA_CMD = ["terraform", "providers", "schema", "--json"]


class TerraformInfoProvider(InfoProvider):
    def __init__(self, projectPath: Path) -> None:
        super().__init__(InfoType.TERRAFORM_PROVIDER)
        self.providerRegex = re.compile(r"^([^_]+)_(.+)$")
        self.blockTypeRegex = re.compile(r"(\w+)\.(\w+)")
        self.providerStore: dict[str, Any] = {}
        self.projectPath: Path = projectPath
        self.providersMap: dict[str, str] = {}

    async def initProject(self) -> None:
        async with semaphore:
            process = await asyncio.create_subprocess_exec(
                *TERRAFORM_INIT_CMD,
                cwd=str(self.projectPath),
                stdout=None,
            )
            await process.communicate()

    async def getProviderSchema(self) -> dict[str, Any]:
        async with semaphore:
            process = await asyncio.create_subprocess_exec(
                *TERRAFORM_PROVIDERS_SCHEMA_CMD,
                cwd=str(self.projectPath),
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
            stdout, stderr = await process.communicate()

            if process.returncode != 0:
                print(f"Error running terraform providers schema in {self.projectPath}:")
                print(stderr.decode())
                return {}

            return json.loads(stdout.decode())

    async def preTerraformInit(self) -> None:
        await self.initProject()
        self.providerStore = await self.getProviderSchema()
        self.providersMap = {
            key.split("/")[-1]: key
            for key in self.providerStore.get("provider_schemas", {}).keys()
        }

    def getProviderBlock(self, provider: str) -> dict[str, Any] | None:
        provider_key = self.providersMap[provider]
        return (
            self.providerStore.get("provider_schemas", {})
            .get(provider_key, {})
            .get("provider", {})
            .get("block")
        )


    def getResourceBlock(self, provider: str, resource: str) -> dict[str, Any] | None:
        provider_key = self.providersMap[provider]
        return (
            self.providerStore.get("provider_schemas", {})
            .get(provider_key, {})
            .get("resource_schemas", {})
            .get(resource, {})
            .get("block")
        )


    def getDataSourceBlock(self, provider: str, source: str) -> dict[str, Any] | None:
        provider_key = self.providersMap[provider]
        return (
            self.providerStore.get("provider_schemas", {})
            .get(provider_key, {})
            .get("data_source_schemas", {})
            .get(source, {})
            .get("block")
        )

    async def mutateGraph(self, graph: Graph) -> Graph:
        await self.preTerraformInit()
        providerIDs = {}
        graphOldNodes = graph.nodes.copy()

        for id_, node in graphOldNodes.items():
            if node.subType_ != "resource" and node.subType_ != "data":
                continue
            match = self.blockTypeRegex.match(id_)
            if match:
                blockType = match.group(
                    1
                )  # например, из aws_instance.my_instance — это "aws_instance"
                blockIdentity = match.group(2)

                provider_match = self.providerRegex.match(blockType)
                if provider_match:
                    providerName = provider_match.group(1)  # например, "aws"
                    providerIDs[id_] = providerName

                    infoNodeID = f"info_block.terraform.{providerName}.{blockType}"
                    if node.subType_ == "resource":
                        newInfoNode = Node(
                            infoNodeID,
                            NodeType.TERRAFORM_PROVIDER_BLOCK,
                            "",
                            self.getResourceBlock(providerName, blockType),
                        )
                    elif node.subType_ == "data":
                        newInfoNode = Node(
                            infoNodeID,
                            NodeType.TERRAFORM_PROVIDER_BLOCK,
                            "",
                            self.getDataSourceBlock(providerName, blockType),
                        )
                    graph = graph.addNode(newInfoNode).addEdge(
                        Edge(newInfoNode, node, EdgeType.INFO)
                    )
                    for attributeName, value in (
                        newInfoNode.getData().get("attributes", {}).items()
                    ):
                        attributeNodeID = f"{blockType}.{blockIdentity}.{attributeName}"

                        attributeSubType = "optional"
                        if value.get("computed", False):
                            attributeSubType = "computed"
                        if value.get("required", False):
                            attributeSubType = "required"

                        newAttributeNode = Node(
                            attributeNodeID,
                            NodeType.TERRAFORM_PROVIDER_ATTRIBUTE,
                            attributeSubType,
                            value,
                        )
                        if (
                            newAttributeNode.getID() in graph.nodes
                            and graph.nodes[newAttributeNode.getID()].getType()
                            == NodeType.ATTRIBUTE
                        ):
                            oldAttributeNode = graph.nodes.get(newAttributeNode.getID(), NodeNop())
                            attributeNodeID = (
                                f"info_attribute.terraform.{attributeNodeID}"
                            )
                            newAttributeNode = newAttributeNode.setID(attributeNodeID)
                            graph = (
                                graph.addNode(newAttributeNode)
                                .addEdge(
                                    Edge(
                                        newAttributeNode,
                                        oldAttributeNode,
                                        EdgeType.INFO_ATTRIBUTE,
                                    )
                                )
                                .addEdge(
                                    Edge(
                                        newInfoNode,
                                        newAttributeNode,
                                        EdgeType.INFO_ATTRIBUTE,
                                    )
                                )
                            )
                        else:
                            graph = graph.addNode(newAttributeNode).addEdge(
                                Edge(
                                    newInfoNode,
                                    newAttributeNode,
                                    EdgeType.INFO_ATTRIBUTE,
                                )
                            )

        return graph
