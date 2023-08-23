import './assets/style.css'

import { createApp } from 'vue'
import App from './App.vue'


import {route} from './router' // 載入配置檔

import { createStore } from 'vuex'


let company_data = {
    "友達_ATC":{
        "location": [24.774162306624227, 121.01954364063755],
        "year":null,
        "month":null,
        "date":null,
        "time":null,
        "time_zone":null,
        "work_hour":[ "08:00", "17:00"],
        "gold_hour":[ "19:00", "21:00"],
        "rest_hour":[ "23:00", "07:00"],
        "color":null,
        "day_times":null,
        "day_colors":null,
    },
    "友達_GRC":{
        "location": [24.777049544180894, 121.00818840488583],
        "year":null,
        "month":null,
        "date":null,
        "time":null,
        "time_zone":null,
        "work_hour":[ "08:00", "17:00"],
        "gold_hour":[ "19:00", "21:00"],
        "rest_hour":[ "23:00", "07:00"],
        "color":null,
        "day_times":null,
        "day_colors":null,
    },
    "友達_昆山":{
        "location": [31.3886250399072, 121.08193142979769],
        "year":null,
        "month":null,
        "date":null,
        "time":null,
        "time_zone":null,
        "work_hour":[ "08:00", "17:00"],
        "gold_hour":[ "19:00", "21:00"],
        "rest_hour":[ "23:00", "07:00"],
        "color":null,
        "day_times":null,
        "day_colors":null,
    },
    "友達_蘇州":{
        "location": [31.333195291328046, 120.70341679091685],
        "year":null,
        "month":null,
        "date":null,
        "time":null,
        "time_zone":null,
        "work_hour":[ "08:00", "17:00"],
        "gold_hour":[ "19:00", "21:00"],
        "rest_hour":[ "23:00", "07:00"],
        "color":null,
        "day_times":null,
        "day_colors":null,
    },
    "友達_廈門":{
        "location": [22.66143158161194, 114.07112822179445],
        "year":null,
        "month":null,
        "date":null,
        "time":null,
        "time_zone":null,
        "work_hour":[ "08:00", "17:00"],
        "gold_hour":[ "19:00", "21:00"],
        "rest_hour":[ "23:00", "07:00"],
        "color":null,
        "day_times":null,
        "day_colors":null,
    },
    "友達_東京":{
        "location": [35.651338998648264, 139.74751899807922],
        "year":null,
        "month":null,
        "date":null,
        "time":null,
        "time_zone":null,
        "work_hour":[ "08:00", "17:00"],
        "gold_hour":[ "19:00", "21:00"],
        "rest_hour":[ "23:00", "07:00"],
        "color":null,
        "day_times":null,
        "day_colors":null,
    },
    "友達_大阪":{
        "location": [34.73360259630881, 135.49247715582405],
        "year":null,
        "month":null,
        "date":null,
        "time":null,
        "time_zone":null,
        "work_hour":[ "08:00", "17:00"],
        "gold_hour":[ "19:00", "21:00"],
        "rest_hour":[ "23:00", "07:00"],
        "color":null,
        "day_times":null,
        "day_colors":null,
    },
    "友達_韓國":{
        "location": [37.293959032600405, 127.0493198502576],
        "year":null,
        "month":null,
        "date":null,
        "time":null,
        "time_zone":null,
        "work_hour":[ "08:00", "17:00"],
        "gold_hour":[ "19:00", "21:00"],
        "rest_hour":[ "23:00", "07:00"],
        "color":null,
        "day_times":null,
        "day_colors":null,
    },
    "友達_新加坡":{
        "location": [1.3607346922837744, 103.92969799623016],
        "year":null,
        "month":null,
        "date":null,
        "time":null,
        "time_zone":null,
        "work_hour":[ "08:00", "17:00"],
        "gold_hour":[ "19:00", "21:00"],
        "rest_hour":[ "23:00", "07:00"],
        "color":null,
        "day_times":null,
        "day_colors":null,
    },
    "友達_底特律":{
        "location": [42.468266506783976, -83.41422311520508],
        "year":null,
        "month":null,
        "date":null,
        "time":null,
        "time_zone":null,
        "work_hour":[ "08:00", "15:00"],
        "gold_hour":[ "19:00", "21:00"],
        "rest_hour":[ "23:00", "07:00"],
        "color":null,
        "day_times":null,
        "day_colors":null,
    },
    "友達_德國":{
        "location": [48.6895943965471, 9.003747399999998],
        "year":null,
        "month":null,
        "date":null,
        "time":null,
        "time_zone":null,
        "work_hour":[ "08:00", "15:00"],
        "gold_hour":[ "19:00", "21:00"],
        "rest_hour":[ "23:00", "07:00"],
        "color":null,
        "day_times":null,
        "day_colors":null,
    },
    "友達_荷蘭":{
        "location": [52.39640932035231, 4.850351413494435],
        "year":null,
        "month":null,
        "date":null,
        "time":null,
        "time_zone":null,
        "work_hour":[ "08:00", "15:00"],
        "gold_hour":[ "19:00", "21:00"],
        "rest_hour":[ "23:00", "07:00"],
        "color":null,
        "day_times":null,
        "day_colors":null,
    },
    "友達_斯洛伐克":{
        "location": [48.886123822116545, 17.9956080491438],
        "year":null,
        "month":null,
        "date":null,
        "time":null,
        "time_zone":null,
        "work_hour":[ "08:00", "15:00"],
        "gold_hour":[ "19:00", "21:00"],
        "rest_hour":[ "23:00", "07:00"],
        "color":null,
        "day_times":null,
        "day_colors":null,
    }
};

// 初始化全選所有的公司
let selected_company = Object.keys(company_data).reduce(function(acc, key) {
    acc[key] = true;
    return acc;
}, {})

// 创建一个新的 store 实例
const store = createStore({
    state () {
      return {
        is_toggle_open:false,
        company:company_data,
        Zone_select_moment:null,
        selected_zone:null,
        selected_company:selected_company,
      }
    },
    
    mutations: {

        update_toggle_state (state, toggle_state) {
            state.is_toggle_open = toggle_state;
        },

        update_company_data (state, new_company_data) {
            state.company = new_company_data;
        },

        update_tz_moment(state, new_tzMoment_obj) {
            state.Zone_select_moment =  new_tzMoment_obj;
        },

        update_selected_zone(state, new_selected_zone) {
            state.selected_zone =  new_selected_zone;    
        },

        update_selected_company(state, new_selected_company) {
            state.selected_company =  new_selected_company;    
        },
    }
  })



createApp(App).use(route).use(store).mount('#app')



