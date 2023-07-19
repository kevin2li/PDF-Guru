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
            this.$patch({
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
            })
        },
    }
})