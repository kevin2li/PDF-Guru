import { defineStore } from "pinia";
import { InsertState } from "../components/data";

export const useInsertState = defineStore("insertState", {
    state: (): InsertState => ({
        input: "",
        output: "",
        page: "",
        op: "insert",
        insert_type: "blank",
        paper_size: "a4",
        orientation: "portrait",
        count: 1,
        src_pos_type: "before_first",
        src_pos: 1,
        src_path: "",
        dst_path: "",
        src_range: "",
        dst_range: ""
    }),
    getters: {

    },
    actions: {
        resetState() {
            this.input = "";
            this.output = "";
            this.page = "";
            this.op = "insert";
            this.insert_type = "blank";
            this.paper_size = "a4";
            this.orientation = "portrait";
            this.count = 1;
            this.src_pos_type = "before_first";
            this.src_pos = 1;
            this.src_path = "";
            this.dst_path = "";
            this.src_range = "";
            this.dst_range = "";
        },
    }
})