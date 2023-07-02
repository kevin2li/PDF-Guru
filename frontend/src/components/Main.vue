<template>
    <a-row>
        <a-col :span="4">
            <a-menu v-model:selectedKeys="currentMenu" style="width: 180px" mode="inline">
                <a-menu-item key="merge">
                    <template #icon>
                        <block-outlined />
                    </template>
                    {{ menuRecord['merge'] }}
                </a-menu-item>
                <a-menu-item key="split">
                    <template #icon>
                        <split-cells-outlined />
                    </template>
                    {{ menuRecord['split'] }}
                </a-menu-item>
                <a-menu-item key="delete">
                    <template #icon>
                        <close-outlined />
                    </template>
                    {{ menuRecord['delete'] }}
                </a-menu-item>
                <a-menu-item key="reorder">
                    <template #icon>
                        <ordered-list-outlined />
                    </template>
                    {{ menuRecord['reorder'] }}
                </a-menu-item>
                <a-menu-item key="insert">
                    <template #icon>
                        <login-outlined />
                    </template>
                    {{ menuRecord['insert'] }}
                </a-menu-item>
                <a-menu-item key="bookmark">
                    <template #icon>
                        <bars-outlined />
                    </template>
                    {{ menuRecord['bookmark'] }}
                </a-menu-item>
                <a-menu-item key="scale">
                    <template #icon>
                        <fullscreen-outlined />
                    </template>
                    {{ menuRecord['scale'] }}
                </a-menu-item>
                <a-menu-item key="watermark">
                    <template #icon>
                        <highlight-outlined />
                    </template>
                    {{ menuRecord['watermark'] }}
                </a-menu-item>
                <a-menu-item key="rotate">
                    <template #icon>
                        <rotate-right-outlined />
                    </template>
                    {{ menuRecord['rotate'] }}
                </a-menu-item>
                <a-menu-item key="crop">
                    <template #icon>
                        <scissor-outlined />
                    </template>
                    {{ menuRecord['crop'] }}
                </a-menu-item>
                <a-menu-item key="extract">
                    <template #icon>
                        <aim-outlined />
                    </template>
                    {{ menuRecord['extract'] }}
                </a-menu-item>
                <a-menu-item key="compress">
                    <template #icon>
                        <file-zip-outlined />
                    </template>
                    {{ menuRecord['compress'] }}
                </a-menu-item>
                <a-menu-item key="convert">
                    <template #icon>
                        <export-outlined />
                    </template>
                    {{ menuRecord['convert'] }}

                </a-menu-item>
                <a-menu-item key="encrypt">
                    <template #icon>
                        <lock-outlined />
                    </template>
                    {{ menuRecord['encrypt'] }}
                </a-menu-item>
                <a-menu-item key="ocr">
                    <template #icon>
                        <eye-outlined />
                    </template>
                    {{ menuRecord['ocr'] }}
                </a-menu-item>
                <a-menu-item key="settings">
                    <template #icon>
                        <SettingOutlined />
                    </template>
                    {{ menuRecord['settings'] }}
                </a-menu-item>
            </a-menu>
        </a-col>
        <a-col :span="20">
            <div>
                <div style="margin-right: 5vw;margin-top: 0.5em;">
                    <a-typography-title>{{ menuRecord[currentMenu.at(0) || "merge"] }}</a-typography-title>
                    <a-typography-paragraph>
                        <blockquote>功能说明：{{ menuDesc[currentMenu.at(0) || "merge"] }}</blockquote>
                    </a-typography-paragraph>
                </div>
                <div>
                    <MergeForm v-if="currentMenu.at(0) === 'merge'" />
                    <SplitForm v-if="currentMenu.at(0) === 'split'" />
                    <DeleteForm v-if="currentMenu.at(0) === 'delete'" />
                    <ReorderForm v-if="currentMenu.at(0) === 'reorder'" />
                    <InsertForm v-if="currentMenu.at(0) === 'insert'" />
                    <BookmarkForm v-if="currentMenu.at(0) === 'bookmark'" />
                    <ScaleForm v-if="currentMenu.at(0) === 'scale'" />
                    <WatermarkForm v-if="currentMenu.at(0) === 'watermark'" />
                    <RotateForm v-if="currentMenu.at(0) === 'rotate'" />
                    <CropForm v-if="currentMenu.at(0) === 'crop'" />
                    <ExtractForm v-if="currentMenu.at(0) === 'extract'" />
                    <CompressForm v-if="currentMenu.at(0) === 'compress'" />
                    <ConvertForm v-if="currentMenu.at(0) === 'convert'" />
                    <EncryptForm v-if="currentMenu.at(0) === 'encrypt'" />
                    <OcrForm v-if="currentMenu.at(0) === 'ocr'" />
                    <PreferencesForm v-if="currentMenu.at(0) === 'settings'" />
                </div>
            </div>
        </a-col>
    </a-row>
