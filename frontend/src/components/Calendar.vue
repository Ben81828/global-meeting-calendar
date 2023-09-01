<script setup>
import { ref, reactive, computed, watch } from 'vue';
import { useStore } from 'vuex';
// timezone
import moment from 'moment-timezone';
import { convertDistance } from '@turf/turf';

// 溝通後端
import axios from "axios";

const store = useStore();

let months_short = ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"];
let weekdays_long = ["Sunday","Monday","Tuesday","Wednesday","Thursday","Friday","Saturday"];
let weekdays_short = ["Sun","Mon","Tue","Wed","Thu","Fri","Sat"];

let select_moment = store.state.Zone_select_moment? new Date(store.state.Zone_select_moment.toISOString()): new Date();


// 目前行事曆主要的年月
let year = ref(select_moment.getFullYear());
let month = ref(select_moment.getMonth() + 1); 


// 整理日曆cell內的顏色、日期
let date_cells = ref({});

const month_cal = (command) => {

    // 先移到當月1號。因為如3/30直接向前平移一個月會到2/30，因不存在導致停留於3/1。月份會仍在3月。
    select_moment.setDate(1);
    
    // moment向前或向後平移一個月
    if(command==="+1"){
        select_moment.setMonth(select_moment.getMonth()+1);
    }
    else if(command==="-1"){
        select_moment.setMonth(select_moment.getMonth()-1);
    }

    // 更新年月
    year.value = select_moment.getFullYear();
    month.value = select_moment.getMonth() + 1;
 
};


// 依據month的變化，去和後端要calendar中每個cell的資訊，並渲染
watch( month ,() => {

   // 取得當前所選年月，建立calendar此月1號的Date物件pointer
   let cell_pointer = new Date(year.value, month.value - 1);
    // 計算下一個月，若下個月>12表示為1月。計算後記錄到next_month
    let next_month = cell_pointer.getMonth() + 2 > 12 ? 1 : cell_pointer.getMonth() + 2; //getMonth()會為月數少1。+2用來表示下個月，過12月則為1月
    // 將cell_pointer移到該月1號前最近的星期天
    cell_pointer.setDate(cell_pointer.getDate() - cell_pointer.getDay());
    // 將cell_pointer複製給cell_pointer做紀錄
    cell_pointer = new Date(cell_pointer.getTime());

    // 建立一個物件，從cell_pointer往後迭帶，存放日期(不含月)及顏色(若該日期為當月為白色，否則為灰色)，直到當月最後一日往後最近的週六
    let cells = {};
    let row_num = 0;
    let col_num = 0;
    while(cell_pointer.getMonth()+1!==next_month||cell_pointer.getDay()!==0){
      let cell_year = cell_pointer.getFullYear();
      let cell_month = cell_pointer.getMonth() + 1;
      let cell_date = cell_pointer.getDate();
      let cell_color = cell_pointer.getMonth() == month.value - 1 ? "white" : "gray";
      cells[row_num] = cells[row_num] || {};
      cells[row_num][col_num] = {"year":cell_year,"month":cell_month, "date":cell_date, "color":cell_color, "holiday":""};
      cell_pointer.setDate(cell_pointer.getDate() + 1);
      col_num++;
      if(col_num == 7){
          col_num = 0;
          row_num++;
      }
    }
    
  date_cells.value = cells;

  // 製作給後端查詢放假補班資料的query物件
  let query = {};
  query.month = {"pre":cell_pointer.getMonth(), "this":month.value, "next":next_month};
  query.year = {"pre":cell_pointer.getFullYear(), "this":year.value, "next":next_month>month.value? year.value: year.value+1 };
  let countrys = ["AUHQ","AUCN"];
  let query_countrys = {}; for(let i=0; i<countrys.length; i++){query_countrys[i] = countrys[i];  }
  query.countrys = query_countrys;

  // 後續要存放假日資訊的陣列
  let holiday_obj_arr = [];

  // 向後端query放假補班資料，並合併到cell資訊中
  axios
    .post("/calendar", query)
    .then((res) => {

      holiday_obj_arr = res.data;  // [{year: '2023', month: '10', date: '1', holiday: '国庆节', holiday_type: '放假', …}, {year: '2023', month: '10', date: '10', holiday: '國慶日', holiday_type: '放假', …}
    })
    .catch((err) => {
      console.log(err);
    })
    .finally(() => {
      // 迭帶date_cells
      for(let row_num in date_cells.value){
        for(let col_num in date_cells.value[row_num]){

          let sites_holiday_arr = [];
          for(let holiday_obj of holiday_obj_arr){
            // 檢查每個cell的year、month、date是否跟holiday_obj_arr內的每個holiday_obj的year、month、date相同
            // 若相同則將holiday_obj的holiday、holiday_type、country資訊存入sites_holiday_arr"
            if(date_cells.value[row_num][col_num].year==holiday_obj.year && date_cells.value[row_num][col_num].month==holiday_obj.month && date_cells.value[row_num][col_num].date==holiday_obj.date){
              let info = {"holiday_name":holiday_obj.holiday, "holiday_type":holiday_obj.holiday_type, "holiday_country":holiday_obj.country};
              sites_holiday_arr.push(info)
            }
          }
          date_cells.value[row_num][col_num].holiday = sites_holiday_arr;
        }
      }
    });

},{ immediate: true });




