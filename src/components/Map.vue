<script setup>

import * as Vue from 'vue';
import L from "leaflet"
import { onMounted } from 'vue';

// 將代碼移入 onMounted 中
onMounted(() => {
    console.log("in map onmount")
    var map = L.map('map').setView([25.0339145, 121.5412233], 13);

    L.tileLayer(' https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
    }).addTo(map);

    L.marker([25.0339145, 121.5412233]).addTo(map)
        .bindPopup('自訂訊息 可以放 HTML')
        .openPopup();
});

</script>


<template>
    <div id="map"></div>

</template>

<style scoped>
    #map { height: 640px; }
</style>
