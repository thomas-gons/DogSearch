import {defineStore} from 'pinia'


export const useUploadQueueStore = defineStore('uploadQueue', {

  state: () => ({
    containersToProcess: [],
    lastContainerId: 1,
  }),

  actions: {
    async fillQueue(files) {
      const aFiles = Array.from(files)
      const batches = []
      const size = 5

      const containerId = this.lastContainerId;

      for (let i = 0; i < files.length; i += size) {
        batches.push({
          "files": aFiles.slice(i, i + size),
        })
      }

      const uploadContainer = {
        "id": containerId,
        "batches": batches,
        "nImages": aFiles.length,
        "progress": 0,
        "status": "waiting",
        "uploadAt": Date.now(),
        "elapsedTime": "00:00"
      }

      this.containersToProcess.push(uploadContainer)
      this.lastContainerId++
    }
  }


})