const cell_color = (color) => {
    if(color==="white"){
        return "border p-1 h-40 xl:w-40 lg:w-30 md:w-30 sm:w-20 w-10 overflow-auto transition cursor-pointer duration-500 ease hover:bg-gray-300"
    }
    else if(color==="gray"){
        return "border bg-gray-100 p-1 h-40 xl:w-40 lg:w-30 md:w-30 sm:w-20 w-10 overflow-auto transition cursor-pointer duration-500 ease hover:bg-gray-300"
    }
    
}

</script>

<template>

  <!-- <body class="bg-gray-200"> -->

    <div class="container mx-auto mt-10 overflow-auto">
    <div class="wrapper bg-white rounded shadow w-full ">
      <div class="header flex justify-between border-b p-2">
        <!-- 標名: 年、月 -->
        <span class="text-lg font-bold" v-text="select_moment.getFullYear()+' '+months_short[select_moment.getMonth()]">
        </span>
        <div class="buttons" >
          <button class="p-1" @click="month_cal('-1')">
              <svg width="1em" fill="gray" height="1em" viewBox="0 0 16 16" class="bi bi-arrow-left-circle"  xmlns="http://www.w3.org/2000/svg">
                <path fill-rule="evenodd" d="M8 15A7 7 0 1 0 8 1a7 7 0 0 0 0 14zm0 1A8 8 0 1 0 8 0a8 8 0 0 0 0 16z"/>
                <path fill-rule="evenodd" d="M8.354 11.354a.5.5 0 0 0 0-.708L5.707 8l2.647-2.646a.5.5 0 1 0-.708-.708l-3 3a.5.5 0 0 0 0 .708l3 3a.5.5 0 0 0 .708 0z"/>
                <path fill-rule="evenodd" d="M11.5 8a.5.5 0 0 0-.5-.5H6a.5.5 0 0 0 0 1h5a.5.5 0 0 0 .5-.5z"/>
              </svg>
          </button>
          <button class="p-1" @click="month_cal('+1')">
              <svg width="1em" fill="gray" height="1em" viewBox="0 0 16 16" class="bi bi-arrow-right-circle"  xmlns="http://www.w3.org/2000/svg">
                <path fill-rule="evenodd" d="M8 15A7 7 0 1 0 8 1a7 7 0 0 0 0 14zm0 1A8 8 0 1 0 8 0a8 8 0 0 0 0 16z"/>
                <path fill-rule="evenodd" d="M7.646 11.354a.5.5 0 0 1 0-.708L10.293 8 7.646 5.354a.5.5 0 1 1 .708-.708l3 3a.5.5 0 0 1 0 .708l-3 3a.5.5 0 0 1-.708 0z"/>
                <path fill-rule="evenodd" d="M4.5 8a.5.5 0 0 1 .5-.5h5a.5.5 0 0 1 0 1H5a.5.5 0 0 1-.5-.5z"/>
              </svg>
          </button>
        </div>
      </div>
      
      <table class="w-full">
        <!-- 表頭: 星期 -->
        <thead>
          <tr>
            <th v-for="num in 8" :key="num" class="p-2 border-r h-10 xl:w-40 lg:w-30 md:w-30 sm:w-20 w-10 xl:text-sm text-xs" >
                <span v-text="weekdays_long[num-1]" class="xl:block lg:block md:block sm:block hidden"></span>
                <span  v-text="weekdays_short[num-1]" class="xl:hidden lg:hidden md:hidden sm:hidden block"></span>
            </th>
          </tr>
        </thead>
        <!-- Calendar content -->
        <tbody>
          <tr class="text-center h-20" v-for="(week_days, row_num) in date_cells" :key="row_num" >
            <td v-for="( content, week_day) in week_days" :key="week_day" :class="cell_color(content.color)">
                <div class="flex flex-col h-40 mx-auto xl:w-40 lg:w-30 md:w-30 sm:w-full w-10 mx-auto overflow-hidden">
                    <div class="top h-5 w-full">
                    <span class="text-gray-500" v-text="content.date"></span>
                    </div>
                    <div class="bottom flex-grow h-30 py-1 w-full cursor-pointer" v-for="(info, idx) in content.holiday" :key="idx">
                        
                        <div
                            v-if="info.holiday_type==='补班'"
                            class="event bg-green-400 text-white rounded p-1 text-sm mb-1"
                        >
                            <div class="event-name">
                            ({{info.holiday_type}}){{info.holiday_name}}
                            </div>
                            <div class="time">
                            {{info.holiday_country}}
                            </div>
                        </div>
                        <div
                            v-else
                            class="event bg-purple-400 text-white rounded p-1 text-sm mb-1"
                        >
                            <div class="event-name">
                            ({{info.holiday_type}}){{info.holiday_name}}
                            </div>
                            <div class="time">
                              {{info.holiday_country}}
                            </div>
                        </div>
                    </div>
                </div>
            </td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>





</template>


<style scoped></style>



