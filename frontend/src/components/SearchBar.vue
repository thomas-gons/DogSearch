<template>
    <div id="search-bar" :style="{ height: searchBarHeight }">
      <input 
        type="text" 
        v-model="query" 
        placeholder="Rechercher une race de chien..." 
        @keyup.enter="search"
      />
      <button @click="search">Rechercher</button>
    </div>
  </template>
  
  <script>
  export default {
    props: {
        searchBarHeight: {
            type: String,
            required: true
        }
    },
    data() {
      return {
        query: '',
      };
    },
    methods: {
      search() {
        this.$emit('search', this.query);
      }
    }
  };
  </script>
  
  <style scoped>
  #search-bar {
    display: flex;
    height: 80px;
    justify-content: center;
    align-items: center;
    margin: 1em;
    transition: height 0.5s ease-out;
  }
  input[type="text"] {
    width: 75%;
    padding: 0.625em 0.8em 0.625em;
    font-size: 1.1em;
    font-family: inherit;
    margin-right: 0.5em;
    border: 1px solid #dde1e6;
    color: var(--text-color);
    background-color: var(--background-color);
    border-radius: 0.5em;
    outline: none;
  }
  input[type="text"]::placeholder {
    color: var(--placeholder-color);
  }
  button {
    padding: 0.625em .8em 0.625em; 
    font-size: 1em;
    color: var(--secondary-color);
    background-color: var(--primary-color);
    font-family: inherit;
    border: none;
    border-radius: 0.5em;
    cursor: pointer;
  }
  button:hover {
    background-color: var(--primary-color-dark);
  }
  </style>
  