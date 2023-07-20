import { defineStore } from "pinia";
import { CutState } from "../components/data";

export const useCutState = defineStore("cutState", {
    state: (): CutState => ({
        input: "",
        output: "",
        page: "",
        op: "split",
        split_h_breakpoints: [],
        split_v_breakpoints: [],
        split_type: "even",
        rows: 1,
        cols: 1,
        paper_size: "a4",
        orientation: "portrait",
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
                split_h_breakpoints: [],
                split_v_breakpoints: [],
                split_type: "even",
                rows: 1,
                cols: 1,
                paper_size: "a4",
                orientation: "portrait",
            })
        },
    }
})