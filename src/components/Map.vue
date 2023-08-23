<script setup>

import { ref, reactive, watch, computed, onMounted, onBeforeUnmount} from 'vue';

// leaflet
import L from "leaflet";
import "leaflet/dist/leaflet.css";

// leaflet terminator
import terminator from '@joergdietrich/leaflet.terminator';
import  "../L.timezones.js";

// timezone
import moment from 'moment-timezone';

//用來檢查座標是否落在時區的多邊形內，以確認落在哪個時區
import * as turf from '@turf/turf'

// store
import { useStore } from 'vuex';
const store = useStore(); // store實體


// 公司資料
let company = computed(() => {return store.state.company}).value;

// 物件: 已被選的公司。各公司按鈕value會on這個物件key所對應的值(true或false)
let company_checked = computed(() => {return store.state.selected_company}).value;



// bool: 此變數為"公司全選按鈕"on的值，按鈕沒被勾選時會變false
let all_company_checked = ref(true);

// 此變數用來在all_company_checked有變化時，改變company_checked所有value，並渲染"公司全選按鈕"的文字。
// all_company_checked 為true的文字為"全選"，false為"取消全選" 
let all_company_select = computed(() => {
 
    for(let site in company_checked){
        company_checked[site]=all_company_checked.value;       
    }
    return all_company_checked.value;
});

// 串列: 因company物件內會有時區資料，此變數整理出唯一時區的串列，並用來渲染"時區下拉選單"
let uniqueTimeZoneList = computed(() => {

    let uniqueList = [Intl.DateTimeFormat().resolvedOptions().timeZone]; //先讀取使用者裝置的時區，當作預設的第一個元素
 
    for (let key in company){ 
       
        let timezone = company[key].time_zone;
        if (( !uniqueList.includes(timezone)) && timezone!==null) {
            uniqueList.push(timezone);
        }
    }
    return uniqueList
});

// 預設時區、時間為使用者瀏覽器當前的時區
let defaultZone = uniqueTimeZoneList.value[0];
let defaultZoneNow = new Date();
// 後續使用者選擇的日曆僅顯示今天到後面一年內
let defaultZoneNow_plus_year = new Date(); defaultZoneNow_plus_year.setFullYear(defaultZoneNow_plus_year.getFullYear() + 1);
// 用漂亮一點的格式，讀取日期、時間，用來做後續解析、轉換
let defaultZoneDate = defaultZoneNow.toLocaleDateString('en-CA'); //2023-08-22
let defaultZoneTime = defaultZoneNow.toLocaleTimeString('en-GB', { hour: '2-digit', minute: '2-digit', second:  '2-digit'}); // ex.16:47:11


// 瀏覽器的"時間選單"初始值
let date_obj;                           
let selectedTimeZone = ref(defaultZone);

let selectedDate = ref(defaultZoneDate);
// let selectedMins= ref(parseInt(defaultZoneTime.split(":")[0])*60 + parseInt(defaultZoneTime.split(":")[1])); 
let selectedSeconds = ref(parseInt(defaultZoneTime.split(":")[0])*3600 + parseInt(defaultZoneTime.split(":")[1])*60 + parseInt(defaultZoneTime.split(":")[2])); 


// 一天86400秒鐘，轉為如"01:50:10"的格式。於指定的時區日期、時間改變，或在加秒時觸發
let hours_selected = computed(() =>{ return Math.floor(selectedSeconds.value / 3600)});
let minutes_selected = computed(() =>{ return Math.floor(selectedSeconds.value % 3600 / 60)});
let seconds_selected = computed(() =>{ return selectedSeconds.value % 3600 % 60;});
let selectedTime =  computed(() => {
    // 若小於10，則在前面加上0
    let hours_str = hours_selected.value < 10 ? "0" + hours_selected.value.toString() : hours_selected.value.toString();
    let minutes_str = minutes_selected.value < 10 ? "0" + minutes_selected.value.toString() : minutes_selected.value.toString();
    let seconds_str = seconds_selected.value < 10 ? "0" + seconds_selected.value.toString() : seconds_selected.value.toString();

    return hours_str + ":" + minutes_str + ":" + seconds_str;

});

