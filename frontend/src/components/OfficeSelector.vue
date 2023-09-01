<script setup>

import { ref, watch, computed, nextTick} from 'vue';

// 溝通後端
import axios from "axios";

// 導入tz-lookup
import tzlookup from "tz-lookup";

// store
import { useStore } from 'vuex';
const store = useStore();

// 公司資料
let company = computed(() => {return store.state.company});

// 物件: 已被選的公司。各公司按鈕value會on這個物件key所對應的值(true或false)
let company_checked = computed(() => {return store.state.selected_company});

// bool: 此變數為"公司全選按鈕"on的值，按鈕沒被勾選時會變false
let all_company_checked = ref(store.state.allcompany_selected);

// 監控all_company_checked有變化時，改變company_checked所有value，並渲染"公司全選按鈕"的文字。
watch(all_company_checked, (is_all) => {

for(let site in company.value){
    company_checked.value[site]=is_all;
}

store.commit('update_is_all_company', is_all);

return is_all;
});

// 燈箱控制
let isShow = ref(false); // 燈箱出現與否
let modalStyle = computed(() => {return !isShow.value ? "display:none;" : ""}); // 燈箱出現與否的樣式
const toggleModal = () => { isShow.value = !isShow.value; }; // 燈箱出現與否的切換

// 搜尋地點
let search_text = ref("");

// 搜尋公司資料
const search = () => {
    let search_text_lower = search_text.value.toLowerCase();

    axios
    .get("/latlng_search/" + search_text_lower)
    .then((res) => {

        let locate_name = res.data.company;
        let lat =  res.data.lat;
        let lng = res.data.lng

        // 用tz-lookup找到他的IANA
        let tz = tzlookup(lat, lng);
        

        // 新增到company、company_checked，並渲染到leaflet、燈箱選項、各site時間字卡
        // 若全選(all_company_checked.value===true)，則燈箱選項、各site時間字卡取消掉原本的全選，僅保留搜尋選項
        company.value[locate_name] = {
            location: [lat, lng],
            year: null,
            month: null,
            date: null,
            time: null,
            time_zone: tz,            
            work_hour: ["08:00", "17:00"],
            stretch_hour: ["07:30", "23:00"],
            rest_hour: ["23:00", "07:00"],
            color: null,
            day_times: null,
            day_colors: null,
        };

        if (all_company_checked.value === true){
            all_company_checked.value = false;
        }

        // nextTick讓這步跟all_company_checked.value = false;不同步更新html
        nextTick(() => {
            store.state.selected_company[locate_name] = true;
        });


    });
};

</script>


<template>
    <div class="flex justify-center items-center">
        <button @click="isShow = true" class="font-extrabold text-[#253fae] bg-transparent hover:bg-[#FAF4FF] border rounded-lg p-2">
            + Edit office
        </button>
    </div>

    <!-- 燈箱：設定office -->
    <div class="modal-mask" :style="modalStyle">
    <div class="modal-container"  @click.self="toggleModal">
        <div class="modal-mask" :style="modalStyle">
            <div class="modal-container"  @click.self="toggleModal">
                <div class="modal-body overflow-auto h-1/2 w-1/2 md:h-1/3 md:w-1/3">

                    <!-- 編輯office出現與否 -->
                    <h3 class="inline font-extrabold text-[#253fae]">Edit office</h3>

                    <!-- search bar -->
                    <div class="grid grid-cols-5 text-gray-600">
                        <input type="search" name="serch" placeholder="Search office..." class="bg-white col-span-4 border-0 p-3" v-model="search_text">             
                        <button type="submit" @click="search"> 
                            <svg class="h-4 w-4 fill-current" xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" version="1.1" id="Capa_1" x="0px" y="0px" viewBox="0 0 56.966 56.966" style="enable-background:new 0 0 56.966 56.966;" xml:space="preserve" >
                            <path d="M55.146,51.887L41.588,37.786c3.486-4.144,5.396-9.358,5.396-14.786c0-12.682-10.318-23-23-23s-23,10.318-23,23  s10.318,23,23,23c4.761,0,9.298-1.436,13.177-4.162l13.661,14.208c0.571,0.593,1.339,0.92,2.162,0.92  c0.779,0,1.518-0.297,2.079-0.837C56.255,54.982,56.293,53.08,55.146,51.887z M23.984,6c9.374,0,17,7.626,17,17s-7.626,17-17,17  s-17-7.626-17-17S14.61,6,23.984,6z"/>
                            </svg>
                        </button>   
                    </div>

                    <br>
                    <!-- 取消全選 -->
                    <div class="border rounded-lg p-1 m-1 mb-2 inline-block">
                        <input id="all_select" type="checkbox" :value="all_company_checked" v-model="all_company_checked" >
                        <label for="all_select" v-if="all_company_checked===true" class="text-sm" >取消全選</label>
                        <label for="all_select" v-else class="text-sm">全選</label>
                    </div>     
                    <!-- 各office勾選方格 -->
                    <div class="flex flex-wrap">
                        <div v-for="(value, site) in company" :key="site" class="border rounded-lg p-1 m-1 mb-2">
                            <div>
                                <input 
                                    type="checkbox" 
                                    :id="site" 
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


</template>


<style scoped>

.modal-mask {
  position: fixed;
  z-index: 40;
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

