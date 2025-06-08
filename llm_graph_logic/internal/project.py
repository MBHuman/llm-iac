import asyncio
import json
from pathlib import Path

from llm_graph_logic.internal.enum import NodeType
from llm_graph_logic.internal.graph import Graph
from llm_graph_logic.internal.integrations.llm.processor import LLMProcessor
from llm_graph_logic.internal.level import Level
from llm_graph_logic.internal.logic_processor import LogicProcessor
from llm_graph_logic.internal.parser import Parser
from llm_graph_logic.internal.results import Result, ResultPlotsBuilder, Results
from llm_graph_logic.internal.sorting import Sorting


class PostProjectProcessor:

    def __init__(self) -> None:
        pass

    def postProcess(self, result: Result) -> None:

        pass

class Project:
    def __init__(self, projectID: str):
        self.projectID: str = projectID
        self.parser: Parser | None = None
        self.llmProcessor: LLMProcessor | None = None
        self.logicProcessor: LogicProcessor | None = None
        self.postProcessor: PostProjectProcessor | None = None
        self.path: Path = Path("./")
        self.allowedTypes: list[NodeType] = []
        self.results: Results | None = None
        self.setAllowedTypes([NodeType.ATTRIBUTE, NodeType.BLOCK])
        self.setLogicProcessor(LogicProcessor())

    def getProjectID(self) -> str:
        return self.projectID

    def setPath(self, path: Path) -> "Project":
        self.path = path
        return self

    def setParser(self, parser: Parser) -> "Project":
        self.parser = parser
        return self

    def setLLMProcessor(self, llmProcessor: LLMProcessor) -> "Project":
        self.llmProcessor = llmProcessor
        return self

    def setLogicProcessor(self, logicProcessor: LogicProcessor) -> "Project":
        self.logicProcessor = logicProcessor
        return self

    def setAllowedTypes(self, allowedTypes: list[NodeType]) -> "Project":
        self.allowedTypes = allowedTypes
        return self

    def getResults(self) -> Results | None:
        return self.results

    def _calcTotal(self, levels: list[Level]) -> int:
        return sum(len(level) for level in levels)

    async def parse(self) -> Graph:
        if self.parser is None:
            raise RuntimeError("Parser is not set.")
        graph = await self.parser.parse(self.path)
        return graph.buildReverseEdges()

    async def process(self) -> None:
        if self.llmProcessor is None:
            raise RuntimeError("LLMProcessor is not set")
        if self.logicProcessor is None:
            raise RuntimeError("LogicProcessor is not set")
        graph = await self.parse()

        levels: list[Level] = Sorting().setAllowedTypes(self.allowedTypes).sort(graph)
        totalCnt = self._calcTotal(levels)
        computedCnt = 0
        subres: list[Result] = []

        for level in levels:
            res = await level.process(
                graph, self.llmProcessor, self.logicProcessor, computedCnt, totalCnt
            )
            computedCnt += len(level)
            subres.extend(res)

        self.results = Results(subres)

    def saveGraph2VisJS(self, path: Path) -> None:
        if self.parser is None:
            raise RuntimeError("Parser is not set.")
        visjs = self.parser.buildVisJSGraph()
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("w", encoding="utf-8") as f:
            json.dump(visjs, f, indent=2)

# class ProjectsGroup:

#     projectsGroupID: str
#     projects: list[Project]
#     projectsGroupProcessor: ProjectsGroupProcessor

#     def __init__(self, pgID: str):
#         self.projectsGroupID = pgID

#     def getProjectGroupID(self) -> str:
#         return self.projectsGroupID

#     def addProjects(self, projects: list[Project]) -> "ProjectsGroup":
#         self.projects.extend(projects)
#         return self

#     def setProjectsGroupProcessor(
#         self, projectsGroupProcessor: ProjectsGroupProcessor
#     ) -> "ProjectsGroup":
#         self.projectsGroupProcessor = projectsGroupProcessor
#         return self

#     async def process(self):
#         await self.projectsGroupProcessor(self)


# class ProjectNode(Node):

#     def __init__(self, project: Project):
#         super().__init__(project.getProjectID(), "", "", project)
#         self.data["metaType"] = NodeMetaType.PROJECT


# class ProjectsGroupNode(Node):

#     def __init__(self, projectsGroup: ProjectsGroup):
#         super().__init__(projectsGroup.getProjectGroupID(), "", "", projectsGroup)
#         self.data["metaType"] = NodeMetaType.PROJECTS_GROUP


