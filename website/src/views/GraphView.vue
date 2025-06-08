<template>
  <div id="graph-view">
    <div ref="networkContainer" class="graph-container"></div>
  </div>
</template>

<script setup>
import { ref, watch, onMounted } from "vue";
import { useGraphStore } from "@/stores/graphStore";
import * as vis from "vis-network/standalone";

// refs
const networkContainer = ref(null);
let network = null;

// store
const store = useGraphStore();

// функция для рендера графа
const renderGraph = () => {
  if (!store.fullData?.nodes || !store.fullData?.edges) return;

  const nodes = new vis.DataSet(store.fullData.nodes);
  const edges = new vis.DataSet(store.fullData.edges);

  const options = {
    layout: { improvedLayout: false },
    physics: { enabled: true, solver: "forceAtlas2Based" },
    interaction: { dragNodes: true, dragView: true, zoomView: true },
    edges: {
      arrows: { to: { enabled: true, scaleFactor: 1 } },
      color: { color: "#848484", highlight: "#ff0000" },
      smooth: { type: "dynamic" },
    },
  };

  if (network) {
    network.destroy(); // очищаем предыдущий граф
  }

  network = new vis.Network(networkContainer.value, { nodes, edges }, options);

  network.on("click", (params) => {
    if (params.nodes.length > 0) {
      const nodeID = params.nodes[0];
      store.setNodeToBuild(nodeID);
    } else {
      store.setNodeToBuild(null);
    }
  });
};

// следим за изменением store.fullData и рендерим граф
watch(
  () => store.fullData,
  () => {
    renderGraph();
  },
  { deep: true }
);

// если нужно отрисовать сразу при монтировании
onMounted(() => {
  if (store.fullData?.nodes) {
    renderGraph();
  }
});
</script>

<style scoped>
#graph-view {
  /* display: flex; */
  height: 100%;
  flex: 1;
}
.graph-container {
  height: 100%;
  flex: 1;
  /* border: 1px solid #ccc; */
}
</style>
