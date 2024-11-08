<template>
  <div class="upload-snackbar">
    <div class="snackbar-content">
      <div v-for="container in containersToProcess" :key="container.id" class="progress-container">
       <svg class="progress-circle" width="120" height="120" viewBox="0 0 120 120">
          <circle
            class="progress-background"
            cx="60"
            cy="60"
            r="25"
            stroke-width="5"
            fill="none"
          ></circle>
          <circle
            class="progress-bar"
            cx="60"
            cy="60"
            r="25"
            stroke-width="5"
            fill="none"
            :stroke-dasharray="circumference"
            :stroke-dashoffset="circumference - (circumference * container.progress) / 100"
            transform="rotate(-90 60 60)"
          ></circle>
          <text x="50%" y="55%" alignment-baseline="middle" text-anchor="middle" fill="#333">
            {{ Math.round(container.progress) }}%
          </text>
        </svg>
        <span>Uploading... {{ Math.round(container.progress) }}%</span>
      </div>
    </div>
  </div>
</template>
<script>

import {useUploadQueueStore} from '@/stores/uploadQueue'

export default {
  setup() {
    const uploadQueueStore = useUploadQueueStore()
    const containersToProcess = uploadQueueStore.containersToProcess

    const radius = 25;
    const circumference = 2 * Math.PI * radius;

    return {containersToProcess, circumference}
  }
}
</script>

<style scoped>
.upload-snackbar {
  padding: 20px;
}

.snackbar-content {
  display: flex;
  flex-direction: column;
}

.progress-container {
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  text-align: center;
}

.progress-background {
  stroke: #e6e6e6;
}

.progress-bar {
  stroke: var(--primary-color);
  stroke-linecap: round;
  transition: stroke-dashoffset 0.5s ease;
}

text {
  font-family: 'IBM Plex Sans', Arial, sans-serif;
  color: var(--placeholder-color);
  font-size: 14px;
}
</style>
