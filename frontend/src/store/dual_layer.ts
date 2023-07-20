import { defineStore } from "pinia";
import { DualLayerState } from "../components/data";

export const useDualLayerState = defineStore("DualLayerState", {
    state: (): DualLayerState => ({
        input: "",
        output: "",
        page: "",
        lang: "chi_sim",
        dpi: 300,
    }),
    getters: {

    },
    actions: {
        resetState() {
            this.$patch({
                input: "",
                output: "",
                page: "",
                lang: "chi_sim",
                dpi: 300,
            })
        },
    }
})