</template>
<script lang="ts">
import { defineComponent, reactive, watch, ref } from 'vue';
import {
    MinusCircleOutlined,
    PlusOutlined,
    AppstoreOutlined,
    SettingOutlined,
    BarsOutlined,
    BorderlessTableOutlined,
    ScissorOutlined,
    CopyOutlined,
    BlockOutlined,
    FileZipOutlined,
    RotateRightOutlined,
    LockOutlined,
    OrderedListOutlined,
    HighlightOutlined,
    AimOutlined,
    ExportOutlined,
    UploadOutlined,
    FullscreenOutlined,
    CloseOutlined,
    FontColorsOutlined,
    FontSizeOutlined,
    EyeOutlined,
    SplitCellsOutlined,
    LoginOutlined
} from '@ant-design/icons-vue';
import { message, Modal } from 'ant-design-vue';
import { menuDesc, menuRecord } from "./data";
import MergeForm from "./Forms/MergeForm.vue";
import SplitForm from "./Forms/SplitForm.vue";
import DeleteForm from "./Forms/DeleteForm.vue";
import ReorderForm from "./Forms/ReorderForm.vue";
import InsertForm from "./Forms/InsertForm.vue";
import BookmarkForm from "./Forms/BookmarkForm.vue";
import ScaleForm from "./Forms/ScaleForm.vue";
import WatermarkForm from './Forms/WatermarkForm.vue';
import RotateForm from "./Forms/RotateForm.vue";
import CropForm from "./Forms/CropForm.vue";
import ExtractForm from "./Forms/ExtractForm.vue";
import CompressForm from "./Forms/CompressForm.vue";
import ConvertForm from "./Forms/ConvertForm.vue";
import EncryptForm from "./Forms/EncryptForm.vue";
import OcrForm from "./Forms/OcrForm.vue";
import PreferencesForm from "./Forms/PreferencesForm.vue";


export default defineComponent({
    components: {
        // icon
        MinusCircleOutlined,
        PlusOutlined,
        AppstoreOutlined,
        SettingOutlined,
        BarsOutlined,
        BorderlessTableOutlined,
        ScissorOutlined,
        CopyOutlined,
        BlockOutlined,
        FileZipOutlined,
        RotateRightOutlined,
        LockOutlined,
        OrderedListOutlined,
        HighlightOutlined,
        AimOutlined,
        ExportOutlined,
        UploadOutlined,
        FullscreenOutlined,
        CloseOutlined,
        FontColorsOutlined,
        FontSizeOutlined,
        EyeOutlined,
        SplitCellsOutlined,
        LoginOutlined,
        // form
        // 合并
        MergeForm,
        // 拆分
        SplitForm,
        // 删除
        DeleteForm,
        // 重排
        ReorderForm,
        // 插入/替换
        InsertForm,
        // 书签
        BookmarkForm,
        // 缩放
        ScaleForm,
        // 水印
        WatermarkForm,
        // 旋转
        RotateForm,
        // 裁剪/分割
        CropForm,
        // 提取
        ExtractForm,
        // 压缩
        CompressForm,
        // 转换
        ConvertForm,
        // 加密
        EncryptForm,
        // OCR
        OcrForm,
        // 首选项
        PreferencesForm,
    },
    setup() {
        return {
            menuRecord,
            menuDesc,
            currentMenu: ref<string[]>(["merge"]),
        };
    },
});
</script>