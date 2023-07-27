import { defineStore } from "pinia";
import { AnnotState } from "../components/data";

export const useAnnotState = defineStore("AnnotState", {
    state: (): AnnotState => ({
        input: "",
        output: "",
        page: "",
        op: "remove",
        annot_types: [],
    }),
    getters: {

    },
    actions: {
        resetState() {
            this.$patch({
                input: "",
                output: "",
                page: "",
                op: "split",
                annot_types: ['all'],
            })
        },
    }
})