class ProjectsProcessor:

    def __init__(
        self,
        projects: dict[str, Project],
        projectsGraph: Graph | None = None,
    ) -> None:
        self.projects = projects
        # self.projectsGraph = projectsGraph
        self.plotsBuilder: ResultPlotsBuilder = (
            ResultPlotsBuilder().setUseTitleForName()
        )

        # self.cache

    async def processProjects(self) -> None:
        # if self.projectsGraph is not None:
            # pass  # TODO добавить обработку projectsGraph перед тем как обрабатывать данные
        await asyncio.gather(
            *(project.process() for _, project in self.projects.items())
        )

    async def parseProjects(self) -> None:
        await asyncio.gather(*(project.parse() for _, project in self.projects.items()))

    # def createResultPlots(self) -> ResultPlots:
    #     for projectID, project in self.projects.items():
    #         x, y = project.getPlotData()
    #         self.plotsBuilder.add_plot(x, y, label=projectID, kind="bar").set_xlabel(
    #             "Количественная оценка качества"
    #         ).set_ylabel("Количество элементов")
    #     resultPlots = self.plotsBuilder.build()
    #     self.plotsBuilder = ResultPlotsBuilder().setUseTitleForName()
    #     return resultPlots

    def getAnalyzerResults(self, projectID: str) -> Results | None:
        project = self.projects.get(projectID)
        if project is None:
            raise KeyError(f"Project '{projectID}' not found in projects")
        return project.getResults()

    # def calcScore(self, projectID: str) -> float:
    #     project = self.projects.get(projectID)
    #     if project is None:
    #         raise KeyError(f"Project '{projectID}' not found in projects")
    #     return project.calcScore()



    def saveGraph2VisJS(self, projectID: str, path: Path) -> None:
        project = self.projects.get(projectID)
        if project is None:
            raise KeyError(f"Project '{projectID}' not found in projects")
        project.saveGraph2VisJS(path)

    # def saveGraphResults2VisJS(self, projectID: str, path: Path) -> None:
    #     project = self.projects.get(projectID)
    #     if project is None:
    #         raise KeyError(f"Project '{projectID}' not found in projects")
    #     project.saveResultsGraph2VisJS(path)


class ProjectsBuilder:

    def __init__(self) -> None:
        # self.projects: List[Project] = []
        self.projects: dict[str, Project] = {}
        # self.projectsGroups: Dict[str, ProjectsGroup] = {}
        # self.projectsGraph: Graph = Graph()

    def addProject(self, project: Project) -> "ProjectsBuilder":
        self.projects.setdefault(project.getProjectID(), project)
        # self.projectsGraph.addNode(ProjectNode(project))
        return self

    # def addProjectsGroup(
    #     self, groupID: str, projects: list[Project]
    # ) -> "ProjectsBuilder":
    #     projectsGroupNode = ProjectsGroupNode(ProjectsGroup(groupID))
    #     # self.projectsGroups.setdefault(groupID, ProjectsGroup(groupID))
    #     # self.projectsGroups[groupID].addProjects(projects)
    #     self.projectsGraph.addNode(projectsGroupNode)
    #     for project in projects:
    #         if project.getProjectID() in self.projectsGraph.nodes:
    #             projectNode = self.projectsGraph.nodes[project.getProjectID()]
    #             self.projectsGraph.addEdge(
    #                 Edge(projectsGroupNode, projectNode, EdgeType.PG_PROJECT)
    #             )
    #     return self

    # def linkProjects(
    #     self, sourceProject: Project, targetProject: Project
    # ) -> "ProjectsBuilder":
    #     if sourceProject not in self.projectsGraph.nodes:
    #         raise KeyError(
    #             f"failed to find source project {sourceProject.getProjectID()} in projects graph"
    #         )
    #     if targetProject not in self.projectsGraph.nodes:
    #         raise KeyError(
    #             f"failed to find source project {targetProject.getProjectID()} in projects graph"
    #         )
    #     sourceProjectNode = self.projectsGraph.nodes.get(sourceProject.getProjectID())
    #     targetProjectNode = self.projectsGraph.nodes.get(targetProject.getProjectID())
    #     self.projectsGraph.addEdge(
    #         Edge(sourceProjectNode, targetProjectNode, EdgeType.PROJECT_PROJECT)
    #     )
    #     return self

    def buildProcessor(self) -> ProjectsProcessor:
        return ProjectsProcessor(
            self.projects
        )
