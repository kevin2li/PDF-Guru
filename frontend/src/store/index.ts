import { defineStore } from "pinia";
import { IndexState } from "../components/data";

export const useIndexState = defineStore("IndexState", {
    state: (): IndexState => ({
        trial_flag: false,
        max_try_times: 3,
        trial_set: false,
    }),
    getters: {

    },
    actions: {
        resetState() {
            this.$patch({
                trial_flag: false,
                max_try_times: 3,
                trial_set: false,
            })
        },
    }
})