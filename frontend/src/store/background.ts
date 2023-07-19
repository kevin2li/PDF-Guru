import { defineStore } from "pinia";
import { BackgroundState } from "../components/data";

export const useBackgroundState = defineStore("BackgroundState", {
    state: (): BackgroundState => ({
        input: "",
        output: "",
        page: "",
        degree: 0,
        op: 'color',
        color: '#FFFFFF',
        opacity: 1,
        scale: 1,
        x_offset: 0,
        y_offset: 0,
        image_path: ''
    }),
    getters: {

    },
    actions: {
        resetState() {
            this.$patch({
                input: "",
                output: "",
                page: "",
                degree: 0,
                op: 'color',
                color: '#FFFFFF',
                opacity: 1,
                scale: 1,
                x_offset: 0,
                y_offset: 0,
                image_path: ''
            })
        },
    }
})