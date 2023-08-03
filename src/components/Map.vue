<script setup>

// import * as Vue from 'vue';
import L from "leaflet";
import "leaflet/dist/leaflet.css";
import terminator from '@joergdietrich/leaflet.terminator';
import { ref, watch, computed, onMounted} from 'vue';
import  "../L.timezones.js";
import moment from 'moment-timezone';

//test
import "sidebar-v2/js/leaflet-sidebar.js"
import "sidebar-v2/css/leaflet-sidebar.css"
import "sidebar-v2/js/leaflet-sidebar.min.js"


// const get_target_time = (layer) =>{

//          //本地 Date物件
//         var now_local_date = new Date();
        
//         //UTC與本地差異時間
//         var local_diff_milsecond = now_local_date.getTimezoneOffset() * 60000; //getTimezoneOffset以分鐘為單位，*60*1000轉毫秒
        
//         //UTC Date物件 = 本地時間+本地與UTC差異時間
//         var now_utc_date = new Date(now_local_date.getTime() + local_diff_milsecond);

//         // 目標地與UTC差異時間
//         var target_zone_time = layer.feature.properties.time_zone; // ex."UTC+09:00"
//         var target_zone_diff = (target_zone_time.slice(3, 6) == "±00")? "0" : target_zone_time.slice(3, 6);


//         // 目標地 Date物件
//         var now_target_date = new Date(now_utc_date.getTime() + target_zone_diff*3600000); //time_zone_string以小時為單位，*60*60*1000轉毫秒
        

//         // 獲取目標地時間   
//         var year = now_target_date.getFullYear();    //獲取年份
//         var month = now_target_date.getMonth() + 1;  //獲取月份，返回的月份會比實際的小1，所以需要加1
//         var day = now_target_date.getDate();         //獲取日期
//         var hour = now_target_date.getHours();       //獲取小時數
//         var minute = now_target_date.getMinutes();   //獲取分鐘數
//         var second = now_target_date.getSeconds();   //獲取秒數

//         // 把獲取的時間元素組合成日期格式
//         var datetimeString = year + "年" + month + "月" + day + "日" + hour + "時" + minute + "分" + second + "秒";

//         return datetimeString;
//     };


// 公司廠區位置
const company = {
    "AUHQ":{
        "location": [24.7740885327886, 121.01952922069313]
    },
    "AUSZ":{
        "location": [31.336267940758084, 120.72016673028376]
    },
    "AUKS":{
        "location": [24.513111028988337, 118.1193578099503]
    },
    "AUXM":{
        "location": [31.188225825762043, 120.93693962361338]
    },
    "AUST":{
        "location": [1.360691789042172, 103.92974091157092]
    },
};

// 瀏覽器開始的初始值
let defaultZone = Intl.DateTimeFormat().resolvedOptions().timeZone;
let defaultZoneNow = new Date();
let defaultZoneNow_plus_year = new Date(); defaultZoneNow_plus_year.setFullYear(defaultZoneNow_plus_year.getFullYear() + 1);
let defaultZoneDate = defaultZoneNow.toLocaleDateString('en-CA');
let defaultZoneTime = defaultZoneNow.toLocaleTimeString('en-GB', { hour: '2-digit', minute: '2-digit' });


let selectedTimeZone = ref(defaultZone);
let selectedDate = ref(defaultZoneDate);
let selectedMins = ref(parseInt(defaultZoneTime.split(":")[0])*60 + parseInt(defaultZoneTime.split(":")[1]));

// 一天1440分鐘，轉為如"01:50:的格式
let selectedTime =  computed(() => {
    let hours = Math.floor(selectedMins.value / 60);
    let minutes = selectedMins.value % 60;

    // 若小於10，則在前面加上0
    hours = hours < 10 ? "0" + hours.toString() : hours.toString();
    minutes = minutes < 10 ? "0" + minutes.toString() : minutes.toString();
    return hours + ":" + minutes;
});

// 畫night lay的計算函式
let dateISO = computed(() => {
    
    // 不同時區的同時間的night lay位置不同，所以一律要轉成ISO_time
    let ISO_time = selectedDate.value + 'T' + selectedTime.value;
 
    // 创建 Moment 对象并设置时区
    let Zone_select_moment = moment.tz( ISO_time, selectedTimeZone.value);

    // 转成 ISO 字符串
    let Zone_moment_isoString = Zone_select_moment.toISOString();

    return Zone_moment_isoString;
});

// night lay的圖
let terminatorLayer;
// 地圖
let map;



