import vis from 'vis-network'

function renderReverseTree() {

}

function renderFull() {

}

function renderTree() {
    
}

function renderGraph(data, type) {
    const nodes = new vis.DataSet(data.nodes);
    const edges = new vis.DataSet(data.edges);

    const options = {
        layout: {
            improvedLayout: false,
        },
        physics: {
            enabled: true,
            solver: 'forceAtlas2Based',
        },
        interaction: {
            dragNodes: true,
            dragView: true,
            zoomView: true,
        },
        edges: {
            arrows: {
                to: {
                    enabled: true,
                    scaleFactor: 1,
                },
            },
            color: { color: "#848484", highlight: "#ff0000" },
            smooth: {
                type: "dynamic",
            },
        },
    };
}