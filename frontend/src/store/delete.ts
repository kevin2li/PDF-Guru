import { defineStore } from "pinia";
import { DeleteState } from "../components/data";

export const useDeleteState = defineStore("DeleteState", {
    state: (): DeleteState => ({
        input: "",
        output: "",
        page: "",
    }),
    getters: {

    },
    actions: {
        resetState() {
            this.$patch({
                input: "",
                output: "",
                page: "",
            })
        },
    }
})