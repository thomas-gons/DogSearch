<template>
  <div id="app">
    <Header/>
    <SearchBar @search="fetchImages" :searchBarHeight="searchBarHeight"/>
    <ImageGallery v-if="isGalleryVisible" :images="images"/>
    <UploadSnackBar/>
  </div>
</template>

<script>
import Header from './components/Header.vue';
import SearchBar from './components/SearchBar.vue';
import ImageGallery from './components/ImageGallery.vue';

import {useUploadQueueStore} from '@/stores/uploadQueue'
import axios from "axios";
import UploadSnackBar from "@/components/UploadSnackBar.vue";

export default {
  setup() {
    const uploadQueueStore = useUploadQueueStore()

    uploadQueueStore.$onAction((context) => {
      if (context.name === 'fillQueue') {

        context.after(() => {

          const isProcessing = uploadQueueStore.$state.containersToProcess
            .some(container => container.status === 'processing');

          if (!isProcessing) {
            processNextContainer()
          }
        })
      }
    })

    const processNextContainer = () => {

      const containerToProcess = uploadQueueStore.$state.containersToProcess
            .find(container => container.status === 'waiting');

      if (!containerToProcess) return;
      containerToProcess.status = 'processing';
      containerToProcess.batches.forEach(batch => {
        const formData = new FormData()
        batch.files.forEach(file => {
          formData.append("files", file)
        })

        const batch_size = batch.files.length

        axios.post("http://localhost:8000/api/uploadImages", formData)
          .then((response) => {
            containerToProcess.progress += Number(batch_size / containerToProcess.nImages * 100)
            if (Math.round(containerToProcess.progress) >= 100) {
              containerToProcess.progress = 100
              containerToProcess.status = 'completed';
              setTimeout(() => {
                uploadQueueStore.$state.containersToProcess.shift()
              }, 5000);
            }
          })
          .catch(error => {
            containerToProcess.status = 'failed';
          })
      })
      processNextContainer()
    }

    return {
      uploadQueueStore,
    };
  },
  components: {
    UploadSnackBar,
    Header,
    SearchBar,
    ImageGallery
  },
  data() {
    return {
      images: [],
      isGalleryVisible: false,
      searchBarHeight: '80vh'
    };
  },
  methods: {
    async fetchImages(query) {
      if (!query) {
        console.warn("Veuillez entrer une requête de recherche.");
        this.isGalleryVisible = false;
        this.searchBarHeight = this.isGalleryVisible ? '10vh' : '80vh';
        return;
      }

      const response = await fetch(`http://localhost:8000/api/findImagesForQuery/${query}`);

      if (!response.ok) {
        console.error("Erreur lors de la récupération des images.");
        this.isGalleryVisible = false;
        this.searchBarHeight = this.isGalleryVisible ? '10vh' : '80vh';
        return;
      }

      const data = await response.json();

      this.images = data;
      this.isGalleryVisible = this.images.length > 0;
      this.searchBarHeight = this.isGalleryVisible ? '10vh' : '80vh';
    },
  }
};
</script>

<style>
@import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Sans:wght@400;700&display=swap');

:root {
  --background-color: #f4f4f4;

  --primary-color: #3b79eb;
  --primary-color-dark: #2c6be0;
  --secondary-color: #f1f5fa;

  --text-color: #393939;
  --placeholder-color: #8d8d8d;
}

#app {
  font-family: 'IBM Plex Sans', Arial, sans-serif;
  text-align: center;
  color: var(--text-color);
  background-color: var(--background-color);
  margin: 0;
  padding: 0;
  min-height: 100vh;
  overflow: hidden;
}
</style>
