import { defineStore } from "pinia";
import { ExtractState } from "../components/data";

export const useExtractState = defineStore("ExtractState", {
    state: (): ExtractState => ({
        input: "",
        output: "",
        page: "",
        op: "page",
    }),
    getters: {

    },
    actions: {
        resetState() {
            this.$patch({
                input: "",
                output: "",
                page: "",
                op: "page",
            })
        },
    }
})