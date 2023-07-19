import { defineStore } from "pinia";

interface MenuState {
    rootSubmenuKeys: string[];
    openKeys: string[];
    selectedKeys: string[];
}

export const useMenuState = defineStore("menuState", {
    state: (): MenuState => ({
        rootSubmenuKeys: ['index', 'page_edit', 'protect', 'other', "settings"],
        selectedKeys: ["index"],
        openKeys: ["index"]
    }),
    getters: {

    },
    actions: {
        resetState() {
            this.openKeys = ["index"];
            this.selectedKeys = ["index"];
        },
        onOpenChange(openKeys: string[]) {
            const latestOpenKey = openKeys.find(key => this.openKeys.indexOf(key) === -1);
            if (this.rootSubmenuKeys.indexOf(latestOpenKey!) === -1) {
                this.openKeys = openKeys;
            } else {
                this.openKeys = latestOpenKey ? [latestOpenKey] : [];
            }
        },
    }
})