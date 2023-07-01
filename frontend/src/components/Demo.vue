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
                    <a-form ref="formRef"
                        style="border: 1px solid #dddddd; padding: 10px 0;border-radius: 10px;margin-right: 5vw;"
                        :model="formState" :label-col="{ span: 3 }" :wrapper-col="{ offset: 1, span: 18 }">
                        <!-- PDF合并 -->
                        <div v-if="currentMenu.at(0) == 'merge'">
                            <a-form-item :label="index === 0 ? '输入路径列表' : ' '" :colon="index === 0 ? true : false"
                                v-for="(item, index) in formState.merge_path_list" :key="index">
                                <a-input v-model:value="formState.merge_path_list[index]" style="width: 95%;"
                                    placeholder="待合并pdf文件路径" />
                                <MinusCircleOutlined @click="removePath(item)" style="margin-left: 1vw;" />
                            </a-form-item>
                            <a-form-item name="span" :label="formState.merge_path_list.length === 0 ? '输入路径列表' : ' '"
                                :colon="formState.merge_path_list.length === 0 ? true : false">
                                <a-button type="dashed" block @click="addPath">
                                    <PlusOutlined />
                                    添加路径
                                </a-button>
                            </a-form-item>
                            <a-form-item name="merge_sort" label="排序字段">
                                <a-radio-group v-model:value="formState.merge_sort">
                                    <a-radio value="hand">添加顺序</a-radio>
                                    <a-radio value="name">文件名</a-radio>
                                    <a-radio value="create">创建时间</a-radio>
                                    <a-radio value="modify">修改时间</a-radio>
                                </a-radio-group>
                            </a-form-item>
                            <a-form-item label="排序方向">
                                <a-radio-group v-model:value="formState.merge_sort_direction"
                                    v-if="currentMenu.at(0) == 'merge'">
                                    <a-radio value="asc">升序</a-radio>
                                    <a-radio value="desc">降序</a-radio>
                                </a-radio-group>
                            </a-form-item>
                        </div>
                        <!-- PDF拆分 -->
                        <div v-if="currentMenu.at(0) == 'split'">
                            <a-form-item name="split_mode" label="类型">
                                <a-radio-group button-style="solid" v-model:value="formState.split_mode">
                                    <a-radio-button value="span">均匀分块</a-radio-button>
                                    <a-radio-button value="range">自定义范围</a-radio-button>
                                    <a-radio-button value="bookmark">目录</a-radio-button>
                                </a-radio-group>
                            </a-form-item>
                            <a-form-item name="span" label="块大小" v-if="formState.split_mode == 'span'">
                                <a-input-number v-model:value="formState.split_span" :min="1" />
                            </a-form-item>
                            <a-form-item name="span" label="页码范围" v-if="formState.split_mode == 'range'">
                                <a-input v-model:value="formState.split_ranges"
                                    placeholder="自定义页码范围,用英文逗号隔开,e.g. 1-10,11-15,16-19" />
                            </a-form-item>
                            <a-form-item name="span" label="目录级别" v-if="formState.split_mode == 'bookmark'">
                                <a-select v-model:value="formState.split_bookmark_level" style="width: 200px">
                                    <a-select-option value="1">一级标题</a-select-option>
                                    <a-select-option value="2">二级标题</a-select-option>
                                    <a-select-option value="3">三级标题</a-select-option>
                                </a-select>
                            </a-form-item>
                        </div>
                        <!-- PDF删除 -->
                        <div v-if="currentMenu.at(0) == 'delete'">
                            <a-form-item name="page" label="页码范围">
                                <a-input v-model:value="formState.page" placeholder="待删除的页码范围, e.g. 1-10" />
                            </a-form-item>
                        </div>
                        <!-- PDF旋转 -->
                        <div v-if="currentMenu.at(0) == 'rotate'">
                            <a-form-item name="rotate" label="操作">
                                <a-radio-group button-style="solid" v-model:value="formState.rotate_op">
                                    <a-radio-button value="rotate">旋转</a-radio-button>
                                    <a-radio-button value="flip">翻转</a-radio-button>
                                </a-radio-group>
                            </a-form-item>
                            <a-form-item name="rotate" label="旋转角度" v-if="formState.rotate_op == 'rotate'">
                                <a-radio-group v-model:value="formState.rotate_degree">
                                    <a-radio :value="90">顺时针90</a-radio>
                                    <a-radio :value="180">顺时针180</a-radio>
                                    <a-radio :value="270">逆时针90</a-radio>
                                </a-radio-group>
                            </a-form-item>
                            <a-form-item name="rotate" label="翻转类型" v-if="formState.rotate_op == 'flip'">
                                <a-radio-group v-model:value="formState.rotate_flip_method">
                                    <a-radio value="horizontal">水平翻转</a-radio>
                                    <a-radio value="vertical">垂直翻转</a-radio>
                                </a-radio-group>
                            </a-form-item>
                            <a-form-item name="page" label="页码范围">
                                <a-input v-model:value="formState.page" placeholder="应用的页码范围, e.g. 1-10" />
                            </a-form-item>
                        </div>

                        <!-- PDF书签 -->
                        <div v-if="currentMenu.at(0) == 'bookmark'">
                            <a-form-item name="bookmark_op" label="操作">
                                <a-radio-group button-style="solid" v-model:value="formState.bookmark_op">
                                    <a-radio-button value="extract">提取书签</a-radio-button>
                                    <a-radio-button value="write">写入书签</a-radio-button>
                                    <a-radio-button value="transform">转换书签</a-radio-button>
                                    <a-radio-button value="recognize">识别书签</a-radio-button>
                                </a-radio-group>
                            </a-form-item>
                            <div v-if="formState.bookmark_op == 'extract'">
                                <a-form-item name="bookmark_extract_format" label="导出格式">
                                    <a-select v-model:value="formState.bookmark_extract_format" style="width: 200px">
                                        <a-select-option value="txt">txt</a-select-option>
                                        <a-select-option value="json">json</a-select-option>
                                    </a-select>
                                </a-form-item>
                            </div>
                            <div v-if="formState.bookmark_op == 'write'">
                                <a-form-item name="bookmark_write_type" label="类型" :rules="{ required: true }">
                                    <a-radio-group v-model:value="formState.bookmark_write_type">
                                        <a-radio value="file">书签文件导入</a-radio>
                                        <a-radio value="page">页码书签</a-radio>
                                    </a-radio-group>
                                </a-form-item>
                                <a-form-item name="bookmark_file" label="书签文件" :rules="{ required: true }"
                                    v-if="formState.bookmark_write_type == 'file'">
                                    <a-input v-model:value="formState.bookmark_file" placeholder="书签文件路径" />
                                </a-form-item>
                                <a-form-item name="bookmark_write_offset" label="页码偏移量" :rules="{ required: true }"
                                    v-if="formState.bookmark_write_type == 'file'">
                                    <a-input-number v-model:value="formState.bookmark_write_offset" placeholder="页码偏移量" />
                                </a-form-item>
                                <a-form-item name="bookmark_write_gap" label="间隔页数" :rules="{ required: true }"
                                    v-if="formState.bookmark_write_type == 'page'">
                                    <a-input-number v-model:value="formState.bookmark_write_gap" placeholder="间隔页数" />
                                </a-form-item>
                                <a-form-item name="bookmark_write_format" label="命名格式"
                                    v-if="formState.bookmark_write_type == 'page'">
                                    <a-input v-model:value="formState.bookmark_write_format"
                                        placeholder="e.g. 第%p页(%p表示页码)" />
                                </a-form-item>
                            </div>
                            <div v-if="formState.bookmark_op == 'transform'">
                                <a-form-item name="bookmark_transform_offset" label="页码偏移量" :rules="{ required: true }">
                                    <a-input-number v-model:value="formState.bookmark_transform_offset"
                                        placeholder="页码偏移量" />
                                </a-form-item>
                                <a-form-item name="bookmark_transform_indent" label="增加缩进" :rules="{ required: true }">
                                    <a-switch v-model:checked="formState.bookmark_transform_indent" />
                                </a-form-item>
                                <a-form-item name="bookmark_transform_dots" label="删除尾部点" :rules="{ required: true }">
                                    <a-switch v-model:checked="formState.bookmark_transform_dots" />
                                </a-form-item>
                            </div>
                            <div v-if="formState.bookmark_op == 'recognize'">
                                <a-form-item name="bookmark_ocr_lang" label="语言">
                                    <a-select v-model:value="formState.bookmark_ocr_lang" style="width: 200px">
                                        <a-select-option value="ch">简体中文</a-select-option>
                                        <a-select-option value="en">英文</a-select-option>
                                    </a-select>
                                </a-form-item>
                                <a-form-item name="bookmark_ocr_double_column" label="双栏">
                                    <a-switch v-model:checked="formState.bookmark_ocr_double_column" />
                                </a-form-item>
                                <a-form-item name="bookmark_ocr_range" label="目录页码范围">
                                    <a-input v-model:value="formState.page" placeholder="e.g. 1-10,11-15,16-19" />
                                </a-form-item>
                            </div>
                        </div>
                        <!-- PDF裁剪/分割 -->
                        <div v-if="currentMenu.at(0) == 'crop'">
                            <a-form-item name="crop_op" label="操作">
                                <a-radio-group button-style="solid" v-model:value="formState.crop_op">
                                    <a-radio-button value="crop">裁剪</a-radio-button>
                                    <a-radio-button value="split">分割</a-radio-button>
                                </a-radio-group>
                            </a-form-item>
                            <a-form-item label="单位" v-if="formState.crop_op == 'crop'">
                                <a-radio-group v-model:value="formState.crop_unit">
                                    <a-radio value="cm">厘米</a-radio>
                                    <a-radio value="mm">毫米</a-radio>
                                    <a-radio value="px">像素</a-radio>
                                    <a-radio value="in">英寸</a-radio>
                                </a-radio-group>
                            </a-form-item>
                            <a-form-item name="crop_type" label="页边距" v-if="formState.crop_op == 'crop'">
                                <a-space size="large">
                                    <a-input-number v-model:value="formState.crop_up" :min="0">
                                        <template #addonBefore>
                                            上
                                        </template>
                                    </a-input-number>
                                    <a-input-number v-model:value="formState.crop_left" :min="0">
                                        <template #addonBefore>
                                            左
                                        </template>
                                    </a-input-number>
                                    <a-input-number v-model:value="formState.crop_down" :min="0">
                                        <template #addonBefore>
                                            下
                                        </template>
                                    </a-input-number>
                                    <a-input-number v-model:value="formState.crop_right" :min="0">
                                        <template #addonBefore>
                                            右
                                        </template>
                                    </a-input-number>
                                </a-space>
                            </a-form-item>
                            <a-form-item label="分割类型" v-if="formState.crop_op == 'split'">
                                <a-radio-group v-model:value="formState.crop_split_type">
                                    <a-radio value="even">均匀分割</a-radio>
                                    <a-radio value="custom">自定义分割</a-radio>
                                </a-radio-group>
                            </a-form-item>
                            <a-form-item label="网格形状"
                                v-if="formState.crop_op == 'split' && formState.crop_split_type == 'even'">
                                <a-space size="large">
                                    <a-input-number v-model:value="formState.crop_split_rows" :min="1">
                                        <template #addonBefore>
                                            行数
                                        </template>
                                    </a-input-number>
                                    <a-input-number v-model:value="formState.crop_split_cols" :min="1">
                                        <template #addonBefore>
                                            列数
                                        </template>
                                    </a-input-number>
                                </a-space>
                            </a-form-item>
                            <a-form-item :label="index === 0 ? '水平分割线' : ' '" :colon="index === 0 ? true : false"
                                v-if="formState.crop_op == 'split' && formState.crop_split_type == 'custom'"
                                v-for="(item, index) in formState.crop_split_h_breakpoints" :key="index">
                                <a-input-number :min="0" :max="100" :formatter="(value: any) => `${value}%`"
                                    :parser="(value: any) => value.replace('%', '')" />
                                <MinusCircleOutlined @click="removeHBreakpoint(item)" style="margin-left: 1vw;" />
                            </a-form-item>
                            <a-form-item name="span"
                                :label="formState.crop_split_h_breakpoints.length === 0 ? '水平分割线' : ' '"
                                :colon="formState.crop_split_h_breakpoints.length === 0 ? true : false"
                                v-if="formState.crop_op == 'split' && formState.crop_split_type == 'custom'">
                                <a-button type="dashed" block @click="addHBreakpoint">
                                    <PlusOutlined />
                                    添加水平分割线
                                </a-button>
                            </a-form-item>
                            <a-form-item :label="index === 0 ? '垂直分割线' : ' '" :colon="index === 0 ? true : false"
                                v-if="formState.crop_op == 'split' && formState.crop_split_type == 'custom'"
                                v-for="(item, index) in formState.crop_split_v_breakpoints" :key="index">
                                <a-input-number :min="0" :max="100" :formatter="(value: any) => `${value}%`"
                                    :parser="(value: any) => value.replace('%', '')" />
                                <MinusCircleOutlined @click="removeVBreakpoint(item)" style="margin-left: 1vw;" />
                            </a-form-item>
                            <a-form-item name="span"
                                :label="formState.crop_split_v_breakpoints.length === 0 ? '垂直分割线' : ' '"
                                :colon="formState.crop_split_v_breakpoints.length === 0 ? true : false"
                                v-if="formState.crop_op == 'split' && formState.crop_split_type == 'custom'">
                                <a-button type="dashed" block @click="addVBreakpoint">
                                    <PlusOutlined />
                                    添加垂直分割线
                                </a-button>
                            </a-form-item>
                            <a-form-item name="page" label="页码范围">
                                <a-input v-model:value="formState.page" placeholder="应用的页码范围, e.g. 1-10" />
                            </a-form-item>
                        </div>

                        <!-- PDF提取 -->
                        <div v-if="currentMenu.at(0) == 'extract'">
                            <a-form-item name="extract_op" label="提取类型">
                                <a-radio-group button-style="solid" v-model:value="formState.extract_op">
                                    <a-radio-button value="text">文本</a-radio-button>
                                    <a-radio-button value="image">图片</a-radio-button>
                                    <a-radio-button value="table">表格</a-radio-button>
                                </a-radio-group>
                            </a-form-item>
                            <a-form-item name="page" label="页码范围">
                                <a-input v-model:value="formState.page" placeholder="应用的页码范围, e.g. 1-10" />
                            </a-form-item>
                        </div>
                        <!-- PDF缩放 -->
                        <div v-if="currentMenu.at(0) == 'scale'">
                            <a-form-item name="scale_conf" label="缩放参数">
                                <a-input v-model:value="formState.scale_conf" placeholder="缩放参数" />
                            </a-form-item>
                            <a-form-item name="page" label="页码范围">
                                <a-input v-model:value="formState.page" placeholder="应用的页码范围, e.g. 1-10" />
                            </a-form-item>
                        </div>
                        <!-- PDF转换 -->
                        <div v-if="currentMenu.at(0) == 'convert'">
                            <a-form-item name="convert_type" label="转换类型">
                                <a-select v-model:value="formState.convert_type" style="width: 200px">
                                    <a-select-opt-group label="PDF转其他">
                                        <a-select-option value="pdf2png">pdf转png</a-select-option>
                                        <a-select-option value="pdf2svg">pdf转svg</a-select-option>
                                        <a-select-option value="pdf2html">pdf转html</a-select-option>
                                        <a-select-option value="pdf2word">pdf转word</a-select-option>
                                    </a-select-opt-group>
                                    <a-select-opt-group label="其他转PDF">
                                        <a-select-option value="png2pdf">png转pdf</a-select-option>
                                        <a-select-option value="svg2pdf">svg转pdf</a-select-option>
                                        <a-select-option value="word2pdf">word转pdf</a-select-option>
                                    </a-select-opt-group>
                                </a-select>
                            </a-form-item>
                            <a-form-item name="page" label="页码范围" v-if="formState.convert_type.startsWith('pdf')">
                                <a-input v-model:value="formState.page" placeholder="应用的页码范围, e.g. 1-3,9-10" />
                            </a-form-item>
                        </div>
                        <!-- PDF加解密 -->
                        <div v-if="currentMenu.at(0) == 'encrypt'">
                            <a-form-item name="encrypt_op" label="类型" style="margin-bottom: 1vh;">
                                <a-radio-group button-style="solid" v-model:value="formState.encrypt_op">
                                    <a-radio-button value="encrypt">加密</a-radio-button>
                                    <a-radio-button value="decrypt">解密</a-radio-button>
                                </a-radio-group>
                            </a-form-item>
                            <a-form-item name="encrypt_opw" label="所有者密码" v-if="false">
                                <a-input v-model:value="formState.encrypt_opw" placeholder="所有者密码" />
                            </a-form-item>
                            <div style="border: 1px solid #dddddd;border-radius: 10px;margin: 0 1vw;"
                                v-if="formState.encrypt_op == 'encrypt'">
                                <a-form-item name="encrypt_opw" label="设置打开密码" :disabled="!formState.encrypt_is_set_upw">
                                    <a-checkbox v-model:checked="formState.encrypt_is_set_upw"></a-checkbox>
                                </a-form-item>
                                <a-form-item name="encrypt_upw" label="设置密码"
                                    :rules="[{ required: formState.encrypt_is_set_upw, validator: validatePass, trigger: 'change' }]">
                                    <a-input-password v-model:value="formState.encrypt_upw" placeholder="不少于6位"
                                        :disabled="!formState.encrypt_is_set_upw" />
                                </a-form-item>
                                <a-form-item name="encrypt_upw_confirm" label="确认密码"
                                    :rules="[{ required: formState.encrypt_is_set_upw, validator: validatePassUpwConfirm, trigger: 'change' }]">
                                    <a-input-password v-model:value="formState.encrypt_upw_confirm" placeholder="再次输入密码"
                                        :disabled="!formState.encrypt_is_set_upw" />
                                </a-form-item>
                            </div>

                            <div style="border: 1px solid #dddddd;border-radius: 10px;margin: 1vw 1vw;"
                                v-if="formState.encrypt_op == 'encrypt'">
                                <a-form-item name="encrypt_opw" label="设置权限密码">
                                    <a-checkbox v-model:checked="formState.encrypt_is_set_opw"></a-checkbox>
                                </a-form-item>
                                <a-form-item name="encrypt_opw" label="设置密码"
                                    :rules="[{ required: formState.encrypt_is_set_opw, validator: validatePass, trigger: 'change' }]">
                                    <a-input-password v-model:value="formState.encrypt_opw" placeholder="不少于6位"
                                        :disabled="!formState.encrypt_is_set_opw" />
                                </a-form-item>
                                <a-form-item name="encrypt_opw_confirm" label="确认密码"
                                    :rules="[{ required: formState.encrypt_is_set_opw, validator: validatePassOpwConfirm, trigger: 'change' }]">
                                    <a-input-password v-model:value="formState.encrypt_opw_confirm" placeholder="再次输入密码"
                                        :disabled="!formState.encrypt_is_set_opw" />
                                </a-form-item>
                                <a-form-item name="encrypt_perm" label="限制功能"
                                    :rules="[{ required: formState.encrypt_is_set_opw }]">
                                    <a-checkbox v-model:checked="checkAll" :indeterminate="indeterminate"
                                        :disabled="!formState.encrypt_is_set_opw" @change="onCheckAllChange">全选</a-checkbox>
                                    <a-divider type="vertical" />
                                    <a-checkbox-group v-model:value="formState.encrypt_perm" :options="encrypt_perm_options"
                                        :disabled="!formState.encrypt_is_set_opw" />
                                </a-form-item>
                            </div>
                            <a-form-item name="encrypt_upw" label="密码" v-if="formState.encrypt_op == 'decrypt'"
                                :rules="[{ required: true }]">
                                <a-input-password v-model:value="formState.encrypt_upw" placeholder="解密密码" />
                            </a-form-item>
                        </div>

                        <!-- PDF水印 -->
                        <div v-if="currentMenu.at(0) == 'watermark'">
                            <a-form-item name="watermark_op" label="操作">
                                <a-radio-group button-style="solid" v-model:value="formState.watermark_op">
                                    <a-radio-button value="add">添加水印</a-radio-button>
                                    <a-radio-button value="remove">去除水印</a-radio-button>
                                </a-radio-group>
                            </a-form-item>
                            <div v-if="formState.watermark_op === 'add'">

                                <a-form-item name="watermark_type" label="水印类型">
                                    <a-radio-group v-model:value="formState.watermark_type">
                                        <a-radio value="text">文本</a-radio>
                                        <a-radio value="image" disabled>图片</a-radio>
                                    </a-radio-group>
                                </a-form-item>
                                <a-form-item name="watermark_text" label="水印文本">
                                    <a-input v-model:value="formState.watermark_text" placeholder="e.g. 这是水印" />
                                </a-form-item>
                                <a-form-item name="watermark_font_size" label="字体属性">
                                    <a-space size="large">
                                        <a-select v-model:value="formState.watermark_font_family" style="width: 200px">
                                            <a-select-option value="msyh.ttc">微软雅黑</a-select-option>
                                            <a-select-option value="simsun.ttc">宋体</a-select-option>
                                            <a-select-option value="simhei.ttf">黑体</a-select-option>
                                            <a-select-option value="simkai.ttf">楷体</a-select-option>
                                            <a-select-option value="simfang.ttf">仿宋</a-select-option>
                                            <a-select-option value="SIMYOU.TTF">幼圆</a-select-option>
                                            <a-select-option value="STHUPO.TTF">华文琥珀</a-select-option>
                                            <a-select-option value="FZSTK.TTF">方正舒体</a-select-option>
                                            <a-select-option value="STZHONGS.TTF">华文中宋</a-select-option>
                                            <a-select-option value="arial.ttf">Arial</a-select-option>
                                            <a-select-option value="times.ttf">TimesNewRoman</a-select-option>
                                            <a-select-option value="calibri.ttf">Calibri</a-select-option>
                                            <a-select-option value="consola.ttf">Consola</a-select-option>
                                        </a-select>
                                        <a-tooltip>
                                            <template #title>字号</template>
                                            <a-input-number v-model:value="formState.watermark_font_size" :min="1">
                                                <template #prefix>
                                                    <font-size-outlined />
                                                </template>
                                            </a-input-number>
                                        </a-tooltip>
                                        <a-tooltip>
                                            <template #title>字体颜色</template>
                                            <a-input v-model:value="formState.watermark_font_color" placeholder="字体颜色"
                                                :defaultValue="formState.watermark_font_color">
                                                <template #prefix>
                                                    <font-colors-outlined />
                                                </template>
                                            </a-input>
                                        </a-tooltip>
                                    </a-space>
                                </a-form-item>
                                <a-form-item name="watermark_font_opacity" label="水印属性">
                                    <a-space size="large">
                                        <a-input-number v-model:value="formState.watermark_font_opacity" :min="0" :max="1"
                                            :step="0.01">
                                            <template #addonBefore>
                                                不透明度
                                            </template>
                                        </a-input-number>
                                        <a-input-number v-model:value="formState.watermark_rotate" :min="0" :max="360">
                                            <template #addonBefore>
                                                旋转角度
                                            </template>
                                        </a-input-number>
                                        <a-input-number v-model:value="formState.watermark_space" :min="0" :max="360">
                                            <template #addonBefore>
                                                文字间距
                                            </template>
                                        </a-input-number>
                                        <a-input-number v-model:value="formState.watermark_quaility" :min="0" :max="360">
                                            <template #addonBefore>
                                                图片质量
                                            </template>
                                        </a-input-number>
                                    </a-space>
                                </a-form-item>
                            </div>
                            <a-form-item name="page" label="页码范围">
                                <a-input v-model:value="formState.page" placeholder="应用的页码范围, e.g. 1-10" />
                            </a-form-item>
                        </div>

                        <!-- OCR识别 -->
                        <div v-if="currentMenu.at(0) == 'ocr'">
                            <a-form-item label="语言">
                                <a-select v-model:value="formState.ocr_lang" style="width: 200px">
                                    <a-select-option value="ch">中文简体</a-select-option>
                                    <a-select-option value="en">英文</a-select-option>
                                </a-select>
                            </a-form-item>
                            <a-form-item label="是否双栏">
                                <a-checkbox v-model:checked="formState.ocr_double_column"></a-checkbox>
                            </a-form-item>
                            <a-form-item name="page" label="页码范围">
                                <a-input v-model:value="formState.page" placeholder="应用的页码范围, e.g. 1-10" />
                            </a-form-item>
                        </div>
                        <!-- 通用 -->
                        <div v-if="currentMenu.at(0) != 'settings'">
                            <a-form-item name="input" label="输入" :rules="[{ required: true, message: '请输入路径!' }]"
                                v-if="currentMenu.at(0) != 'merge'">
                                <a-input v-model:value="formState.input" placeholder="输入文件路径" />
                            </a-form-item>
                            <a-form-item name="output" label="输出">
                                <a-input v-model:value="formState.output" placeholder="输出目录" />
                            </a-form-item>
                            <a-form-item :wrapperCol="{ offset: 4 }" style="margin-bottom: 10px;">
                                <a-button type="primary" html-type="submit" @click="onSubmit"
                                    :loading="confirmLoading">确认</a-button>
                                <a-button style="margin-left: 10px" @click="resetFields">重置</a-button>
                            </a-form-item>
                        </div>
                        <div v-if="currentMenu.at(0) == 'settings'">
                            <a-form-item label="ocr路径">
                                <a-input v-model:value="formState.output" placeholder="填写ocr路径" disabled></a-input>
                            </a-form-item>
                            <a-form-item label="pandoc路径">
                                <a-input v-model:value="formState.output" placeholder="填写ocr路径" disabled></a-input>
                            </a-form-item>
                            <a-form-item :wrapperCol="{ offset: 4 }" style="margin-bottom: 10px;">
                                <a-button type="primary" html-type="submit" @click="onSubmit" :loading="confirmLoading">修改
                                </a-button>
                            </a-form-item>
                        </div>
                    </a-form>
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
    SplitCellsOutlined
} from '@ant-design/icons-vue';
import { message, Modal } from 'ant-design-vue';
import {
    MergePDF,
    ScalePDF,
    ReorderPDF,
    CompressPDF,
    SplitPDF,
    RotatePDF,
    ConvertPDF,
    EncryptPDF,
    DecryptPDF,
    ExtractBookmark,
    TransformBookmark,
    WriteBookmarkByFile,
    WriteBookmarkByGap,
    WatermarkPDF,
    OCR
} from '../../wailsjs/go/main/App';
import type { FormInstance } from 'ant-design-vue';
import type { Rule } from 'ant-design-vue/es/form';
import { menuDesc, menuRecord } from "./data";

