<template>
  <div id="app">
    <Header />
    <SearchBar @search="fetchImages" :searchBarHeight="searchBarHeight" />
    <ImageGallery v-if="isGalleryVisible" :images="images" />
  </div>
</template>

<script>
import Header from './components/Header.vue';
import SearchBar from './components/SearchBar.vue';
import ImageGallery from './components/ImageGallery.vue';

export default {
  components: {
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
    }
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
