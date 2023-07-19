import { defineStore } from "pinia";
import { PageNumberState } from "../components/data";

export const usePageNumberState = defineStore("PageNumberState", {
    state: (): PageNumberState => ({
        input: "",
        output: "",
        page: "",
        op: 'add',
        pos: 'footer',
        number_style: '1',
        number_start: 1,
        custom_style: '',
        is_custom_style: false,
        align: 'center',
        font_family: 'simsun.ttc',
        font_size: 14,
        font_color: '#000000',
        up: 1.27,
        down: 1.27,
        left: 2.54,
        right: 2.54,
        opacity: 1,
        unit: 'cm'
    }),
    getters: {

    },
    actions: {
        resetState() {
            this.$patch({
                input: "",
                output: "",
                page: "",
                op: 'add',
                pos: 'footer',
                number_style: '1',
                number_start: 1,
                custom_style: '',
                is_custom_style: false,
                align: 'center',
                font_family: 'simsun.ttc',
                font_size: 14,
                font_color: '#000000',
                up: 1.27,
                down: 1.27,
                left: 2.54,
                right: 2.54,
                opacity: 1,
                unit: 'cm'
            })
        },
    }
})