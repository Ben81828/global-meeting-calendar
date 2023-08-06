<script setup>

// import * as Vue from 'vue';
import L from "leaflet";
import "leaflet/dist/leaflet.css";
import terminator from '@joergdietrich/leaflet.terminator';
import { ref, reactive, watch, computed, onMounted, nextTick} from 'vue';
import  "../L.timezones.js";
import moment from 'moment-timezone';

//test
import "sidebar-v2/js/leaflet-sidebar.js"
import "sidebar-v2/css/leaflet-sidebar.css"
import "sidebar-v2/js/leaflet-sidebar.min.js"


// 公司廠區位置
let company = reactive({
    "AUHQ":{
        "location": [24.7740885327886, 121.01952922069313],
        "time":null,
        "time_zone":null,
    },
    "AUSZ":{
        "location": [31.336267940758084, 120.72016673028376],
        "time":null,
        "time_zone":null,
    },
    "AUKS":{
        "location": [24.513111028988337, 118.1193578099503],
        "time":null,
        "time_zone":null,
    },
    "AUXM":{
        "location": [31.188225825762043, 120.93693962361338],
        "time":null,
        "time_zone":null,
    },
    "AUST":{
        "location": [1.360691789042172, 103.92974091157092],
        "time":null,
        "time_zone":null,
    },
});

let company_checked = reactive(Object.keys(company).reduce(function(acc, key) {
    acc[key] = true;
    return acc;
}, {}));



// 預設時區、時間為使用者瀏覽器當前的時區
let defaultZone = Intl.DateTimeFormat().resolvedOptions().timeZone;
let defaultZoneNow = new Date();
// 後續使用者選擇的日曆僅顯示今天到後面一年內
let defaultZoneNow_plus_year = new Date(); defaultZoneNow_plus_year.setFullYear(defaultZoneNow_plus_year.getFullYear() + 1);
// 時間轉換的日期及時間
let defaultZoneDate = defaultZoneNow.toLocaleDateString('en-CA');
let defaultZoneTime = defaultZoneNow.toLocaleTimeString('en-GB', { hour: '2-digit', minute: '2-digit' });

// 瀏覽器側邊欄時間選單的初始值
let iso_date_obj;                           // 後面要計算其他時區的時間，需先轉換成ISO標準時間
let selectedTimeZone = ref(defaultZone);
let selectedDate = ref(defaultZoneDate);
let selectedMins = ref(parseInt(defaultZoneTime.split(":")[0])*60 + parseInt(defaultZoneTime.split(":")[1])); 


// 一天1440分鐘，轉為如"01:50"的格式。於指定的時區日期、時間改變時觸發
let selectedTime =  computed(() => {
    let hours = Math.floor(selectedMins.value / 60);
    let minutes = selectedMins.value % 60;

    // 若小於10，則在前面加上0
    hours = hours < 10 ? "0" + hours.toString() : hours.toString();
    minutes = minutes < 10 ? "0" + minutes.toString() : minutes.toString();
    return hours + ":" + minutes;
});


// 將指定時區的時間轉成標準時間ISO，用於計算和轉換night layer及marker顯示的時間。指定的時區日期時間改變時觸發
let dateISO = computed(() => {
    
    let ISO_time = selectedDate.value + 'T' + selectedTime.value;
 
    // 创建 Moment 对象并设置时区
    let Zone_select_moment = moment.tz( ISO_time, selectedTimeZone.value);

    // 转成 ISO 字符串
    let Zone_moment_isoString = Zone_select_moment.toISOString();

    // 更新iso_date_obj物件    
    iso_date_obj = new Date(Zone_moment_isoString); //dateISO是dateString

    return Zone_moment_isoString;
});

// night lay的圖
let terminatorLayer;
// 地圖
let map;


// 調本地時區的時間按鈕
const decrementMins = () => {
    if (selectedMins.value > 0 && selectedMins.value % 15 !== 0) {
        selectedMins.value = (parseInt(selectedMins.value) - (parseInt(selectedMins.value) % 15));         
    }
    else if (selectedMins.value > 0 && selectedMins.value % 15 === 0) {
        selectedMins.value = (parseInt(selectedMins.value) - 15).toString();    
    }
};

