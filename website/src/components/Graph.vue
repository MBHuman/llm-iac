<script setup>
</script>

<template>
    <h2>Terraform Dependency Tree (Vis.js)</h2>
    <div id="info-panel">
      <h3>Детали узла</h3>
      <p id="node-details">Выберите узел для просмотра деталей.</p>
    </div>

    <div class="network" id="full-graph"></div>
    <div class="network" id="tree-graph"></div>

    <div id="legend" style="display: none;">
      <h3>Легенда</h3>
      <ul>
        <li><span class="legend-node resource"></span> Resource</li>
        <li><span class="legend-node data"></span> Data</li>
        <li><span class="legend-node output"></span> Output</li>
        <li><span class="legend-edge"></span> Зависимость</li>
      </ul>
    </div>
</template>