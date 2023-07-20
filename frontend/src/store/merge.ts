import { defineStore } from "pinia";
import { MergeState } from "../components/data";

export const useMergeState = defineStore("MergeState", {
    state: (): MergeState => ({
        input_path_list: [],
        output: "",
        sort: "default",
        sort_direction: "asc",
    }),
    getters: {

    },
    actions: {
        resetState() {
            this.$patch({
                input_path_list: [],
                output: "",
                sort: "default",
                sort_direction: "asc",
            })
        },
    }
})