const incrementMins = () => {
    if (selectedMins.value < 1440 && selectedMins.value % 15 !== 0) {
        selectedMins.value = (parseInt(selectedMins.value) + 15 - (parseInt(selectedMins.value) % 15));      
    }
    else if (selectedMins.value < 1440 && selectedMins.value % 15 === 0) {
        selectedMins.value = (parseInt(selectedMins.value) + 15).toString();
    }

};




// onMounted 
onMounted(() => {

    // 監控日期、時間或者時區的改變
    watch([selectedTimeZone, selectedDate, selectedMins, company_checked], () => {
        
        terminatorLayer.setLatLngs(terminator({time: dateISO.value}).getLatLngs()).redraw();
        
    });
    

     // 建立 leaflet 地圖
    map = L.map('map').fitWorld().setView([24.7740885327886, 121.01952922069313], 2.5);
    terminatorLayer = terminator({time: dateISO.value}).addTo(map);


    // https://tiles.stadiamaps.com/tiles/alidade_smooth_dark/{z}/{x}/{y}{r}.png   // 黑底地圖
    L.tileLayer(' https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        minZoom: 2, // 這裡設定Z最大為5
        maxZoom: 3, // 這裡設定Z最大為5
        attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
    }).addTo(map);
    
    // sidebar
    const sidebar = L.control.sidebar('sidebar').addTo(map);
    
    // 限制使用者未能滾動出此範圍
    var southWest = L.latLng(-69.98155760646617, -180),
        northEast = L.latLng(89.99346179538875, 180);
    var bounds = L.latLngBounds(southWest, northEast);

    map.setMaxBounds(bounds);


    // 存全世界各時區的layer，判斷後續各site的時區位置(抓site目前時間)
    let timezoneLayers = [];  // 用于保存所有的 timezone Layer 对象
    // 全世界各時區的layer，取出名字非null的，放入timezoneLayers
    for (let layer_num in L.timezones._layers){
        let timezoneLayer = L.timezones._layers[layer_num];
        let layer_name = timezoneLayer.feature.properties.tz_name1st;
        
        try{
            //若layer_name為null會報錯，就跳過
            new Date().toLocaleString("en-GB", {timeZone:layer_name, timeZoneName:"short"});
            //沒報錯就加到後續用來判斷的時區
            timezoneLayers.push(timezoneLayer);

        }catch{
            null;
        }
    };

    let layerGroup = L.layerGroup().addTo(map);

    
    // 依據checkbox的變化，建立site圖標
    watch([dateISO, company_checked], () => {
        layerGroup.clearLayers();
                
        // 建立各 site 圖標時，會從company中取出座標，並依座標檢查它在timezoneLayers中所在時區，用iso_date_obj去計算其時間，並將時間放回company中
        for (let key in company) {
            // 在 checkbox 被打勾的才進行後續建立圖標
            if (company_checked[key] !== true){ continue };
            
            let location = company[key].location;
            
            // 計算在哪個layer
            let lat = location[0];
            let lng = location[1];

            // 待計算的時區和時間
            let layer_name;
            let time;
            
            //檢查圖標經緯度是否在 timezoneLayers 下的 layer 中，若有的話，將指定時間轉換的ISO時間，轉成該timezone的時間
            for ( let layer of timezoneLayers){
                if (layer.getBounds().contains([lat,lng])){
                    layer_name = layer.feature.properties.tz_name1st
                    time = iso_date_obj.toLocaleString("en-GB", {timeZone:layer_name});                  
                    company[key].time = time;
                    company[key].time_zone = layer_name;
                    
                                                    
                    break;
                };
            };

            let company_data = `${key} <br>時间: ${time}`;

            // 建立 marker 并加入图层组
            let marker = L.marker([lat, lng], {riseOnHover: true}).bindPopup(company_data);
            layerGroup.addLayer(marker);
        };
        

    },{ immediate: true }); // immediate: true表示網頁初始化时立即调用



    //建立時區物件，並在點擊時渲染目標地時間
    L.timezones.bindPopup(function (layer) {
    return iso_date_obj.toLocaleString("en-GB",{timeZone:layer.feature.properties.tz_name1st, timeZoneName:"short"})
}).addTo(map);



});




