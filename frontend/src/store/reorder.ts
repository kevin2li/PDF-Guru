import { defineStore } from "pinia";
import { ReorderState } from "../components/data";

export const useReorderState = defineStore("ReorderState", {
    state: (): ReorderState => ({
        input: "",
        output: "",
        page: "",
    }),
    getters: {

    },
    actions: {
        resetState() {
            this.$patch({
                input: "",
                output: "",
                page: "",
            })
        },
    }
})