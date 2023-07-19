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
        input_list: []
    }),
    getters: {

    },
    actions: {
        resetState() {
        },
    }
})