</script>


<template>
    
    <div id="map_container">

        <div id="map_container" class="relative w-full h-0 pb-[75%] sm:pb-[56.25%]">
            
          <!-- leaflet-sidebar-v2-->
          <div class="sidebar collapsed !border-r-0" id="sidebar">
            <!-- Tabs 按鈕-->
            <div class="sidebar-tabs">
              <!-- 第一個 ul 在上面-->
              <ul>
                <li><a class="justify-center items-center !flex" href="#time_select"><img class="icon_img" src="../assets/clock.svg"/></a></li>
                <li><a class="justify-center items-center !flex" href="#sites_show" target="_blank"><img class="icon_img" src="../assets/locate-marker.svg"/></a></li>
                <li><a class="justify-center items-center !flex" href="#sites_time" target="_blank"><img class="icon_img" src="../assets/calendars-with-check-mark.svg"/></a></li>
              </ul>
              <!-- 第二個 ul 在下面-->
              <ul>
                <li><a class="justify-center items-center !flex" href="#settings"><img class="icon_img" src="../assets/setting.svg"/></a></li>
              </ul>
            </div>
            <!-- Tabs 內容-->
            <div class="sidebar-content text-gray-800">
                
                <!--Tab1:調整本地時區、日期、時間作為基準-->
                <div class="sidebar-pane" id="time_select">
                    <h3 class="sidebar-header mb-4 bg-main">會議時間<span class="sidebar-close"><i class="fa fa-caret-left"></i></span></h3>
                    <!-- 時區 -->
                    <div id="select_area" >
                        <div id="timezone_select_area">
                            <h3 for="tz">本地時區</h3>
                                <select id="tz" v-model="selectedTimeZone" >
                                    <option value="Asia/Taipei">Asia/Taipei</option>
                                    <option value="America/New_York">America/New_York</option>
                                </select>
                            </div>
                    </div>
                    <!-- 日期 -->
                    <div id="select_area" >
                        <div id="date_select_area">
                            <h3 for="date">本地日期</h3>
                                <input type="date" id="date" v-model="selectedDate" v-bind:min="defaultZoneDate" v-bind:max="defaultZoneNow_plus_year.toLocaleDateString('en-CA')" >
                        </div>
                     </div>
                    <!-- 時間 -->
                    <div id="select_area" >
                        <div id="time_select_area">

                            <h3 for="time" >本地時間: {{selectedTime}}</h3>
                    
                                <input type="range" id="time" v-model="selectedMins" min="0" max="1440" step="15" > 
                     
                            <div id="time_control_area" style="display: flex;">
                                <button @click="decrementMins" style="height: 2vh; width: 2vh; display: flex; align-items: center; justify-content: center;">
                                    <img src="../assets/left.png" style="height: 2vh; width: 2vh;" >            
                                </button>   
                                <button @click="incrementMins " style="height: 2vh; width: 2vh; display: flex; align-items: center; justify-content: center;">
                                    <img src="../assets/right.png" style="height: 2vh; width: 2vh;">            
                                </button>
                            </div>                                
                        </div>
                    </div>
                </div>
              
                <!--Tab2:生成勾選各site的核取方格-->
              <div class="sidebar-pane" id="sites_show">
                <h3 class="sidebar-header mb-4 bg-main">Sites顯示<span class="sidebar-close"><i class="fa fa-caret-left"></i></span></h3>
                <div v-for="(value, site) in company" :key="site">
                    <input 
                        type="checkbox" 
                        :id="site" 
                        :value="value"
                        v-model="company_checked[site]"
                    >
                    <label :for="site">{{site}}</label>
                    
                  
                </div>
              </div>

              <div class="sidebar-pane" id="sites_time">
                <h3 class="sidebar-header mb-4 bg-main">Sites 時間<span class="sidebar-close"><i class="fa fa-caret-left"></i></span></h3>
                <div v-for="(value, site) in company" :key="site" >
                    <div v-if="company_checked[site]"   class="site_card_area" >
                 
                        <label v-text="site" style="font-weight: bold;"></label>
                        <br><label v-text="'時區名稱: '+value.time_zone"></label> 
                        <br><label v-text="'時區時間: '+value.time"></label> 
                    </div>
                </div>
              </div>

              <div class="sidebar-pane" id="settings">
                <h3 class="sidebar-header mb-4 bg-main">設定<span class="sidebar-close"><i class="fa fa-caret-left"></i></span></h3>
                <p>這邊可以加入使用說明</p>
              </div>
            </div>
          </div>
        <div class="sidebar-map absolute w-full !h-full" id="map"></div>
    </div>

    </div>

