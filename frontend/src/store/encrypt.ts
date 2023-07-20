import { defineStore } from "pinia";
import { EncryptState } from "../components/data";

export const useEncryptState = defineStore("EncryptState", {
    state: (): EncryptState => ({
        input: "",
        output: "",
        op: "encrypt",
        upw: "",
        opw: "",
        perm: [],
        is_set_upw: false,
        is_set_opw: false,
        upw_confirm: "",
        opw_confirm: "",
        old_upw: "",
        old_opw: ""
    }),
    getters: {

    },
    actions: {
        resetState() {
            this.$patch({
                input: "",
                output: "",
                op: "encrypt",
                upw: "",
                opw: "",
                perm: [],
                is_set_upw: false,
                is_set_opw: false,
                upw_confirm: "",
                opw_confirm: "",
                old_upw: "",
                old_opw: ""
            })
        },
    }
})