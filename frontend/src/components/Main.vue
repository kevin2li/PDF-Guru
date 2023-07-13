<template>
    <a-row>
        <a-col :span="4">
            <a-menu v-model:selectedKeys="state.selectedKeys" :open-keys="state.openKeys" style="width: 180px"
                @openChange="onOpenChange" mode="inline">
                <a-sub-menu key="page_edit">
                    <template #title>页面编辑</template>
                    <template #icon>
                        <form-outlined />
                    </template>
                    <a-menu-item key="insert">
                        <template #icon>
                            <login-outlined />
                        </template>
                        {{ menuRecord['insert'] }}
                    </a-menu-item>
                    <a-menu-item key="merge">
                        <template #icon>
                            <merge-cells-outlined />
                        </template>
                        {{ menuRecord['merge'] }}
                    </a-menu-item>
                    <a-menu-item key="split">
                        <template #icon>
                            <split-cells-outlined />
                        </template>
                        {{ menuRecord['split'] }}
                    </a-menu-item>
                    <a-menu-item key="rotate">
                        <template #icon>
                            <rotate-right-outlined />
                        </template>
                        {{ menuRecord['rotate'] }}
                    </a-menu-item>
                    <a-menu-item key="delete">
                        <template #icon>
                            <delete-outlined />
                        </template>
                        {{ menuRecord['delete'] }}
                    </a-menu-item>
                    <a-menu-item key="reorder">
                        <template #icon>
                            <ordered-list-outlined />
                        </template>
                        {{ menuRecord['reorder'] }}
                    </a-menu-item>
                    <a-menu-item key="crop">
                        <template #icon>
                            <scissor-outlined />
                        </template>
                        {{ menuRecord['crop'] }}
                    </a-menu-item>
                    <a-menu-item key="scale">
                        <template #icon>
                            <fullscreen-outlined />
                        </template>
                        {{ menuRecord['scale'] }}
                    </a-menu-item>
                    <a-menu-item key="cut">
                        <template #icon>
                            <borderless-table-outlined />
                        </template>
                        {{ menuRecord['cut'] }}
                    </a-menu-item>
                    <a-menu-item key="header">
                        <template #icon>
                            <credit-card-outlined />
                        </template>
                        {{ menuRecord['header'] }}
                    </a-menu-item>
                    <a-menu-item key="page_number">
                        <template #icon>
                            <field-binary-outlined />
                        </template>
                        {{ menuRecord['page_number'] }}
                    </a-menu-item>
                    <a-menu-item key="background">
                        <template #icon>
                            <bg-colors-outlined />
                        </template>
                        {{ menuRecord['background'] }}
                    </a-menu-item>
                </a-sub-menu>
                <a-sub-menu key="protect">
                    <template #title>保护</template>
                    <template #icon>
                        <safety-certificate-outlined />
                    </template>
                    <a-menu-item key="watermark">
                        <template #icon>
                            <highlight-outlined />
                        </template>
                        {{ menuRecord['watermark'] }}
                    </a-menu-item>
                    <a-menu-item key="encrypt">
                        <template #icon>
                            <lock-outlined />
                        </template>
                        {{ menuRecord['encrypt'] }}
                    </a-menu-item>
                </a-sub-menu>
                <a-sub-menu key="other">
                    <template #title>其他</template>
                    <template #icon>
                        <appstore-outlined />
                    </template>
                    <!-- <a-menu-item key="meta">
                        <template #icon>
                            <info-circle-outlined />
                        </template>
                        {{ menuRecord['meta'] }}
                    </a-menu-item> -->
                    <a-menu-item key="bookmark">
                        <template #icon>
                            <book-outlined />
                        </template>
                        {{ menuRecord['bookmark'] }}
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
                            <sync-outlined />
                        </template>
                        {{ menuRecord['convert'] }}
                    </a-menu-item>
                    <a-menu-item key="ocr">
                        <template #icon>
                            <eye-outlined />
                        </template>
                        {{ menuRecord['ocr'] }}
                    </a-menu-item>
                    <!-- <a-menu-item key="crack">
                        <template #icon>
                            <tool-outlined />
                        </template>
                        {{ menuRecord['crack'] }}
                    </a-menu-item> -->
                    <a-menu-item key="dual">
                        <template #icon>
                            <file-search-outlined />
                        </template>
                        {{ menuRecord['dual'] }}
                    </a-menu-item>
                </a-sub-menu>
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
                    <a-typography-title>{{ menuRecord[state.selectedKeys.at(0) || "merge"] }}</a-typography-title>
                    <a-typography-paragraph>
                        <blockquote>功能说明：{{ menuDesc[state.selectedKeys.at(0) || "merge"] }}</blockquote>
                    </a-typography-paragraph>
                </div>
                <div>
                    <MergeForm v-if="state.selectedKeys.at(0) === 'merge'" />
                    <SplitForm v-if="state.selectedKeys.at(0) === 'split'" />
                    <DeleteForm v-if="state.selectedKeys.at(0) === 'delete'" />
                    <ReorderForm v-if="state.selectedKeys.at(0) === 'reorder'" />
                    <InsertForm v-if="state.selectedKeys.at(0) === 'insert'" />
                    <BookmarkForm v-if="state.selectedKeys.at(0) === 'bookmark'" />
                    <ScaleForm v-if="state.selectedKeys.at(0) === 'scale'" />
                    <WatermarkForm v-if="state.selectedKeys.at(0) === 'watermark'" />
                    <RotateForm v-if="state.selectedKeys.at(0) === 'rotate'" />
                    <CropForm v-if="state.selectedKeys.at(0) === 'crop'" />
                    <CutForm v-if="state.selectedKeys.at(0) === 'cut'" />
                    <ExtractForm v-if="state.selectedKeys.at(0) === 'extract'" />
                    <CompressForm v-if="state.selectedKeys.at(0) === 'compress'" />
                    <ConvertForm v-if="state.selectedKeys.at(0) === 'convert'" />
                    <EncryptForm v-if="state.selectedKeys.at(0) === 'encrypt'" />
                    <OcrForm v-if="state.selectedKeys.at(0) === 'ocr'" />
                    <PreferencesForm v-if="state.selectedKeys.at(0) === 'settings'" />
                    <HeaderAndFooterForm v-if="state.selectedKeys.at(0) === 'header'" />
                    <PageNumberForm v-if="state.selectedKeys.at(0) === 'page_number'" />
                    <BackgroundForm v-if="state.selectedKeys.at(0) === 'background'" />
                    <!-- <MetaForm v-if="state.selectedKeys.at(0) === 'meta'" /> -->
                    <DualLayerForm v-if="state.selectedKeys.at(0) === 'dual'" />
                    <PasswordCrackForm v-if="state.selectedKeys.at(0) === 'crack'" />
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
    LoginOutlined,
    FormOutlined,
    DeleteOutlined,
    MergeCellsOutlined,
    InfoCircleOutlined,
    BookOutlined,
    CreditCardOutlined,
    BgColorsOutlined,
    SafetyCertificateOutlined,
    TabletOutlined,
    FieldBinaryOutlined,
    SyncOutlined,
    FileSearchOutlined,
    ToolOutlined,
    createFromIconfontCN,
} from '@ant-design/icons-vue';

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
import CutForm from "./Forms/CutForm.vue";
import ExtractForm from "./Forms/ExtractForm.vue";
import CompressForm from "./Forms/CompressForm.vue";
import ConvertForm from "./Forms/ConvertForm.vue";
import EncryptForm from "./Forms/EncryptForm.vue";
import OcrForm from "./Forms/OcrForm.vue";
import PreferencesForm from "./Forms/PreferencesForm.vue";
import HeaderAndFooterForm from "./Forms/HeaderAndFooterForm.vue";
import BackgroundForm from "./Forms/BackgroundForm.vue";
import PageNumberForm from "./Forms/PageNumberForm.vue";
import MetaForm from "./Forms/MetaForm.vue";
import DualLayerForm from "./Forms/DualLayerForm.vue";
import PasswordCrackForm from "./Forms/PasswordCrackForm.vue";