// "計時器"加秒
setInterval(function() {
    if (selectedSeconds.value < 86400){
        selectedSeconds.value++;
    };
}, 1000);  // 這裡的 1000 是毫秒，所以 1000 毫秒就是 1 秒

// 選定時區、時間的Moment對象
let Zone_select_moment;

// 將指定時區的時間轉成標準時間ISO，用於計算和轉換night layer及marker顯示的時間。指定的時區日期時間改變時觸發
let date_ISO_str = computed(() => {
    
    let selected_time_format = selectedDate.value + 'T' + selectedTime.value;
 
    // 创建 Moment 对象并设置时区
    Zone_select_moment = moment.tz( selected_time_format, selectedTimeZone.value);
    
    // 转成 ISO 字符串
    let Zone_moment_isoString = Zone_select_moment.toISOString();

    // 更新date_obj物件    
    date_obj = new Date(Zone_moment_isoString); //date_ISO_str是dateString

    return Zone_moment_isoString;
});


// night lay的圖
let terminatorLayer;
// 地圖
let map;

// 燈箱控制
let isShow = ref(false);
let modalStyle = computed(() => {return !isShow.value ? "display:none;" : ""});
const toggleModal = () => { isShow.value = !isShow.value; };


// 調本地時區的時間按鈕
const decrementMins = () => {
    if (selectedSeconds.value > 0 && selectedSeconds.value % 900 !== 0) {
        selectedSeconds.value = (parseInt(selectedSeconds.value) - (parseInt(selectedSeconds.value) % 900));         
    }
    else if (selectedSeconds.value > 0 && selectedSeconds.value % 900 === 0) {
        selectedSeconds.value = (parseInt(selectedSeconds.value) - 900).toString();    
    }
};

const incrementMins = () => {
    if (selectedSeconds.value < 86400 && selectedSeconds.value % 900 !== 0) {
        selectedSeconds.value = (parseInt(selectedSeconds.value) + 900 - (parseInt(selectedSeconds.value) % 900));      
    }
    else if (selectedSeconds.value < 86400 && selectedSeconds.value % 900 === 0) {
        selectedSeconds.value = (parseInt(selectedSeconds.value) + 900).toString();
    }
};


const getDayInEnglish = (dayNumber) => {
  const days = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'];

  return days[dayNumber];
};



