import { defineStore } from 'pinia'

export const useUploadQueueStore = defineStore('uploadQueue', {
  state: () => ({
    containersToProcess: []
  }),

  actions: {
    async fillQueue(files){
      const aFiles = Array.from(files)
      const batches = []
      const size = 5

      for (let i = 0; i < files.length; i += size) {
        batches.push({
          "files": aFiles.slice(i, i + size),
          "status": 'waiting'
        })
      }

      const uploadContainer = {
        "batches": batches,
        "progresss": 0,
      }

      this.containersToProcess.push(uploadContainer)
    }
  }


})
