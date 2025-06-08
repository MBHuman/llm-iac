<script setup>
import { useCounterStore } from '@/stores/counter';


const counter = useCounterStore();
</script>

<template>
    <button @click="counter.increment()">
        Current Count: {{ counter.count }}
    </button>
</template>