const IconFont = createFromIconfontCN({ scriptUrl: '//at.alicdn.com/t/font_8d5l8fzk5b87iudi.js' });

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
        FormOutlined,
        DeleteOutlined,
        MergeCellsOutlined,
        InfoCircleOutlined,
        BookOutlined,
        CreditCardOutlined,
        BgColorsOutlined,
        SafetyCertificateOutlined,
        TabletOutlined,
        FieldBinaryOutlined,
        SyncOutlined,
        FileSearchOutlined,
        ToolOutlined,
        IconFont,
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
        // 裁剪
        CropForm,
        // 分割/组合
        CutForm,
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
        // 页眉页脚
        HeaderAndFooterForm,
        // 文档背景
        BackgroundForm,
        // 页码设置
        PageNumberForm,
        // 文档属性
        MetaForm,
        // 双层PDF
        DualLayerForm,
        // 密码破解
        PasswordCrackForm
    },
    setup() {
        const state = reactive({
            rootSubmenuKeys: ['page_edit', 'protect', 'other', "settings"],
            selectedKeys: ["insert"],
            openKeys: ["page_edit"]
        });
        const onOpenChange = (openKeys: string[]) => {
            const latestOpenKey = openKeys.find(key => state.openKeys.indexOf(key) === -1);
            if (state.rootSubmenuKeys.indexOf(latestOpenKey!) === -1) {
                state.openKeys = openKeys;
            } else {
                state.openKeys = latestOpenKey ? [latestOpenKey] : [];
            }
        };
        return {
            menuRecord,
            menuDesc,
            state,
            onOpenChange
        };
    },
});
</script>