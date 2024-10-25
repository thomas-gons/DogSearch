<template>
    <div class="gallery" v-if="images.length > 0">
      <div 
        v-for="(image, index) in images" 
        :key="index" 
        class="image-container"
      >
        <img :src="image" alt="Dog Image" />
      </div>
    </div>
  </template>
  
  
  <script>
  export default {
    props: {
      images: {
        type: Array,
        default: () => []
      }
    }
  };
  </script>
  
  <style scoped>
  .gallery {
    display: flex;
    flex-wrap: wrap;
    gap: 1em;
    justify-content: center;
    background-color: #f4f4f4;
    border-radius: 8px;
  }
  
  .image-container {
    width: 150px;
    height: 150px;
    border: 1px solid #dde1e6;
    border-radius: 4px;
    overflow: hidden;
    box-shadow: 0px 4px 8px rgba(0, 0, 0, 0.1);
  }
  
  .image-container img {
    width: 100%;
    height: 100%;
    object-fit: cover;
  }
  </style>
  