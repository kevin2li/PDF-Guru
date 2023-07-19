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
            this.input = "";
            this.output = "";
            this.page = "";
            this.op = "split";
            this.split_h_breakpoints = [];
            this.split_v_breakpoints = [];
            this.split_type = "even";
            this.rows = 1;
            this.cols = 1;
            this.paper_size = "a4";
            this.orientation = "portrait";
        },
    }
})