// onMounted 
onMounted(() => {

    // 監控日期、時間或者時區的改變
    watch([selectedTimeZone, selectedDate, selectedSeconds, company_checked], () => {
        terminatorLayer.setLatLngs(terminator({time: date_ISO_str.value}).getLatLngs()).redraw();
    });
    

     // 建立 leaflet 地圖
    map = L.map('map',{
        // zoomControl: false,
        // dragging: false,
        scrollWheelZoom: false,
        doubleClickZoom: false,
        minZoom: 1,
        maxZoom: 2,
    })
    .fitWorld()
    // .setView([0, 0], 0);
    .setView([45,5],2);
    terminatorLayer = terminator({time: date_ISO_str.value}).addTo(map);

    // tile setting
    // https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png //openstreetmap
    // https://tiles.stadiamaps.com/tiles/alidade_smooth_dark/{z}/{x}/{y}{r}.png   // 黑底地圖
    // https://tiles.stadiamaps.com/tiles/alidade_smooth/{z}/{x}/{y}{r}.png  // 白底
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        noWrap: true,              //this is the crucial line!(使地圖超出範圍後不重複)
        bounds: [
            [-65, -180],
            [84, 180]
        ],
        attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
    }).addTo(map);
    
    //建立時區物件，並在點擊時渲染目標地時間
    L.timezones.bindPopup(function (layer) {
        let timezone = layer.feature.properties.tz_name1st;
        return timezone
    }).addTo(map);

    // // sidebar
    // const sidebar = L.control.sidebar('sidebar').addTo(map);

    
    // 限制使用者未能滾動出此範圍
    var southWest = L.latLng(-65, -180),
        northEast = L.latLng(84, 180);
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

   
    
    // 依據checkbox的變化，建立site圖標
    let layerGroup = L.layerGroup().addTo(map);
    watch([date_ISO_str, company_checked], () => {

        layerGroup.clearLayers();                
        // 建立各 site 圖標時，會從company中取出座標，並依座標檢查它在timezoneLayers中所在時區，用date_obj去計算其時間，並將時間放回company中
        for (let key in company) {
            // 在 checkbox 被打勾的才進行後續建立圖標
            if (company_checked[key] !== true){ continue };
            
            let location = company[key].location;
            
            // 計算在哪個layer
            let lat = location[0];
            let lng = location[1];

            // 待計算的時區和時間
            let layer_name;
            let year; let month; let date; let day;let time;
            let color;
            let company_data;

                    
            //檢查圖標經緯度是否在 timezoneLayers 下的 layer 中，若有的話，將指定時間轉換的ISO時間，轉成該timezone的時間
            for ( let layer of timezoneLayers){

                
                //將當前的layer轉為GeoJSON
                let layerGeoJSON = layer.toGeoJSON();
                
                //創建一個表示你測試的點的GeoJSON
                let point = turf.point([lng, lat]);

                if (turf.booleanPointInPolygon(point,layerGeoJSON)){
                    layer_name = layer.feature.properties.tz_name1st
                    // 用toLocaleString轉出layer的時間
                    //toLocaleString會變day/month/year，這邊改成month/day/year，後面放Date()內時才不會出錯
                    let parts = date_obj.toLocaleString("en-GB", {timeZone:layer_name}).split("/");
                    let layer_date_obj = new Date(`${parts[1]}/${parts[0]}/${parts[2]}`);
                    year = parts[2].split(',')[0];
                    month = parts[1];
                    date = parts[0];
                    time = parts[2].split(',')[1].trim();
                    day = layer_date_obj.getDay();

                    company[key].year = year;
                    company[key].month = month;
                    company[key].date = date;
                    company[key].time = time;
                    company[key].week_day = getDayInEnglish(day);

  


                    // if (layer_name==="Australia/Perth"){layer_name="Asia/Taipei"}; //"Australia/Perth"跟"Asia/Taipei"一樣，讓後續調時區時兩選項效果一樣，"Australia/Perth"可能也較容易混淆
                    company[key].time_zone = layer_name;
                    
                    // 判斷是否在工作時間或黃金時間                   
                    let hours = layer_date_obj.getHours();// 获取小时和分钟
                    let minutes = layer_date_obj.getMinutes();// 获取小时和分钟
                    let seconds = layer_date_obj.getSeconds();// 获取小时和分钟
                    // 转换为分钟的总量，更便于比较
                    let timeInMinutes = hours * 60 + minutes;            
                    // 小時分鐘轉文字
                    let hours_str = hours  < 10 ? "0" + hours.toString() : hours.toString(); 
                    let minutes_str = minutes < 10 ? "0" + minutes.toString() : minutes.toString(); 
                    let seconds_str = seconds < 10 ? "0" + seconds.toString() : seconds.toString(); 
                                        

                    // 把work time和gold time也转换为分钟的总量
                    let work_interval = company[key].work_hour
                    let work_start = parseInt(work_interval[0].split(":")[0]) * 60 + parseInt(work_interval[0].split(":")[1]);
                    let work_end = parseInt(work_interval[1].split(":")[0]) * 60 + parseInt(work_interval[1].split(":")[1]);

                    // 把work time和gold time也转换为分钟的总量
                    let gold_interval = company[key].gold_hour
                    let gold_start = parseInt(gold_interval[0].split(":")[0]) * 60 + parseInt(gold_interval[0].split(":")[1]);
                    let gold_end = parseInt(gold_interval[1].split(":")[0]) * 60 + parseInt(gold_interval[1].split(":")[1]);

                    // 把work time和rest time也转换为分钟的总量
                    let rest_interval = company[key].rest_hour
                    let rest_start = parseInt(rest_interval[0].split(":")[0]) * 60 + parseInt(rest_interval[0].split(":")[1]);
                    let rest_end = parseInt(rest_interval[1].split(":")[0]) * 60 + parseInt(rest_interval[1].split(":")[1]);

                    // work_time內為綠色、gold_time內為黃色、red_time內為紅色、rest_time內為黑色
                    if (timeInMinutes >= work_start && timeInMinutes < work_end) {
                        color="green";
                        company[key].color=color;
                        } 
                    else if(timeInMinutes >= gold_start && timeInMinutes < gold_end){
                        color="yellow";
                            company[key].color=color;
                        }
                    else if(timeInMinutes >= rest_start || timeInMinutes < rest_end){
                        color="black";
                            company[key].color=color;
                        }
                    else{
                        color="red";
                        company[key].color=color;
                        }
                        
                    company_data = `${key} <br>時區:${layer_name}<br>時間: ${layer_date_obj.getFullYear()}年${layer_date_obj.getMonth()}月${layer_date_obj.getDay()}日 ${hours_str}:${minutes_str}:${seconds_str}`
                    
       
                    break;
                };
            };            

            // 建立 circle 并加入图层组
            let circleMarker = L.circleMarker([lat, lng], {riseOnHover: true, color: color}).bindTooltip(company_data);
            layerGroup.addLayer(circleMarker);
        };
    },{ immediate: true }); // immediate: true表示網頁初始化时立即调用



});

