import { defineStore } from "pinia";
import { CompressState } from "../components/data";

export const useCompressState = defineStore("CompressState", {
    state: (): CompressState => ({
        input: "",
        output: "",
    }),
    getters: {

    },
    actions: {
        resetState() {
            this.$patch({
                input: "",
                output: "",
            })
        },
    }
})