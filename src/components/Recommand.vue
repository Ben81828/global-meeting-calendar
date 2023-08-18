<script setup>
import { computed } from 'vue';
import { useStore } from 'vuex';
import moment from 'moment-timezone'; // timezone



const store = useStore();

// 各公司資訊物件
let company = store.state.company;
let company_selected = store.state.selected_company;
console.log(company_selected)

// 選定時區物件回到當天00:00:00
let select_moment_obj = store.state.Zone_select_moment;
let select_hours = select_moment_obj.hours()
let select_mins = select_moment_obj.minutes()
let select_seconds =  select_moment_obj.seconds()
let select_0hr_obj = select_moment_obj.subtract(select_hours, 'hours').subtract(select_mins, 'minutes').subtract(select_seconds, 'seconds')

// 建立各 site 圖標時，會從company中取出座標，並依座標檢查它在timezoneLayers中所在時區，用date_obj去計算其時間，並將時間放回company中
for (let key in company) {
    // 在 checkbox 被打勾的才進行後續建立圖標
    if (company_selected[key] !== true){ continue };

    let this_company = company[key];
    
    // 把work time和gold time转换为分钟的总量
    let this_work_interval = this_company.work_hour
    let this_work_start = parseInt(this_work_interval[0].split(":")[0]) * 60 + parseInt(this_work_interval[0].split(":")[1]);
    let this_work_end = parseInt(this_work_interval[1].split(":")[0]) * 60 + parseInt(this_work_interval[1].split(":")[1]);

    // 把work time和gold time转换为分钟的总量
    let this_gold_interval = this_company.gold_hour
    let this_gold_start = parseInt(this_gold_interval[0].split(":")[0]) * 60 + parseInt(this_gold_interval[0].split(":")[1]);
    let this_gold_end = parseInt(this_gold_interval[1].split(":")[0]) * 60 + parseInt(this_gold_interval[1].split(":")[1]);

    // 把work time和rest time转换为分钟的总量
    let this_rest_interval = this_company.rest_hour
    let this_rest_start = parseInt(this_rest_interval[0].split(":")[0]) * 60 + parseInt(this_rest_interval[0].split(":")[1]);
    let this_rest_end = parseInt(this_rest_interval[1].split(":")[0]) * 60 + parseInt(this_rest_interval[1].split(":")[1]);

    // 複製select_0hr_obj，並初始轉為此時區的時間物件
    let this_zone_time_obj = moment(select_0hr_obj).tz(this_company.time_zone);

    let times = [];
    let colors = [];

    for (let add_30mins=0; add_30mins<48; add_30mins++){        
        
        let this_zone_hours = this_zone_time_obj.hours();
        let this_zone_mins = this_zone_time_obj.minutes();   
        let this_timeInMinutes = this_zone_hours * 60 + this_zone_mins;

        let this_time_color
         // work_time內為綠色、gold_time內為黃色、red_time內為紅色、rest_time內為黑色
        if (this_timeInMinutes >= this_work_start && this_timeInMinutes < this_work_end) {
                this_time_color="green";
            } 
        else if(this_timeInMinutes >= this_gold_start && this_timeInMinutes < this_gold_end){
                this_time_color="yellow";
            }
        else if(this_timeInMinutes >= this_rest_start || this_timeInMinutes < this_rest_end){
                this_time_color="black";
            }
        else{
                this_time_color="red";
            }
        
        colors.push(this_time_color);
        times.push(this_zone_time_obj.format());

        // 增加30分鐘
        this_zone_time_obj.add( 30, 'minutes');
        
    };
    company[key].day_times = times;
    company[key].day_colors = colors;

};

let time_stamps = Array.from({length: 48}, (_, i) => i % 2 === 0 ? (i/2).toString() : "");

</script>


<template>

    <table class="text-base text-[#646464] w-11/12">
        <thead class=" text-[#005087]">
        <tr>
            <th class="" >
            <div>location</div>
            </th>
            <th class="" v-for="(time_stamp, idx) in time_stamps" :key="idx">
            <div v-text="time_stamp" ></div>
            </th>
        </tr>
        </thead>

        <tbody v-for="(selected, site) in company_selected" :key="site" :value="selected">
            <tr v-if="selected">
                <td class="border text-left">
                    {{site}}
                </td>

                <td v-for="(color, idx) in company[site].day_colors"  :key="idx" class="border">
                    <div v-if="color === 'green'" class="bg-green-500 flex items-center justify-center">
                        <div class="bg-green-500 w-4 h-4"></div>
                    </div>
                    <div v-if="color === 'yellow'" class=" bg-yellow-500 flex items-center justify-center">
                        <div class="bg-yellow-500 w-4 h-4"></div>
                    </div>
                    <div v-if="color === 'red'" class=" bg-red-500 flex items-center justify-center">
                        <div class="bg-red-500 w-4 h-4"></div>
                    </div>
                    <div v-if="color === 'black'" class="bg-black flex items-center justify-center">
                        <div class="bg-black w-4 h-4"></div>
                    </div>
                </td>
                

            </tr>

        </tbody>

    </table>

</template>


<style>

</style>