import { defineStore } from "pinia";
import { HeaderAndFooterState } from "../components/data";

export const useHeaderAndFooterState = defineStore("HeaderAndFooterState", {
    state: (): HeaderAndFooterState => ({
        input: "",
        output: "",
        page: "",
        op: "add",
        is_set_header: false,
        is_set_footer: false,
        header_left: '',
        header_center: '',
        header_right: '',
        footer_left: '',
        footer_center: '',
        footer_right: '',
        up: 1.27,
        left: 2.54,
        down: 1.27,
        right: 2.54,
        unit: 'cm',
        font_family: 'msyh.ttc',
        font_size: 11,
        font_color: '#000000',
        opacity: 1,
        remove_list: []
    }),
    getters: {

    },
    actions: {
        resetState() {
            this.$patch({
                input: "",
                output: "",
                page: "",
                op: "add",
                is_set_header: false,
                is_set_footer: false,
                header_left: '',
                header_center: '',
                header_right: '',
                footer_left: '',
                footer_center: '',
                footer_right: '',
                up: 1.27,
                left: 2.54,
                down: 1.27,
                right: 2.54,
                unit: 'cm',
                font_family: 'msyh.ttc',
                font_size: 11,
                font_color: '#000000',
                opacity: 1,
                remove_list: []
            })
        },
    }
})