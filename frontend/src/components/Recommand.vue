<script setup>
import { onBeforeUnmount } from 'vue';
import { useStore } from 'vuex';
import moment from 'moment-timezone'; // timezone


const store = useStore();

// 時區資訊物件
// 選定的時區
let selected_zone = store.state.selected_zone;
// 各公司資訊物件
let company = store.state.company;
let company_selected = store.state.selected_company;
let selected_company_array = Object.keys(company_selected).filter(site => company_selected [site]);

// 選定時區物件回到當天00:00:00
let select_moment_obj = store.state.Zone_select_moment.clone(); // 2021-09-01T00:00:00+08:00
let select_hours = select_moment_obj.hours() // 0~23
let select_mins = select_moment_obj.minutes() // 0~59
let select_seconds =  select_moment_obj.seconds() // 0~59
let select_0hr_obj = select_moment_obj.subtract(select_hours, 'hours').subtract(select_mins, 'minutes').subtract(select_seconds, 'seconds') // 00:00:00~23:59:59

// 建立各 site 圖標時，會從company中取出座標，並依座標檢查它在timezoneLayers中所在時區，用date_obj去計算其時間，並將時間放回company中
for (let key in company) {
    // 在 checkbox 被打勾的才進行後續建立圖標
    if (company_selected[key] !== true){ continue };

    let this_company = company[key];
    
    // 把work time和stretch time转换为分钟的总量
    let this_work_interval = this_company.work_hour
    let this_work_start = parseInt(this_work_interval[0].split(":")[0]) * 60 + parseInt(this_work_interval[0].split(":")[1]);
    let this_work_end = parseInt(this_work_interval[1].split(":")[0]) * 60 + parseInt(this_work_interval[1].split(":")[1]);

    // 把work time和stretch time转换为分钟的总量
    let this_stretch_interval = this_company.stretch_hour
    let this_stretch_start = parseInt(this_stretch_interval[0].split(":")[0]) * 60 + parseInt(this_stretch_interval[0].split(":")[1]);
    let this_stretch_end = parseInt(this_stretch_interval[1].split(":")[0]) * 60 + parseInt(this_stretch_interval[1].split(":")[1]);

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
         // work_time內為綠色、stretch_time內為黃色、red_time內為紅色、rest_time內為黑色
        if (this_timeInMinutes >= this_work_start && this_timeInMinutes < this_work_end) {
                this_time_color="green";
            } 
        else if(this_timeInMinutes >= this_stretch_start && this_timeInMinutes < this_stretch_end){
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

// ["0","","1","",.....]
let time_stamps = Array.from({length: 48}, (_, i) => i % 2 === 0 && i < 20 ? "0" + (i/2).toString() : i % 2 === 0 && i >= 20 ? (i/2).toString() : "" );



// 依照時段顏色塞進表格的html樣式
let getColorClass = (this_color, idx, colorList) => {

  // 給背景色
  let classString = "";
  if (this_color=="black"){
    classString += `group bg-${this_color} flex items-center justify-center h-5/6 `;
  }
  else{
    classString +=`group bg-${this_color}-500 flex items-center justify-center h-full `;
  }
 
  // 第一個或最後一個給圓角
  let pre_pointer = idx-1;
  let next_pointer = idx+1;

  if (idx===0||colorList[pre_pointer]!==this_color){ //當為列表第0個或和前一個顏色不同，代表是此色第一個，所以加左圓角
    classString +=" rounded-l-lg"
  }
  else if(idx===colorList.length||colorList[next_pointer]!==this_color){ //當為列表最後一個或和後一個顏色不同，代表是此色最後一個，所以加右圓角
    classString +=" rounded-r-lg"
  }

  return classString;
};





/////////推薦

let time_color_obj = {};
time_color_obj.header = selected_company_array;
time_color_obj.body = {};

for(let time_pointer=0; time_pointer<48; time_pointer++){

  let this_time_colors = [];
  let color_counter = {
      "green":0,
      "yellow":0,
      "red":0,
      "black":0
  };
  for( let site of time_color_obj.header ){
    let this_time_color = company[site].day_colors[time_pointer];
    this_time_colors.push(this_time_color);
    color_counter[this_time_color] += 1;

  }
  let this_time_hour = Math.floor((time_pointer*30)/60) < 10 ? `0${Math.floor((time_pointer*30)/60)}` : `${Math.floor((time_pointer*30)/60)}`;
  let this_time_min = time_pointer%2 !== 0 ? "30" : "00" ;
  let this_time = this_time_hour + ':' + this_time_min;
  time_color_obj.body[this_time] = {"colors":this_time_colors,
                                    "color_count":color_counter,
                                    "eliminate_order":[],
                                  };
}


// 推薦的遞迴函數
function compareColors(time_color_obj) {

  let time_color_obj_copy = JSON.parse(JSON.stringify(time_color_obj));

  // 物件空就結束
  if( Object.keys(time_color_obj_copy).length === 0){
      return [];
  }

  else{    
    let black_bucks_obj = {};//有黑的time:color_list放這
    let red_bucks_obj = {};//無黑有紅的time:color_list放這
    let yellow_bucks_obj= {};//無黑無紅有黃的time:color_list放這

    // 目標要回傳recommand_list
    let recommand_list = [];//無黑無紅無黃的time放這(只有綠或空字串)
    
    for( let time in time_color_obj_copy){   
       
        
      let color_list = time_color_obj_copy[time].colors; 

      if(color_list.includes("black")){
        // time_color_obj[time].eliminate_order.push("black");
        color_list.splice(color_list.indexOf("black"), 1);//移除一個顏色
        black_bucks_obj[time] = {"colors":color_list};//放進他的籃子
      }
      else if(color_list.includes("red")){
        // time_color_obj[time].eliminate_order.push("red");
        color_list.splice(color_list.indexOf("red"), 1);
        red_bucks_obj[time] = {"colors":color_list};
      }
      else if(color_list.includes("yellow")){        
        // time_color_obj[time].eliminate_order.push("yellow");
        color_list.splice(color_list.indexOf("yellow"), 1);
        yellow_bucks_obj[time] = {"colors":color_list};
      }
      else {
        recommand_list.push(time)
      }
    }

  // 最終要排序的推薦列，依照順序去遞迴。concat是js的串接array的方法
  recommand_list = recommand_list.concat(compareColors(yellow_bucks_obj)).concat(compareColors(red_bucks_obj)).concat(compareColors(black_bucks_obj))

  return recommand_list
  }
}
let recommend_time_list = compareColors(time_color_obj.body);


onBeforeUnmount(() => {
    store.commit('update_company_data', company);
    store.commit('update_selected_company', company_selected);   
    store.commit('update_selected_zone', selected_zone);
});


</script>


<template>

<div class=" w-full flex flex-col md:flex-row md:h-[750px] lg:flex-row ">
               
  <div class="bg-white border rounded-lg flex justify-center  p-6 mb-6 w-full h-[550px] md:w-1/2 md:h-full lg:w-2/3">

    <div class="overflow-auto">
      <table class="">
        <colgroup>
          <col class="fixed-col" /> <!-- Width for the first column -->
          <col v-for="(time_stamp, idx) in time_stamps" :key="idx" class="dynamic-col" />
        </colgroup>
        <tbody>
          <tr class=" ">
            <th class="text-[#005087] p-0 bg-white sticky left-0 top-0 z-[30]">              
              <div class="text-right" v-text="selected_zone"></div>
              <div class="text-right">Time</div>
            </th>
            <th v-for="(time_stamp, idx) in time_stamps" :key="idx" :class="' bg-white sticky top-0 z-[20] custom-td ' + (time_stamp !== '' ? ' border-l border-gray-400 ' : '')">
    
              <div v-text="(time_stamp !== '' ? time_stamp : '&nbsp&nbsp&nbsp&nbsp')" class="px-0 " ></div>
     
            </th>
          </tr>     
          <tr v-for="(site, idx) in selected_company_array" :key="idx" class=" bg-white">
            <td class="text-left p-0 bg-white sticky left-0 z-[20]">{{ site }}</td>
            <td v-for="(color, idx) in company[site].day_colors" :key="idx" :class="'z-[0] custom-td '+(idx%2 === 0 ? ' border-l border-gray-400' : '')">
              <div :class="getColorClass(color,idx,company[site].day_colors)">
                <div class="bg-[color] relative p-2">
                  <span
                    class="hidden group-hover:inline-block text-sm text-gray-500 rounded-md bg-yellow-100 p-1 top-0 left-full transform translate-y-[calc(-100%+2px)] translate-x-2 w-auto whitespace-nowrap text-left z-30 absolute "
                    style="word-wrap: break-word;"
                  >
                    當地時區:{{ company[site].time_zone }}
                    <br />
                    當地日期:{{ company[site].day_times[idx].split("T")[0] }}
                    <br />
                    當地時間:{{ company[site].day_times[idx].split("T")[1].slice(0,8) }}
                    <br />
                  </span>
                </div>
              </div>
            </td>
          </tr>

        </tbody>
      </table>
    </div>
  </div>
   
  <div class="bg-white border rounded-lg p-6 mb-6 xl:mb-0 w-full md:h-full  md:w-1/2 md:overflow-auto lg:w-1/3">
    <div class="text-left text-[#005087]" v-text="'Recommand'"></div>
    <div v-for="(time, idx) in recommend_time_list" :key="idx" >

      
      <div :class="'bg-green'+' border rounded-lg p-1 pt-5 m-1 mb-2'" >

        <!-- 父 -->
        <div class="grid grid-cols-2">

          <!-- 子1 -->
          <label class="text-4xl font-bold leading-tight " v-text="time"></label>

          <!-- 子2 -->
          <div class="flex justify-end"> 
            <div v-for="(count, color) in time_color_obj.body[time].color_count" :key="color" :value="count" class=""> 
              <div class="bg-green-500 w-5 h-5 rounded-full mr-2" v-if="color==='green'"></div>
              <div class="bg-yellow-500 w-5 h-5 rounded-full mr-2" v-if="color==='yellow'"></div>
              <div class="bg-red-500 w-5 h-5 rounded-full mr-2" v-if="color==='red'"></div> 
              <div class="bg-black w-5 h-5 rounded-full mr-2" v-if="color==='black'"></div> 
              <span v-text="count" class=""></span> 
            </div>
          </div>
        </div>

      <div class="border-t-2 border-current mt-1 mb-4"></div> <!-- 分隔線 -->
        <div class="flex justify-between">
            <label class="text-sm font-bold mt-1 mb-4" v-text="selected_zone+' Time'"></label>
    
        </div>

      </div>
    </div>
  </div>

</div>




</template>

<style scoped>

table {
  display: flex;
  /* flex-direction: column; */
  width: 100%;

}

thead {
  display: contents; 
}

th,
td {
  flex: 1;
  min-width: 0; /* Allow cell content to shrink */
  text-align: center;
  padding: 0.5rem;
  white-space: nowrap; /* Prevent text wrapping */
}

@media (min-width: 640px) {
  /* Apply different styles for screens wider than 640px */
  th,
  td {
    padding: 0.5rem;
  }
}

.custom-td {
  padding: 0 !important;
}
</style>