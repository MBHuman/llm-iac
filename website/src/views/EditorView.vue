<script setup>
import { VueMonacoEditor } from "@guolao/vue-monaco-editor";
import { ref } from "vue";
// import { MonacoEditor } from "@guolao/vue-monaco-editor";

const code = ref("// your code here");
</script>

<template>
  <VueMonacoEditor v-model:value="code" language="javascript" theme="vs-dark" />
</template>