// onUpdated(() => {
//     store.commit('update_company_data', company);
//     console.log(store.state.company);
// });

onBeforeUnmount(() => {
    store.commit('update_company_data', company);
    store.commit('update_selected_company', company_checked);   
    store.commit('update_tz_moment', Zone_select_moment);
    store.commit('update_selected_zone', selectedTimeZone.value);
});
</script>


<template>
<!-- Map.vue -->
<div class=" w-full flex flex-col md:flex-row md:h-[750px] lg:flex-row">
    <!-- Map Section -->    
    <div class="bg-white border rounded-lg flex justify-center  p-6 mb-6 xl:mb-0  w-full h-[550px] md:w-1/2 md:h-full lg:w-2/3">
        <div id="map_container" class="relative z-0 flex-grow w-full md:w-full lg:w-2/3"> 
        <!-- <div id="map_container" class="relative h-[700px] w-[1000px] z-0">  -->
            <div id="map" class="lg:w-full"></div>
            <div id="select_area" >
                <!-- 時區 -->
                <div id="timezone_select_area">
                    <h3 for="tz">本地時區</h3>
                    <select id="tz" v-model="selectedTimeZone" >
                        <option v-for="(zone_name, index) in uniqueTimeZoneList" :key="index" :value="zone_name" >
                            {{ zone_name }}
                        </option>
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
                        <input type="range" id="time" v-model="selectedSeconds" min="0" max="86400" step="900" style="height: 30%;" >    
                        <button @click="incrementMins " style="height: 2vh; width: 2vh; display: flex; align-items: center; justify-content: center;">
                            <img src="../assets/right.png" style="height: 2vh; width: 2vh;">            
                        </button>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <!-- Site Office Section -->
    <div class="bg-white border rounded-lg p-6 mb-6 xl:mb-0 w-full md:h-full md:w-1/2 md:overflow-auto lg:w-1/3">  
        <div class="flex justify-center items-center">
             <button @click="isShow = true" class="font-extrabold text-[#253fae] bg-transparent hover:bg-[#FAF4FF] border rounded-lg p-2">
                + Eddit office
            </button>
        </div>
        <div v-for="(value, site) in company" :key="site" >
            <div v-if="company_checked[site]"   :class="company[site].color+' border rounded-lg p-1 pt-5 m-1 mb-2'" >
                
                <!-- 時間 -->
                <div class="flex justify-between">
                <label class="text-4xl font-bold leading-tight" v-text="company[site].time"></label>
                <label class="text-sm font-bold leading-tight" v-text="site"></label>
                </div>
                <!-- 分隔線 -->
                <div class="border-t-2 border-current mt-1 mb-4"></div>

                
                <div class="flex justify-between">
                    <label class="text-sm font-bold mt-1 mb-4" v-text="company[site].week_day"></label>
                    <label class="text-sm font-bold mt-1 mb-4" v-text="value.time_zone"></label>
                </div>
        
            </div>
        </div>

    </div>

    <!-- 燈箱：設定office -->
    <div class="modal-mask" :style="modalStyle">
    <div class="modal-container"  @click.self="toggleModal">
        <div class="modal-mask" :style="modalStyle">
            <div class="modal-container"  @click.self="toggleModal">
                <div class="modal-body overflow-auto h-1/2 w-1/2 md:h-1/3 md:w-1/3">      
                    <h3 class="inline">Edit office</h3>
                    <br>
                    <!-- 取消全選 -->
                    <div class="border rounded-lg p-1 m-1 mb-2 inline-block">
                        <input type="checkbox" :value="all_company_checked" v-model="all_company_checked" >
                        <label v-if="all_company_select===true" class="text-sm" >取消全選</label>
                        <label v-else class="text-sm">全選</label>
                    </div>     
                    <!-- 各office勾選方格 -->
                    <div class="flex flex-wrap">
                        <div v-for="(value, site) in company" :key="site" class="border rounded-lg p-1 m-1 mb-2">
                            <div>
                                <input 
                                    type="checkbox" 
                                    :id="site" 
                                    :value="value"
                                    v-model="company_checked[site]"
                                >
                                <label :for="site" class="text-sm" v-text="site"></label>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>
    </div>

   