// 將代碼移入 onMounted 中
onMounted(() => {

    // 監控日期、時間或者時區的改變
    watch([selectedTimeZone, selectedDate, selectedMins], () => {
        terminatorLayer.setLatLngs(terminator({time: dateISO.value}).getLatLngs()).redraw();
    });


     // 建立 leaflet 地圖
    map = L.map('map').setView([24.7740885327886, 121.01952922069313], 2.5);
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


    // 建立各site圖標
    for (let key in company) {
        let location = company[key].location;
        let lat = location[0];
        let lng = location[1];
        let time = null;
        
        //檢查圖標經緯度是否在timezoneLayers下的layer中，若有的話紀錄該時區目前時間
        for ( let layer of timezoneLayers){
    
            if (layer.getBounds().contains([lat,lng])){
                let layer_name = layer.feature.properties.tz_name1st
                time = new Date().toLocaleString("en-GB", {timeZone:layer_name});
                break;
            };
        };
        
        
        let company_data = `${key}<br>緯度: ${lat}, <br>經度: ${lng} <br>時間: ${time} `;
        
        // get_target_time
        L.marker([lat, lng]).addTo(map).bindPopup(company_data); // .openPopup('AUHQ')

    };


    //建立時區物件，並在點擊時渲染目標地時間
    L.timezones.bindPopup(function (layer) {
    return new Date().toLocaleString("en-GB", {timeZone:layer.feature.properties.tz_name1st, timeZoneName:"short"})
}).addTo(map);



});

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
                <li><a class="justify-center items-center !flex" href="#home"><img src="dist/menu-hambuger.svg"/></a></li>
                <li><a class="justify-center items-center !flex" href="https://www.letswrite.tw/leaflet-plugins/" target="_blank"><img src="dist/web.svg"/></a></li>
                <li><a class="justify-center items-center !flex" href="https://github.com/letswritetw/letswrite-leaflet-plugins" target="_blank"><img src="dist/brand-github.svg"/></a></li>
              </ul>
              <!-- 第二個 ul 在下面-->
              <ul>
                <li><a class="justify-center items-center !flex" href="#settings"><img src="dist/setting.svg"/></a></li>
              </ul>
            </div>
            <!-- Tabs 內容-->
            <div class="sidebar-content text-gray-800">
              <div class="sidebar-pane" id="home">
                <h3 class="sidebar-header mb-4 bg-main">客製選單 說明<span class="sidebar-close"><i class="fa fa-caret-left"></i></span></h3>
                <p class="mb-2 font-bold text-xl">使用套件</p>
                <ul class="list-disc pl-6">
                  <li><a class="inline-block mb-4 text-main" href="https://github.com/turbo87/sidebar-v2/" target="_blank">sidebar-v2</a></li>
                </ul>
                <p class="mb-2 font-bold text-xl">其它覺得不錯的套件</p>
                <ul class="list-disc pl-6">
                  <li class="mb-2"><a class="text-main" href="https://github.com/yohanboniface/Leaflet.TileLegend" target="_blank">Leaflet.TileLegend</a></li>
                  <li class="mb-2"><a class="text-main" href="https://github.com/yigityuce/Leaflet.Control.Custom" target="_blank">Leaflet.Control.Custom</a></li>
                  <li class="mb-2"><a class="text-main" href="https://github.com/ptma/Leaflet.Legend" target="_blank">Leaflet.Legend</a></li>
                  <li class="mb-2"><a class="text-main" href="https://github.com/maxwell-ilai/Leaflet.SidePanel" target="_blank">Leaflet.SidePanel</a></li>
                </ul>
              </div>
              <div class="sidebar-pane" id="settings">
                <h3 class="sidebar-header mb-4 bg-main">設定<span class="sidebar-close"><i class="fa fa-caret-left"></i></span></h3>
                <p>這邊可以加入使用說明</p>
              </div>
            </div>
          </div>
          <div class="sidebar-map absolute w-full !h-full" id="map"></div>
        </div>
          
          
       
  
    
       
        <div id="select_area" >
            <!-- 時區 -->
            <div id="timezone_select_area">
                <h3 for="tz">本地時區</h3>
                    <select id="tz" v-model="selectedTimeZone" style="height: 30%;">
                        <option value="Asia/Taipei">Asia/Taipei</option>
                        <option value="America/New_York">America/New_York</option>
                    </select>
                </div>
    
            <!-- 日期 -->
            <div id="date_select_area">
                <h3 for="date">本地日期</h3>
                    <input type="date" id="date" v-model="selectedDate" v-bind:min="defaultZoneDate" v-bind:max="defaultZoneNow_plus_year.toLocaleDateString('en-CA')" style="height: 30%;">
            </div>

            <!-- 時間 -->
            <div id="time_select_area">

                <h3 for="time" >本地時間: {{selectedTime}}</h3>
                <div id="time_control_area" style="display: flex; align-items: center;">
                    <button @click="decrementMins" style="height: 2vh; width: 2vh; display: flex; align-items: center; justify-content: center;">
                        <img src="../assets/left.png" style="height: 2vh; width: 2vh;" >            
                    </button>
                    <input type="range" id="time" v-model="selectedMins" min="0" max="1440" step="15" style="height: 30%;" >    
                    <button @click="incrementMins " style="height: 2vh; width: 2vh; display: flex; align-items: center; justify-content: center;">
                        <img src="../assets/right.png" style="height: 2vh; width: 2vh;">            
                    </button>
                </div>
            </div>


        </div>


    </div>



</template>

<style >
body {
        padding: 0;
        margin: 0;
    }

/* #map會依照父元素的大小決定大小，所以要設定#map上面的父元素 */
html, body, #app, #map_container, #map {
    height: 100%;
    width: 100%;
}

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

.lorem {
            font-style: italic;
            color: #AAA;
        }

</style>
