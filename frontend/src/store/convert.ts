import { defineStore } from "pinia";
import { ConvertState } from "../components/data";

export const useConvertState = defineStore("ConvertState", {
    state: (): ConvertState => ({
        input: "",
        output: "",
        page: "",
        type: "pdf2png",
        dpi: 300,
        is_merge: false,
        sort_method: 'name',
        sort_direction: 'asc',
        input_list: [],
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
                type: "pdf2png",
                dpi: 300,
                is_merge: false,
                sort_method: 'name',
                sort_direction: 'asc',
                input_list: [],
                paper_size: "a4",
                orientation: "portrait",
            })
        },
    }
})