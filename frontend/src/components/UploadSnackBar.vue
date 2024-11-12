<template>
  <div class="upload-snackbar">
    <transition-group name="snackbar" tag="div" id="snackbar-content">
      <div
        v-for="container in containersToProcess"
        :key="container.id"
        class="progress-container"
        :style="{ width: dynamicWidth }"
      >
        <svg class="progress-circle" width="40" height="40" viewBox="0 0 40 40">
          <!-- Cercle de fond vert -->
          <circle
            class="progress-background"
            cx="20"
            cy="20"
            r="13"
            :stroke-width="stroke_width"
            stroke="#71D256"
            fill="none"
          ></circle>

          <!-- Cercle de progression -->
          <circle
            class="progress-bar"
            :class="{ 'completed': container.progress >= 100 }"
            cx="20"
            cy="20"
            r="13"
            :stroke-width="stroke_width"
            stroke="#71D256"
            fill="none"
            :stroke-dasharray="circumference"
            :stroke-dashoffset="circumference - (circumference * container.progress) / 100"
            transform="rotate(-90 20 20)"
          ></circle>

          <g v-if="container.progress >= 100" class="check-icon" transform="translate(8, 8)">
            <path
              d="M7 12l3 3 7-7"
              :stroke-width="stroke_width"
              fill="none"
              stroke-linecap="round"
              stroke-linejoin="round"
            />
          </g>
        </svg>

        <span class="text">
          Uploading #{{ container.id }} - {{ Math.round(container.progress) }}%
          ({{ container.elapsedTime }}s)
        </span>
      </div>
    </transition-group>
  </div>
</template>

<script>
import { useUploadQueueStore } from '@/stores/uploadQueue'
import { onMounted, onUnmounted, reactive } from "vue";

export default {
  setup() {
    const uploadQueueStore = useUploadQueueStore()
    const containersToProcess = uploadQueueStore.containersToProcess

    const maxId = uploadQueueStore.lastContainerId.toString()
    const dynamicWidth = 275 + (10 * (maxId.length - 1))
    const stroke_width = 2.75
    const radius = 13
    const circumference = 2 * Math.PI * radius

    const updateElapsedTime = () => {
      containersToProcess.forEach(container => {
        if (container.status === "processing") {
          container.elapsedTime = (new Date(Date.now() - container.uploadAt)).toLocaleString(navigator.language, {
            minute: "2-digit",
            second: "2-digit"
          })
        }
      })
    }

    let intervalId
    onMounted(() => {
      intervalId = setInterval(updateElapsedTime, 1000)
    })

    onUnmounted(() => {
      clearInterval(intervalId)
    })

    return { containersToProcess, stroke_width, circumference, dynamicWidth }
  }
}
</script>

<style scoped>
.upload-snackbar {
  position: fixed;
  right: 0;
  bottom: 0;
  z-index: 10;
  padding: 20px;
}

#snackbar-content {
  display: flex;
  flex-direction: column-reverse;
}

.progress-container {
  display: flex;
  align-items: center;
  background: #eee;
  border-radius: 10px;
  margin: 2px;
  height: 60px;
  transition: transform 0.8s ease, opacity 0.6s ease;
}

.progress-background {
  stroke: #e6e6e6;
}

.progress-circle {
  margin-left: 10px;
}

.progress-bar {
  stroke: var(--primary-color);
  stroke-linecap: round;
  transition: all 0.8s ease;
}

.progress-bar.completed {
  stroke: #6ec355
}

.check-icon path {
  stroke: #6ec355;
  transition: all 0.5s ease-in;
  transition-delay: 2s;
}

.text {
  margin-left: 8px;
  margin-right: 20px;
  font-family: inherit;
  color: var(--placeholder-color);
  font-size: 15px;
}

.snackbar-enter-active, .snackbar-leave-active {
  transition: transform 0.8s ease, opacity 0.6s ease;
}

.snackbar-enter, .snackbar-leave-to {
  opacity: 0;
  transform: translateX(100%);
}
</style>
