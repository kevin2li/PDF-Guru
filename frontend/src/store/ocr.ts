import { defineStore } from "pinia";
import { OcrState } from "../components/data";

export const useOcrState = defineStore("OcrState", {
    state: (): OcrState => ({
        input: "",
        output: "",
        page: "",
        lang: "ch",
        double_column: false,
        engine: "paddleocr",
    }),
    getters: {

    },
    actions: {
        resetState() {
            this.$patch({
                input: "",
                output: "",
                page: "",
                lang: "ch",
                double_column: false,
                engine: "paddleocr",
            })
        },
    }
})