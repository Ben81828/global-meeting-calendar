import { createRouter, 
    // createWebHashHistory, 
    createWebHistory
 } from "vue-router";

import Map from "@/components/Map.vue";
import Recommand from "@/components/Recommand.vue";
import Calendar from "@/components/Calendar.vue";


export const route = createRouter({
//   history: createWebHashHistory(),
  history: createWebHistory(),
  routes: [
          { 
            path: "/",
            name: "map", 
            alias: '/map',
            component: Map,
          },
          { 
            path: "/recommand",
            name: "recommand", 
            component: Recommand,

          },
          { 
            path: "/calendar",
            name: "calendar", 
            component: Calendar,
          },                
  ]
});