</template>

<style >
body {
    padding: 0;
    margin: 0;
}

/* #map會依照父元素的大小決定大小，所以要設定#map上面的父元素 */
html, body, #app, #map_container {
    height: 100%;
    width: 100%;
    /* display: flex; */
    /* width: 100vw; */

}

#map{
    position: absolute;
    top: 0;
    right: 0;
    bottom: 0;
    left: 0;  
}

.icon_img {
  max-width: 100%;
  height: auto;
}


.lorem {
            font-style: italic;
            color: #AAA;
        }

#select_area {
    display: flex;               /* 使子元素沿行方向排列 */
    flex-direction: column;      /* 子元素以列的方式排列 */
    justify-content: space-around; /* 子元素之間的空間平均分佈，並在首尾也留有空間 */
    box-sizing: border-box;      /* 讓 padding 和 border 不影響元素的實際寬度和高度 */
    width: 90%;                  /* 元素佔父元素寬度的百分比 */
    height: 30%;                 /* 元素佔父元素高度的百分比 */
    margin: 5% auto;             /* 垂直居中元素並設定上下邊距 */
    padding: 1em;                /* 把距離內部的子元素們設定為1em */
    border-radius: 5px;
    border: 1px solid black;
}

#timezone_select_area, #date_select_area, #time_select_area {
  flex-basis: 32%;
  /* 為 mobile view 設定，若畫面夠小則換行排列 */
  margin-bottom: 15px;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;

}

#time-control_area {
    display: flex;
    align-items: center;
    /* if you need some space between elements */
    justify-content: space-between;
    margin: 0%;
    padding: 0;
  } 


.site_card_area {
    margin-top: 10px;
    margin-bottom: 10px;
    text-align: left; 
    border-radius: 5px;
    border: 1px solid black;
}


</style>

<!-- 
#select_area{
    /* 距離上方的距離，可以修改以符合你的需求 */
    position: absolute;
    bottom: 20px;
    /* 距離左邊的距離，可以修改以符合你的需求 */
    left: 50%;
    transform: translateX(-50%);
    width: 65%;
    /* 這裡的值需要比你的地圖的 z-index 更高 */
    z-index: 1000;  
    /* 添加白色背景 */
    background-color: rgba(255, 255, 255, 0.8);
    /* 添加黑色边框 */
    border-radius: 5px;
    border: 1px solid black;

    display: flex;
    flex-wrap: wrap;
    justify-content: space-between;
    /* 可選的 padding 和 margin 樣式，用以確保內部元件與容器的邊緣有些間距 */
    padding: 10px;
    box-sizing: border-box;
    pointer-events:auto;
}

#timezone_select_area, #date_select_area, #time_select_area {
  flex-basis: 32%;
  /* 為 mobile view 設定，若畫面夠小則換行排列 */
  margin-bottom: 15px;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;

}

#time-control_area {
    display: flex;
    align-items: center;
    /* if you need some space between elements */
    justify-content: space-between;
    margin: 0%;
    padding: 0;
  } -->