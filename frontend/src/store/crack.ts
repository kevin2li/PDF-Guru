import { defineStore } from "pinia";
import { CrackState } from "../components/data";

export const useCrackState = defineStore("CrackState", {
    state: (): CrackState => ({
        input: "",
        output: "",
        hash_type: '',
        charset: '',
        attack_mode: '3',
        crack_type: 'PDF',
        dict_path: '',
    }),
    getters: {

    },
    actions: {
        resetState() {
            this.$patch({
                input: "",
                output: "",
                hash_type: '',
                charset: '',
                attack_mode: '3',
                crack_type: 'PDF',
                dict_path: '',
            })
        },
    }
})