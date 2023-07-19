import { defineStore } from "pinia";
import { SplitState } from "../components/data";

export const useSplitState = defineStore("SplitState", {
    state: (): SplitState => ({
        input: "",
        output: "",
        page: "",
        op: "span",
        span: 5,
        bookmark_level: "1",
    }),
    getters: {

    },
    actions: {
        resetState() {
            this.$patch({
                input: "",
                output: "",
                page: "",
                op: "span",
                span: 5,
                bookmark_level: "1",
            })
        },
    }
})