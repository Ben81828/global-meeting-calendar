<script setup>
import Sidebar from "./Sidebar.vue"
// import Footer from "./Footer.vue"
import Navbar from "./Navbar.vue"

</script>

<template>

<div class="leading-normal tracking-normal" id="main-body">
    <div class="flex flex-wrap">

      <Sidebar />
      
      <div class="w-full bg-gray-100 pl-0 lg:pl-64 min-h-screen">

        <Navbar></Navbar>

        <div class="p-6 bg-gray-100 mb-0 z-0 ">
            <router-view></router-view>
            <!-- <Map></Map> -->
        </div>

        <!-- <Footer></Footer> -->

      </div>
    </div>
</div>



        <!-- <div class="">
            <Map></Map>
        </div> -->
        

    

    
</template>

<style >


</style>