export default defineComponent({
    components: {
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
        SplitCellsOutlined
    },
    setup() {
        const formRef = ref<FormInstance>();
        const encrypt_perm_options = [
            "复制", "注释", "打印", "表单", "插入/删除页面"
        ];
        const confirmLoading = ref<boolean>(false);
        const indeterminate = ref<boolean>(false);
        const checkAll = ref<boolean>(false);
        const formState = reactive<{
            // 合并
            merge_path_list: string[],
            merge_sort: string,
            merge_sort_direction: string,
            // 拆分
            split_mode: string,
            split_span: number,
            split_ranges: string,
            split_bookmark_level: string,
            // 裁剪/分割
            crop_op: string,
            crop_unit: string,
            crop_up: number,
            crop_left: number,
            crop_down: number,
            crop_right: number,
            crop_split_h_breakpoints: number[],
            crop_split_v_breakpoints: number[],
            crop_split_type: string,
            crop_split_rows: number,
            crop_split_cols: number,
            // 提取
            extract_op: string,
            // 加密
            encrypt_op: string,
            encrypt_perm: string[],
            encrypt_is_set_upw: boolean,
            encrypt_is_set_opw: boolean,
            encrypt_upw: string,
            encrypt_opw: string,
            encrypt_upw_confirm: string,
            encrypt_opw_confirm: string,
            convert_type: string,
            // 水印
            watermark_op: string,
            watermark_type: string,
            watermark_text: string,
            watermark_font_family: string,
            watermark_font_size: number,
            watermark_font_color: string,
            watermark_font_opacity: number,
            watermark_quaility: number,
            watermark_rotate: number,
            watermark_space: number,
            // 缩放
            scale_conf: string,
            // 旋转
            rotate_op: string,
            rotate_degree: number,
            rotate_flip_method: string,
            // 书签
            bookmark_op: string,
            bookmark_file: string,
            bookmark_write_type: string,
            bookmark_write_format: string,
            bookmark_write_offset: number,
            bookmark_write_gap: number,
            bookmark_extract_format: string,
            bookmark_transform_offset: number,
            bookmark_transform_indent: boolean,
            bookmark_transform_dots: boolean,
            bookmark_ocr_lang: string,
            bookmark_ocr_double_column: boolean,

            // ocr
            ocr_lang: string,
            ocr_double_column: boolean,
            // 通用
            page: string,
            input: string,
            output: string
        }>({
            // 合并
            merge_path_list: [],
            merge_sort: "hand",
            merge_sort_direction: "asc",
            // 拆分
            split_mode: "span",
            split_span: 5,
            split_ranges: "",
            split_bookmark_level: "1",
            // 裁剪/分割
            crop_op: "crop",
            crop_unit: "cm",
            crop_up: 0,
            crop_left: 0,
            crop_down: 0,
            crop_right: 0,
            crop_split_h_breakpoints: [],
            crop_split_v_breakpoints: [],
            crop_split_type: "even",
            crop_split_rows: 1,
            crop_split_cols: 1,
            // 提取
            extract_op: "text",
            // 加密
            encrypt_op: "encrypt",
            encrypt_perm: ["打开"],
            encrypt_is_set_upw: false,
            encrypt_is_set_opw: false,
            encrypt_upw: "",
            encrypt_opw: "",
            encrypt_upw_confirm: "",
            encrypt_opw_confirm: "",
            convert_type: "pdf2png",
            // 水印
            watermark_op: "add",
            watermark_type: "text",
            watermark_text: "",
            watermark_font_family: "msyh.ttc",
            watermark_font_size: 14,
            watermark_font_color: "#808080",
            watermark_font_opacity: 0.15,
            watermark_quaility: 80,
            watermark_rotate: 30,
            watermark_space: 75,
            // 缩放
            scale_conf: "",
            // 旋转
            rotate_op: "rotate",
            rotate_degree: 90,
            rotate_flip_method: "horizontal",
            // 书签
            bookmark_op: "extract",
            bookmark_file: "",
            bookmark_write_type: "file",
            bookmark_write_format: "",
            bookmark_write_offset: 0,
            bookmark_write_gap: 1,
            bookmark_extract_format: "txt",
            bookmark_transform_offset: 0,
            bookmark_transform_indent: false,
            bookmark_transform_dots: false,
            bookmark_ocr_lang: "ch",
            bookmark_ocr_double_column: false,
            // ocr
            ocr_lang: "ch",
            ocr_double_column: false,
            // 通用
            page: "",
            input: "",
            output: ""
        });

        // 加密密码验证
        let validatePass = async (_rule: Rule, value: string) => {
            if (value === '') {
                return Promise.reject('Please input the password');
            } else {
                if (value.length < 6) {
                    return Promise.reject('Password length must be greater than 6');
                }
                return Promise.resolve();
            }
        };
        let validatePassUpwConfirm = async (_rule: Rule, value: string) => {
            if (value === '') {
                return Promise.reject('Please input the password again');
            } else if (value !== formState.encrypt_upw) {
                return Promise.reject("Two inputs don't match!");
            } else {
                return Promise.resolve();
            }
        };
        let validatePassOpwConfirm = async (_rule: Rule, value: string) => {
            if (value === '') {
                return Promise.reject('Please input the password again');
            } else if (value !== formState.encrypt_opw) {
                return Promise.reject("Two inputs don't match!");
            } else {
                return Promise.resolve();
            }
        };
        const resetFields = () => {
            formRef.value?.resetFields();
        }
        async function handleOps(func: any, args: any[]) {
            await func(...args).then((res: any) => {
                console.log({ res });
                if (!res) {
                    message.success('处理成功！');
                } else {
                    message.error('处理失败！');
                }
            }).catch((err: any) => {
                console.log({ err });
                Modal.error({
                    title: '处理失败！',
                    content: err,
                });
            });
        }
        const onSubmit = async () => {
            console.log(formState);
            confirmLoading.value = true;
            switch (currentMenu.value.at(0)) {
                case "split": {
                    await handleOps(SplitPDF, [formState.input, formState.split_mode, formState.split_span, formState.output]);
                    break;
                }
                case "merge": {
                    const inFiles = formState.input.split(";").map((item: string) => item.trim());
                    await handleOps(MergePDF, [inFiles, formState.output, "create", false]);
                    break;
                }
                case "reorder": {
                    await handleOps(ReorderPDF, [formState.input, formState.output, formState.page]);
                    break;
                }
                case "bookmark": {
                    switch (formState.bookmark_op) {
                        case "extract": {
                            await handleOps(ExtractBookmark, [formState.input, formState.output, formState.bookmark_extract_format]);
                            break;
                        }
                        case "write": {
                            switch (formState.bookmark_write_type) {
                                case "file": {
                                    await handleOps(WriteBookmarkByFile, [formState.input, formState.output, formState.bookmark_file, formState.bookmark_write_offset]);
                                    break;
                                }
                                case "page": {
                                    await handleOps(WriteBookmarkByGap, [formState.input, formState.output, formState.bookmark_write_gap, formState.bookmark_write_format]);
                                    break;
                                }
                            }
                            break;
                        }
                        case "transform": {
                            await handleOps(TransformBookmark, [formState.input, formState.output, formState.bookmark_transform_indent, formState.bookmark_transform_offset, formState.bookmark_transform_dots]);
                            break;
                        }
                    }
                    break;
                }
                case "watermark": {
                    await handleOps(WatermarkPDF, [formState.input, formState.output, formState.watermark_text, formState.watermark_font_family, formState.watermark_font_size, formState.watermark_font_color, formState.watermark_rotate, formState.watermark_space, formState.watermark_font_opacity, formState.watermark_quaility]);
                    break;
                }
                case "rotate": {
                    await handleOps(RotatePDF, [formState.input, formState.output, formState.rotate_degree, formState.page]);
                    break;
                }
                case "crop": {
                    break;
                }
                case "delete": {
                    let pageStr = formState.page.split(",").map(item => {
                        return "!" + item.trim();
                    }).join(",");
                    await handleOps(ReorderPDF, [formState.input, formState.output, pageStr]);
                    break;
                }
                case "extract": {
                    break;
                }
                case "compress": {
                    await handleOps(CompressPDF, [formState.input, formState.output]);
                    break;
                }
                case "convert": {
                    await handleOps(ConvertPDF, [formState.input, formState.output, formState.convert_type, formState.page]);
                    break;
                }
                case "scale": {
                    await handleOps(ScalePDF, [formState.input, formState.output, formState.scale_conf, formState.page]);
                    break;
                }
                case "encrypt": {
                    switch (formState.encrypt_op) {
                        case "encrypt": {
                            let upw = "", opw = "", perm: string[] = [];
                            if (formState.encrypt_is_set_upw) { upw = formState.encrypt_upw; }
                            if (formState.encrypt_is_set_opw) {
                                opw = formState.encrypt_opw;
                                perm = formState.encrypt_perm;
                            }
                            await handleOps(EncryptPDF, [formState.input, formState.output, upw, opw, perm]);
                            break;
                        }
                        case "decrypt": {
                            await handleOps(DecryptPDF, [formState.input, formState.output, formState.encrypt_upw]);
                            break;
                        }
                    }
                    break;
                }
                case "ocr": {
                    await handleOps(OCR, [formState.input, formState.output, formState.page, formState.ocr_lang, formState.ocr_double_column]);
                    break;
                }
            }
            confirmLoading.value = false;
        }

        // 加密PDF
        const onCheckAllChange = (e: any) => {
            Object.assign(formState, {
                encrypt_perm: e.target.checked ? encrypt_perm_options : [],
            });
            indeterminate.value = false;
        };
        watch(
            () => formState.encrypt_perm,
            (val: any) => {
                indeterminate.value = !!val.length && val.length < encrypt_perm_options.length;
                checkAll.value = val.length === encrypt_perm_options.length;
            }
        )
        const currentMenu = ref<string[]>(['merge']);

        // 合并PDF
        const addPath = () => {
            formState.merge_path_list.push("");
        }
        const removePath = (item: string) => {
            const index = formState.merge_path_list.indexOf(item);
            if (index != -1) {
                formState.merge_path_list.splice(index, 1);
            }
        }
        // 分割PDF
        const addHBreakpoint = () => {
            formState.crop_split_h_breakpoints.push(0);
        }
        const removeHBreakpoint = (item: number) => {
            const index = formState.crop_split_h_breakpoints.indexOf(item);
            if (index != -1) {
                formState.crop_split_h_breakpoints.splice(index, 1);
            }
        }
        const addVBreakpoint = () => {
            formState.crop_split_v_breakpoints.push(0);
        }
        const removeVBreakpoint = (item: number) => {
            const index = formState.crop_split_v_breakpoints.indexOf(item);
            if (index != -1) {
                formState.crop_split_v_breakpoints.splice(index, 1);
            }
        }

        return {
            formRef,
            confirmLoading,
            indeterminate,
            checkAll,
            menuRecord,
            menuDesc,
            encrypt_perm_options,
            currentMenu,
            formState,
            onSubmit,
            onCheckAllChange,
            addPath,
            removePath,
            validatePass,
            validatePassUpwConfirm,
            validatePassOpwConfirm,
            resetFields,
            addHBreakpoint,
            removeHBreakpoint,
            addVBreakpoint,
            removeVBreakpoint
        };
    },
});
</script>