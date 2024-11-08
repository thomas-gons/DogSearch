import {defineStore} from 'pinia'

export const useUploadQueueStore = defineStore('uploadQueue', {
  state: () => ({
    containersToProcess: []
  }),

  actions: {
    async fillQueue(files) {
      const aFiles = Array.from(files)
      const batches = []
      const size = 5

      const containerId = crypto.randomUUID(); // Exemple d'ID unique

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
        "status": "waiting"
      }

      this.containersToProcess.push(uploadContainer)
    }
  }


})
