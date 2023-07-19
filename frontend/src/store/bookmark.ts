import { defineStore } from "pinia";
import { BookmarkState } from "../components/data";

export const useBookmarkState = defineStore("BookmarkState", {
    state: (): BookmarkState => ({
        input: "",
        output: "",
        page: "",
        op: "extract",
        bookmark_file: "",
        write_type: "file",
        write_format: "",
        write_offset: 0,
        write_gap: 1,
        extract_format: "txt",
        transform_offset: 0,
        transform_indent: false,
        transform_dots: false,
        ocr_lang: "ch",
        ocr_double_column: false,
        delete_level_below: 0,
        default_level: 1,
        remove_blank_lines: true,
        recognize_type: "font",
        start_number: 1,
    }),
    getters: {

    },
    actions: {
        resetState() {
            this.input = "";
            this.output = "";
            this.page = "";
            this.op = "extract";
            this.bookmark_file = "";
            this.write_type = "file";
            this.write_format = "";
            this.write_offset = 0;
            this.write_gap = 1;
            this.extract_format = "txt";
            this.transform_offset = 0;
            this.transform_indent = false;
            this.transform_dots = false;
            this.ocr_lang = "ch";
            this.ocr_double_column = false;
            this.delete_level_below = 0;
            this.default_level = 1;
            this.remove_blank_lines = true;
            this.recognize_type = "font";
            this.start_number = 1;
        },
    }
})