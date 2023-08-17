import { createRouter, 
    // createWebHashHistory, 
    createWebHistory
 } from "vue-router";
// import Layout from "@/components/Layout.vue";
import Map from "@/components/Map.vue";
import Recommand from "@/components/Recommand.vue";


export const route = createRouter({
//   history: createWebHashHistory(),
  history: createWebHistory(),
  routes: [
          { 
            path: "/",
            name: "map", 
            alias: '/map',
            component: Map,
            // component: () => import("../views/GenerateJD.vue"),
          },
          { 
            path: "/recommand",
            name: "recommand", 
            component: Recommand,
            // component: () => import("../views/ResumeSearch.vue"),
            props: (route) => route.params
          },         
  ]
});