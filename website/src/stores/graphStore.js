import { defineStore } from "pinia";

export const useGraphStore = defineStore('graph', {
    state: () => ({
        analysisData: {},
        fullData: {nodes: [], edges: []},
        noteToBuild: null
    }),
    getters: {
        nodeCount: state => state.fullData.nodes.length(),
        edgesCount: state => state.fullData.edges.length(),
    },
    actions: {
        loadGraphData(data) {
            this.fullData = data
        },
        loadAnalysisData(data) {
            this.fullData = Object.fromEntries(data.map(item => [item.node_id, item]));
        },
        setNodeToBuild(nodeID) {
            this.noteToBuild = nodeID;
        }
    }
})