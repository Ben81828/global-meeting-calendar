<template>
    <!-- give the sidebar z-50 class so its higher than the navbar if you want to see the logo -->
    <!-- you will need to add a little "X" button next to the logo in order to close it though -->

    
    <div class="w-1/2 md:w-1/3 lg:w-64 fixed md:top-0 md:left-0 h-screen lg:block bg-gray-100 border-r z-50" :class="sideBarOpen ? '' : 'hidden'" id="main-nav">

          <div class="w-full h-20 border-b flex px-4 items-center mb-8">
            <img src="../assets/logo-footer.svg" class="z-50">
  
          </div>

          <div class="mb-4 px-4">
            <p class="pl-4 text-sm font-semibold mb-1">MAIN</p>

            <div class="w-full flex items-center text-blue-400 h-10 pl-4  hover:bg-gray-200 rounded-lg cursor-pointer">
              <svg class="h-6 w-6 fill-current mr-2" viewBox="0 0 20 20">
                <path d="M18.121,9.88l-7.832-7.836c-0.155-0.158-0.428-0.155-0.584,0L1.842,9.913c-0.262,0.263-0.073,0.705,0.292,0.705h2.069v7.042c0,0.227,0.187,0.414,0.414,0.414h3.725c0.228,0,0.414-0.188,0.414-0.414v-3.313h2.483v3.313c0,0.227,0.187,0.414,0.413,0.414h3.726c0.229,0,0.414-0.188,0.414-0.414v-7.042h2.068h0.004C18.331,10.617,18.389,10.146,18.121,9.88 M14.963,17.245h-2.896v-3.313c0-0.229-0.186-0.415-0.414-0.415H8.342c-0.228,0-0.414,0.187-0.414,0.415v3.313H5.032v-6.628h9.931V17.245z M3.133,9.79l6.864-6.868l6.867,6.868H3.133z"></path>
              </svg>
              
              <router-link to="/" exact-active-class="bg-gray-200">
                <span class="text-gray-700">Global Office Time</span>
              </router-link>
            </div>
            
            <div class="w-full flex items-center text-blue-400 h-10 pl-4 hover:bg-gray-200 rounded-lg cursor-pointer">              
               
              <svg class="h-6 w-6 fill-current mr-2" viewBox="0 0 20 20">
                <path d="M17.431,2.156h-3.715c-0.228,0-0.413,0.186-0.413,0.413v6.973h-2.89V6.687c0-0.229-0.186-0.413-0.413-0.413H6.285c-0.228,0-0.413,0.184-0.413,0.413v6.388H2.569c-0.227,0-0.413,0.187-0.413,0.413v3.942c0,0.228,0.186,0.413,0.413,0.413h14.862c0.228,0,0.413-0.186,0.413-0.413V2.569C17.844,2.342,17.658,2.156,17.431,2.156 M5.872,17.019h-2.89v-3.117h2.89V17.019zM9.587,17.019h-2.89V7.1h2.89V17.019z M13.303,17.019h-2.89v-6.651h2.89V17.019z M17.019,17.019h-2.891V2.982h2.891V17.019z"></path>
              </svg>

              <router-link to="/recommand" exact-active-class="bg-gray-200" class="bg-blue">   
                  <span class="text-gray-700">Schedule Recommand</span>
              </router-link>
            </div>  

            <div class="w-full flex items-center text-blue-400 h-10 pl-4 hover:bg-gray-200 rounded-lg cursor-pointer">              
            
              <svg class="h-6 w-6 fill-current mr-2" viewBox="0 0 24 24">
                <path d="M4 5h4V3a1 1 0 0 1 2 0v2h4V3a1 1 0 0 1 2 0v2h4a1 1 0 0 1 1 1v14a1 1 0 0 1-1 1H4a1 1 0 0 1-1-1V6a1 1 0 0 1 1-1zm5 10v6h6v-6H9z"/>
              </svg>

              <router-link to="/calendar" exact-active-class="bg-gray-200" class="bg-blue">   
                  <span class="text-gray-700">Calendar</span>
              </router-link>
            </div> 
              
            
          </div>
    </div>




</template>

<script setup>
import { computed } from 'vue';
import { useStore } from 'vuex';
const store = useStore();

let sideBarOpen = computed(() => store.state.is_toggle_open);



</script>

<style>

</style>