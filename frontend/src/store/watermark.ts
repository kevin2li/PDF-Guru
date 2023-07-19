import { defineStore } from "pinia";
import { WatermarkState } from "../components/data";

export const useWatermarkState = defineStore("WatermarkState", {
    state: (): WatermarkState => ({
        input: "",
        output: "",
        page: "",
        op: "add",
        type: "text",
        text: "",
        font_family: "msyh.ttc",
        font_size: 50,
        font_color: "#000000",
        font_opacity: 0.3,
        rotate: 45,
        num_lines: 1,
        multiple_mode: false,
        x_offset: 0,
        y_offset: 0,
        word_spacing: 1,
        line_spacing: 1,
        remove_method: "type",
        step: "1",
        wm_index: "",
        lines: 0,
        wm_path: "",
        scale: 1,
        mask_type: 'annot',
        unit: 'pt',
        width: 0,
        height: 0,
        annot_page: 1,
        mask_color: '#FFFFFF',
        mask_opacity: 1,
        layer: "bottom",
    }),
    getters: {

    },
    actions: {
        resetState() {
            this.input = "";
            this.output = "";
            this.page = "";
            this.op = "add";
            this.type = "text";
            this.text = "";
            this.font_family = "msyh.ttc";
            this.font_size = 50;
            this.font_color = "#000000";
            this.font_opacity = 0.3;
            this.rotate = 45;
            this.num_lines = 1;
            this.multiple_mode = false;
            this.x_offset = 0;
            this.y_offset = 0;
            this.word_spacing = 1;
            this.line_spacing = 1;
            this.remove_method = "type";
            this.step = "1";
            this.wm_index = "";
            this.lines = 0;
            this.wm_path = "";
            this.scale = 1;
            this.mask_type = 'annot';
            this.unit = 'pt';
            this.width = 0;
            this.height = 0;
            this.annot_page = 1;
            this.mask_color = '#FFFFFF';
            this.mask_opacity = 1;
            this.layer = "bottom";
        },
    }
})