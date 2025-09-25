<script setup lang="ts">
import { RouterLink, RouterView } from 'vue-router'
import HelloWorld from './components/HelloWorld.vue'

import { onMounted } from 'vue'

onMounted(async () => {
  const res = await fetch('/api/hello')
  const data = await res.json()
  console.log(data.message)  // should log: "Hello from Flask!"
})

</script>

<template>
  <div class="app-container">
    <header>
      <div class="logobox">
        <img alt="Vue logo" class="logo" src="@/assets/DatabaseLogoWhite.png" />
        <img alt="Vue logo" class="logotext" src="@/assets/databasetext.png" />
      </div>


      <nav>
        <router-link to="/">Home</router-link>
        <router-link to="/about">About</router-link>
        <router-link to="/uploadpath">Upload</router-link>
      </nav>

    </header>

    <main>
      <RouterView />
    </main>

    <div class="bg">
      <img alt="Vue logo" class="molecules left" src="@/assets/moleculesBG2.png" />

    </div>

    <footer>
      <!-- here is the footer-->
      <p></p>
    </footer>
  </div>
</template>

<style>
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

html {
  margin: 0;
  padding: 0;
  width: 100%;
  height: 100%;
}

body {
  margin: 0;
  padding: 0;
  width: 100vw;
  height: 100vh;
  overflow-x: hidden;
}

#app {
  margin: 0;
  padding: 0;
  width: 100vw;
  height: 100%;
}

.app-container {
  min-height: 100vh;
  width: 100vw;
  margin: 0;
  padding: 0;
  display: flex;
  flex-direction: column;
  position: relative;
}

header {
  width: 100vw;
  margin: 0;
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 1rem 0;
  background-color: #26a69a;
  z-index: 1;
}

main {
  flex: 1;
  min-height: 400px;
}

.bg{
  position:fixed;
  width:100vw;
  height:100vh;
  left:0;
  top:0;
  background-image: radial-gradient(circle at 50% 10%, #224e49 0, #121212 100%);
  z-index: -1;
}

.molecules{
  width:100vw;
  height:100vh;
  left:0;
  top:0;
  z-index: -1;
}

.left{
  float: left;
}

.right{
  float: right;
}

footer {
  width: 100vw;
  margin: 0;
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 1rem 0;
  background-color: #26a69a;
  z-index: 1;
  margin-top: auto;
}

.logobox{
  width: 50vw;
  display: flex;
  justify-content: center;
  flex-direction: row;
  align-items: center;
  margin-left: auto;
  margin-right: auto;
}

.logo {
  width: 100px;
  height: 100px;
  margin-right:-30px;
}
.logotext {
  width: 350px;
  height: 100px;
}

nav {
  display: flex;
  gap: 1rem;
  font-size: 16px;
}

nav a.router-link-exact-active {
  color: rgb(255, 255, 255);
  text-decoration: underline 2px;
  text-underline-offset: 4px;
}

</style>