import { defineStore } from "pinia";
import { AnkiState } from "../components/data";

export const useAnkiState = defineStore("AnkiState", {
    state: (): AnkiState => ({
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