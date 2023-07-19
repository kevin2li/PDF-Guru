import { defineStore } from "pinia";
import { CropState } from "../components/data";

export const useCropState = defineStore("CropState", {
    state: (): CropState => ({
        input: "",
        output: "",
        page: "",
        op: "margin",
        unit: "pt",
        keep_size: true,
        up: 0,
        left: 0,
        down: 0,
        right: 0,
    }),
    getters: {

    },
    actions: {
        resetState() {
            this.$patch({
                input: "",
                output: "",
                page: "",
                op: "margin",
                unit: "pt",
                keep_size: true,
                up: 0,
                left: 0,
                down: 0,
                right: 0,
            })
        },
    }
})