import { defineStore } from "pinia";
import { RotateState } from "../components/data";

export const useRotateState = defineStore("RotateState", {
    state: (): RotateState => ({
        input: "",
        output: "",
        page: "",
        degree: 90,
    }),
    getters: {

    },
    actions: {
        resetState() {
            this.$patch({
                input: "",
                output: "",
                page: "",
                degree: 90,
            })
        },
    }
})