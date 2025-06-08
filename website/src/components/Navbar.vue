<template>
  <div id="navbar">
    <h3>Панель управления</h3>

    <!-- Загрузка файла -->
    <p>Загрузите файл <code>vis_graph.json</code>:</p>
    <input @change="handleFileUpload" type="file" id="fileInput" accept=".json" />

    <p>Загрузите файл анализа узлов (node_analysis.json):</p>
    <input type="file" id="analysisInput" accept=".json" />

    <!-- Фильтры -->
    <div id="filters" style="display: none">
      <h4>Фильтры</h4>
      <label>
        <input type="checkbox" id="filterNodes" checked /> Показать узлы
      </label>
      <label>
        <input type="checkbox" id="filterEdges" checked /> Показать связи
      </label>
      <label>
        <input type="text" id="searchNode" placeholder="Поиск узла..." />
      </label>
    </div>

    <!-- Статистика -->
    <div id="stats" style="display: none">
      <h4>Статистика</h4>
      <p>Узлов: <span id="nodeCount">0</span></p>
      <p>Связей: <span id="edgeCount">0</span></p>
    </div>

    <!-- Настройки отображения -->
    <div id="settings" style="display: none">
      <h4>Настройки</h4>
      <label>
        Размер узлов:
        <input type="range" id="nodeSize" min="10" max="50" value="20" />
      </label>
      <label>
        Цвет фона:
        <input type="color" id="bgColor" value="#f4f6f8" />
      </label>
    </div>

    <!-- Кнопки действий -->
    <div id="controls" style="display: none">
      <button onclick="renderReverseTree()">
        Показать дерево зависимостей
      </button>
      <button onclick="renderFullGraph()">Показать весь граф</button>
    </div>
  </div>
</template>


<script setup>
import { useGraphStore } from '@/stores/graphStore';

const graphStore = useGraphStore()

const handleFileUpload = async (event) => {
  const file = event.target.files[0];
  if (!file) return

  const reader = new FileReader();
  reader.onload = (e) => {
    try {
      const fullData = JSON.parse(e.target.result);
      graphStore.loadGraphData(fullData);
    } catch (err) {
      console.log('Ошибка чтения JSON:', err);
    }
  };

  reader.readAsText(file);
}


</script>

<style scoped>
/* Sidebar Styling */
#navbar {
  display: flex;
  flex-direction: column;
  width: 280px; /* Увеличенная ширина для удобства */
  height: 100vh;
  background-color: #241F3A; /* Характерный тёмно-синий цвет HashiCorp */
  color: #E6E6E6; /* Светлый текст */
  padding: 20px;
  box-shadow: 2px 0 10px rgba(0, 0, 0, 0.1);
}

#navbar h3 {
  font-size: 1.4rem;
  color: #FF6B35; /* Акцентный оранжевый цвет HashiCorp */
  margin-bottom: 20px;
}

#navbar p {
  font-size: 0.9rem;
  color: #BDBDBD; /* Серый текст */
  margin-bottom: 20px;
}

#navbar input[type="file"] {
  display: block;
  padding: 10px;
  border: 1px solid #FF6B35; /* Акцентный оранжевый */
  border-radius: 5px;
  background-color: transparent;
  color: #FF6B35;
  cursor: pointer;
  transition: all 0.3s ease;
}

#navbar input[type="file"]:hover {
  background-color: #FF6B35;
  color: #fff;
}

#navbar label {
  display: flex;
  align-items: center;
  margin-bottom: 10px;
  font-size: 0.9rem;
  color: #E6E6E6;
}

#navbar input[type="checkbox"], 
#navbar input[type="range"], 
#navbar input[type="color"] {
  margin-left: 10px;
}

#controls {
  display: flex;
  margin-top: 2em;
  margin-bottom: 2em;
}

#navbar button {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 100%;
  padding: 10px;
  margin-bottom: 10px;
  border: none;
  border-radius: 5px;
  background-color: #FF6B35; /* Акцентный оранжевый */
  color: #fff;
  font-size: 0.9rem;
  cursor: pointer;
  transition: background-color 0.3s ease;
}

#navbar button:hover {
  background-color: #E65A25; /* Темнее оранжевый при наведении */
}
</style>