</div>
    
</template>



<style scoped>

#map{
    position: absolute;
    background: #AAD3DF;
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


#timezone_select_area, #date_select_area, .time_select_area {
  flex-basis: 32%;
  margin-bottom: 15px;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
}

/* #time-control_area {
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin: 0%;
    padding: 0;
  }  */


/* .site_card_area {
    margin-top: 10px;
    margin-bottom: 10px;
    text-align: left; 
    border-radius: 5px;
    border: 1px solid black;
} */

.red{
    background: linear-gradient(to right, rgb(255, 240, 252), rgb(255, 199, 255)); color: rgb(38, 40, 36); --va-0-stripe-color-computed: #253fae;
}

.yellow{
    background: linear-gradient(to right, rgb(255, 238, 112), rgb(249, 197, 78)); color: rgb(38, 40, 36); --va-0-stripe-color-computed: #253fae;
}

.green{
    background: linear-gradient(to right, rgb(41, 250, 250), rgb(5, 214, 158)); color: rgb(38, 40, 36); --va-0-stripe-color-computed: #253fae;
}


/* .clock_time{
    font-size:2.5rem;
    margin: 5 2;
    font-weight:700;
    line-height:3rem
} */

/* .clock_time{
    font-size:2rem;
    margin: 5rem 0 0 .25rem;
    font-weight:700;
    line-height:2rem;
} */


.modal-mask {
  position: fixed;
  z-index: 10;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  display: table;
  background-color: rgba(0, 0, 0, .5);
  transition: opacity .3s ease;
  /* z-index: 999; */
}

.modal-container {
  cursor: pointer;
  display: table-cell;
  vertical-align: middle;
}

.modal-body {
  cursor: auto;
  display: block;
  margin: 0 auto;
  padding: 2rem;
  background-color: #fff;
}
</style>
