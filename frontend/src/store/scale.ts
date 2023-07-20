import { defineStore } from "pinia";
import { ScaleState } from "../components/data";

export const useScaleState = defineStore("ScaleState", {
    state: (): ScaleState => ({
        input: "",
        output: "",
        page: "",
        op: "ratio",
        ratio: 0,
        paper_size: "A4",
        width: 0,
        height: 0,
        unit: "pt"
    }),
    getters: {

    },
    actions: {
        resetState() {
            this.$patch({
                input: "",
                output: "",
                page: "",
                op: "ratio",
                ratio: 0,
                paper_size: "A4",
                width: 0,
                height: 0,
                unit: "pt"
            })
        },
    }
})