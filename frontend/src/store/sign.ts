import { defineStore } from "pinia";
import { SignState } from "../components/data";

export const useSignState = defineStore("SignState", {
    state: (): SignState => ({
        input: "",
        output: "",
        op: "image",
        text: "",
        font_family: "",
        font_size: 11,
        font_color: "#000000",
        thinning: 0.75,
        smoothing: 0.5,
        streamline: 0.5,
        is_pressure: true,
    }),
    getters: {

    },
    actions: {
        resetState() {
            this.$patch({
                input: "",
                output: "",
                op: "image",
                text: "",
                font_family: "",
                font_size: 11,
                font_color: "#000000",
                thinning: 0.75,
                smoothing: 0.5,
                streamline: 0.5,
                is_pressure: true,
            })
        },
    }
})