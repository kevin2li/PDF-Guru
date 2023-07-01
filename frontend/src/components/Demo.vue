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
                    <a-form ref="formRef"
                        style="border: 1px solid #dddddd; padding: 10px 0;border-radius: 10px;margin-right: 5vw;"
                        :model="formState" :label-col="{ span: 3 }" :wrapper-col="{ offset: 1, span: 18 }" :rules="rules">
                        <!-- PDF合并 -->
                        <div v-if="currentMenu.at(0) == 'merge'">
                            <a-form-item :label="index === 0 ? '输入路径列表' : ' '" :colon="index === 0 ? true : false"
                                name="merge_input" v-for="(item, index) in formState.merge.path_list" :key="index">
                                <a-input v-model:value="formState.merge.path_list[index]" style="width: 95%;" allow-clear
                                    placeholder="待合并pdf文件路径" />
                                <MinusCircleOutlined @click="removePath(item)" style="margin-left: 1vw;" />
                            </a-form-item>
                            <a-form-item name="span" :label="formState.merge.path_list.length === 0 ? '输入路径列表' : ' '"
                                :colon="formState.merge.path_list.length === 0 ? true : false">
                                <a-button type="dashed" block @click="addPath">
                                    <PlusOutlined />
                                    添加路径
                                </a-button>
                            </a-form-item>
                            <a-form-item name="merge.sort" label="排序字段">
                                <a-radio-group v-model:value="formState.merge.sort">
                                    <a-radio value="hand">添加顺序</a-radio>
                                    <a-radio value="name">文件名</a-radio>
                                    <a-radio value="create">创建时间</a-radio>
                                    <a-radio value="modify">修改时间</a-radio>
                                </a-radio-group>
                            </a-form-item>
                            <a-form-item label="排序方向">
                                <a-radio-group v-model:value="formState.merge.sort_direction"
                                    v-if="currentMenu.at(0) == 'merge'">
                                    <a-radio value="asc">升序</a-radio>
                                    <a-radio value="desc">降序</a-radio>
                                </a-radio-group>
                            </a-form-item>
                        </div>
                        <!-- PDF拆分 -->
                        <div v-if="currentMenu.at(0) == 'split'">
                            <a-form-item name="split_op" label="类型">
                                <a-radio-group button-style="solid" v-model:value="formState.split.op">
                                    <a-radio-button value="span">均匀分块</a-radio-button>
                                    <a-radio-button value="range">自定义范围</a-radio-button>
                                    <a-radio-button value="bookmark">目录</a-radio-button>
                                </a-radio-group>
                            </a-form-item>
                            <a-form-item name="span" label="块大小" v-if="formState.split.op == 'span'">
                                <a-input-number v-model:value="formState.split.span" :min="1" />
                            </a-form-item>
                            <a-form-item name="span" label="页码范围" v-if="formState.split.op == 'range'">
                                <a-input v-model:value="formState.split.ranges"
                                    placeholder="自定义页码范围,用英文逗号隔开,e.g. 1-10,11-15,16-19" />
                            </a-form-item>
                            <a-form-item name="span" label="目录级别" v-if="formState.split.op == 'bookmark'">
                                <a-select v-model:value="formState.split.bookmark_level" style="width: 200px">
                                    <a-select-option value="1">一级标题</a-select-option>
                                    <a-select-option value="2">二级标题</a-select-option>
                                    <a-select-option value="3">三级标题</a-select-option>
                                </a-select>
                            </a-form-item>
                            <a-form-item name="input" label="输入" has-feedback :validateStatus="validateStatus.input">
                                <a-input v-model:value="formState.input" placeholder="输入文件路径" allow-clear />
                            </a-form-item>
                        </div>
                        <!-- PDF删除 -->
                        <div v-if="currentMenu.at(0) == 'delete'">
                            <a-form-item name="page" label="页码范围">
                                <a-input v-model:value="formState.page" placeholder="待删除的页码范围(留空表示全部), e.g. 1-10" />
                            </a-form-item>
                            <a-form-item name="input" label="输入" has-feedback :validateStatus="validateStatus.input">
                                <a-input v-model:value="formState.input" placeholder="输入文件路径" allow-clear />
                            </a-form-item>
                        </div>
                        <!-- PDF重排 -->
                        <div v-if="currentMenu.at(0) == 'reorder'">
                            <a-form-item name="page" label="页码范围">
                                <a-input v-model:value="formState.page" placeholder="调整后的页码顺序, e.g. 1-10" />
                            </a-form-item>
                            <a-form-item name="input" label="输入" has-feedback :validateStatus="validateStatus.input">
                                <a-input v-model:value="formState.input" placeholder="输入文件路径" allow-clear />
                            </a-form-item>
                        </div>
                        <!-- PDF插入/替换 -->
                        <div v-if="currentMenu.at(0) == 'insert'">
                            <a-form-item name="insert_op" label="操作">
                                <a-radio-group button-style="solid" v-model:value="formState.insert.op">
                                    <a-radio-button value="insert">插入</a-radio-button>
                                    <a-radio-button value="replace">替换</a-radio-button>
                                </a-radio-group>
                            </a-form-item>
                            <a-form-item label="源PDF路径" name="insert_src_path" has-feedback
                                :validateStatus="validateStatus.insert_src_path">
                                <a-input v-model:value="formState.insert.src_path"
                                    :placeholder="formState.insert.op === 'insert' ? '被插入的PDF路径' : '被替换的PDF路径'"
                                    allow-clear></a-input>
                            </a-form-item>
                            <a-form-item name="page" label="插入位置" v-if="formState.insert.op == 'insert'">
                                <a-tooltip>
                                    <template #title>
                                        插入到指定页码之前
                                    </template>
                                    <a-input-number v-model:value="formState.insert.src_pos" placeholder="插入位置, e.g. 10"
                                        :min="1" />
                                </a-tooltip>
                            </a-form-item>
                            <a-form-item name="page" label="页码范围" v-if="formState.insert.op == 'replace'">
                                <a-input v-model:value="formState.insert.src_range"
                                    placeholder="被替换的页码范围(留空表示全部), e.g. 1-10" />
                            </a-form-item>
                            <a-form-item label="目标PDF路径" name="insert_dst_path" has-feedback
                                :validateStatus="validateStatus.insert_dst_path">
                                <a-input v-model:value="formState.insert.dst_path" placeholder="插入的PDF路径" allow-clear />
                            </a-form-item>
                            <a-form-item name="page" label="页码范围">
                                <a-input v-model:value="formState.insert.dst_range"
                                    placeholder="目标PDF的页码范围(留空表示全部), e.g. 1-10" />
                            </a-form-item>
                        </div>
                        <!-- PDF旋转 -->
                        <div v-if="currentMenu.at(0) == 'rotate'">
                            <!-- <a-form-item name="rotate" label="操作" >
                                <a-radio-group button-style="solid" v-model:value="formState.rotate_op">
                                    <a-radio-button value="rotate">旋转</a-radio-button>
                                    <a-radio-button value="flip">翻转</a-radio-button>
                                </a-radio-group>
                            </a-form-item> -->
                            <a-form-item name="rotate" label="旋转角度" v-if="formState.rotate.op == 'rotate'">
                                <a-radio-group v-model:value="formState.rotate.degree">
                                    <a-radio :value="90">顺时针90</a-radio>
                                    <a-radio :value="180">顺时针180</a-radio>
                                    <a-radio :value="270">逆时针90</a-radio>
                                </a-radio-group>
                            </a-form-item>
                            <!-- <a-form-item name="rotate" label="翻转类型" v-if="formState.rotate_op == 'flip'">
                                <a-radio-group v-model:value="formState.rotate_flip_method">
                                    <a-radio value="horizontal">水平翻转</a-radio>
                                    <a-radio value="vertical">垂直翻转</a-radio>
                                </a-radio-group>
                            </a-form-item> -->
                            <a-form-item name="page" label="页码范围">
                                <a-input v-model:value="formState.page" placeholder="应用的页码范围(留空表示全部), e.g. 1-10"
                                    allow-clear />
                            </a-form-item>
                            <a-form-item name="input" label="输入" has-feedback :validateStatus="validateStatus.input">
                                <a-input v-model:value="formState.input" placeholder="输入文件路径" allow-clear />
                            </a-form-item>
                        </div>

                        <!-- PDF书签 -->
                        <div v-if="currentMenu.at(0) == 'bookmark'">
                            <a-form-item name="bookmark_op" label="操作">
                                <a-radio-group button-style="solid" v-model:value="formState.bookmark.op">
                                    <a-radio-button value="extract">提取书签</a-radio-button>
                                    <a-radio-button value="write">写入书签</a-radio-button>
                                    <a-radio-button value="transform">转换书签</a-radio-button>
                                    <a-radio-button value="recognize">识别书签</a-radio-button>
                                </a-radio-group>
                            </a-form-item>
                            <div v-if="formState.bookmark.op == 'extract'">
                                <a-form-item name="bookmark.extract_format" label="导出格式">
                                    <a-select v-model:value="formState.bookmark.extract_format" style="width: 200px">
                                        <a-select-option value="txt">txt</a-select-option>
                                        <a-select-option value="json">json</a-select-option>
                                    </a-select>
                                </a-form-item>
                            </div>
                            <div v-if="formState.bookmark.op == 'write'">
                                <a-form-item name="bookmark.write_type" label="类型" :rules="{ required: true }">
                                    <a-radio-group v-model:value="formState.bookmark.write_type">
                                        <a-radio value="file">书签文件导入</a-radio>
                                        <a-radio value="page">页码书签</a-radio>
                                    </a-radio-group>
                                </a-form-item>
                                <a-form-item name="bookmark.file" label="书签文件" :rules="{ required: true }"
                                    v-if="formState.bookmark.write_type == 'file'">
                                    <a-input v-model:value="formState.bookmark.file" placeholder="书签文件路径" allow-clear />
                                </a-form-item>
                                <a-form-item name="bookmark.write_offset" label="页码偏移量" :rules="{ required: true }"
                                    v-if="formState.bookmark.write_type == 'file'">
                                    <a-input-number v-model:value="formState.bookmark.write_offset" placeholder="页码偏移量" />
                                </a-form-item>
                                <a-form-item name="bookmark.write_gap" label="间隔页数" :rules="{ required: true }"
                                    v-if="formState.bookmark.write_type == 'page'">
                                    <a-input-number v-model:value="formState.bookmark.write_gap" placeholder="间隔页数" />
                                </a-form-item>
                                <a-form-item name="bookmark.write_format" label="命名格式"
                                    v-if="formState.bookmark.write_type == 'page'">
                                    <a-input v-model:value="formState.bookmark.write_format" placeholder="e.g. 第%p页(%p表示页码)"
                                        allow-clear />
                                </a-form-item>
                            </div>
                            <div v-if="formState.bookmark.op == 'transform'">
                                <a-form-item name="bookmark.transform_offset" label="页码偏移量" :rules="{ required: true }">
                                    <a-input-number v-model:value="formState.bookmark.transform_offset"
                                        placeholder="页码偏移量" />
                                </a-form-item>
                                <a-form-item name="bookmark.transform_indent" label="增加缩进" :rules="{ required: true }">
                                    <a-switch v-model:checked="formState.bookmark.transform_indent" />
                                </a-form-item>
                                <a-form-item name="bookmark.transform_dots" label="删除尾部点" :rules="{ required: true }">
                                    <a-switch v-model:checked="formState.bookmark.transform_dots" />
                                </a-form-item>
                            </div>
                            <div v-if="formState.bookmark.op == 'recognize'">
                                <a-form-item name="bookmark.ocr_lang" label="语言">
                                    <a-select v-model:value="formState.bookmark.ocr_lang" style="width: 200px">
                                        <a-select-option value="ch">简体中文</a-select-option>
                                        <a-select-option value="en">英文</a-select-option>
                                    </a-select>
                                </a-form-item>
                                <a-form-item name="bookmark.ocr_double_column" label="双栏">
                                    <a-switch v-model:checked="formState.bookmark.ocr_double_column" />
                                </a-form-item>
                                <a-form-item name="bookmark.ocr_range" label="目录页码范围">
                                    <a-input v-model:value="formState.page" placeholder="e.g. 1-10,11-15,16-19"
                                        allow-clear />
                                </a-form-item>
                            </div>
                            <a-form-item name="input" label="输入" has-feedback :validateStatus="validateStatus.input">
                                <a-input v-model:value="formState.input" placeholder="输入文件路径" allow-clear />
                            </a-form-item>
                        </div>
                        <!-- PDF裁剪/分割 -->
                        <div v-if="currentMenu.at(0) == 'crop'">
                            <a-form-item name="crop_op" label="操作">
                                <a-radio-group button-style="solid" v-model:value="formState.crop.op">
                                    <a-radio-button value="crop">裁剪</a-radio-button>
                                    <a-radio-button value="split">分割</a-radio-button>
                                </a-radio-group>
                            </a-form-item>
                            <a-form-item label="单位" v-if="formState.crop.op == 'crop'">
                                <a-radio-group v-model:value="formState.crop.unit">
                                    <a-radio value="cm">厘米</a-radio>
                                    <a-radio value="mm">毫米</a-radio>
                                    <a-radio value="px">像素</a-radio>
                                    <a-radio value="in">英寸</a-radio>
                                </a-radio-group>
                            </a-form-item>
                            <a-form-item name="crop.type" label="页边距" v-if="formState.crop.op == 'crop'">
                                <a-space size="large">
                                    <a-input-number v-model:value="formState.crop.up" :min="0">
                                        <template #addonBefore>
                                            上
                                        </template>
                                    </a-input-number>
                                    <a-input-number v-model:value="formState.crop.left" :min="0">
                                        <template #addonBefore>
                                            左
                                        </template>
                                    </a-input-number>
                                    <a-input-number v-model:value="formState.crop.down" :min="0">
                                        <template #addonBefore>
                                            下
                                        </template>
                                    </a-input-number>
                                    <a-input-number v-model:value="formState.crop.right" :min="0">
                                        <template #addonBefore>
                                            右
                                        </template>
                                    </a-input-number>
                                </a-space>
                            </a-form-item>
                            <a-form-item label="分割类型" v-if="formState.crop.op == 'split'">
                                <a-radio-group v-model:value="formState.crop.split_type">
                                    <a-radio value="even">均匀分割</a-radio>
                                    <a-radio value="custom">自定义分割</a-radio>
                                </a-radio-group>
                            </a-form-item>
                            <a-form-item label="网格形状"
                                v-if="formState.crop.op == 'split' && formState.crop.split_type == 'even'">
                                <a-space size="large">
                                    <a-input-number v-model:value="formState.crop.split_rows" :min="1">
                                        <template #addonBefore>
                                            行数
                                        </template>
                                    </a-input-number>
                                    <a-input-number v-model:value="formState.crop.split_cols" :min="1">
                                        <template #addonBefore>
                                            列数
                                        </template>
                                    </a-input-number>
                                </a-space>
                            </a-form-item>
                            <a-form-item :label="index === 0 ? '水平分割线' : ' '" :colon="index === 0 ? true : false"
                                v-if="formState.crop.op == 'split' && formState.crop.split_type == 'custom'"
                                v-for="(item, index) in formState.crop.split_h_breakpoints" :key="index">
                                <a-input-number :min="0" :max="100" :formatter="(value: any) => `${value}%`"
                                    :parser="(value: any) => value.replace('%', '')" />
                                <MinusCircleOutlined @click="removeHBreakpoint(item)" style="margin-left: 1vw;" />
                            </a-form-item>
                            <a-form-item name="span"
                                :label="formState.crop.split_h_breakpoints.length === 0 ? '水平分割线' : ' '"
                                :colon="formState.crop.split_h_breakpoints.length === 0 ? true : false"
                                v-if="formState.crop.op == 'split' && formState.crop.split_type == 'custom'">
                                <a-button type="dashed" block @click="addHBreakpoint">
                                    <PlusOutlined />
                                    添加水平分割线
                                </a-button>
                            </a-form-item>
                            <a-form-item :label="index === 0 ? '垂直分割线' : ' '" :colon="index === 0 ? true : false"
                                v-if="formState.crop.op == 'split' && formState.crop.split_type == 'custom'"
                                v-for="(item, index) in formState.crop.split_v_breakpoints" :key="index">
                                <a-input-number :min="0" :max="100" :formatter="(value: any) => `${value}%`"
                                    :parser="(value: any) => value.replace('%', '')" />
                                <MinusCircleOutlined @click="removeVBreakpoint(item)" style="margin-left: 1vw;" />
                            </a-form-item>
                            <a-form-item name="span"
                                :label="formState.crop.split_v_breakpoints.length === 0 ? '垂直分割线' : ' '"
                                :colon="formState.crop.split_v_breakpoints.length === 0 ? true : false"
                                v-if="formState.crop.op == 'split' && formState.crop.split_type == 'custom'">
                                <a-button type="dashed" block @click="addVBreakpoint">
                                    <PlusOutlined />
                                    添加垂直分割线
                                </a-button>
                            </a-form-item>
                            <a-form-item name="page" label="页码范围">
                                <a-input v-model:value="formState.page" placeholder="应用的页码范围(留空表示全部), e.g. 1-10"
                                    allow-clear />
                            </a-form-item>
                            <a-form-item name="input" label="输入" has-feedback :validateStatus="validateStatus.input">
                                <a-input v-model:value="formState.input" placeholder="输入文件路径" allow-clear />
                            </a-form-item>
                        </div>

                        <!-- PDF提取 -->
                        <div v-if="currentMenu.at(0) == 'extract'">
                            <a-form-item name="extract_op" label="提取类型">
                                <a-radio-group button-style="solid" v-model:value="formState.extract.op">
                                    <a-radio-button value="page">页面</a-radio-button>
                                    <a-radio-button value="text">文本</a-radio-button>
                                    <a-radio-button value="image">图片</a-radio-button>
                                    <a-radio-button value="table">表格</a-radio-button>
                                </a-radio-group>
                            </a-form-item>
                            <a-form-item name="page" label="页码范围">
                                <a-input v-model:value="formState.page" placeholder="应用的页码范围(留空表示全部), e.g. 1-10"
                                    allow-clear />
                            </a-form-item>
                            <a-form-item name="input" label="输入" has-feedback :validateStatus="validateStatus.input">
                                <a-input v-model:value="formState.input" placeholder="输入文件路径" allow-clear />
                            </a-form-item>
                        </div>
                        <!-- PDF缩放 -->
                        <div v-if="currentMenu.at(0) == 'scale'">
                            <a-form-item name="scale_conf" label="缩放参数">
                                <a-input v-model:value="formState.scale.scale_conf" placeholder="缩放参数" allow-clear />
                            </a-form-item>
                            <a-form-item name="page" label="页码范围">
                                <a-input v-model:value="formState.page" placeholder="应用的页码范围(留空表示全部), e.g. 1-10"
                                    allow-clear />
                            </a-form-item>
                            <a-form-item name="input" label="输入" has-feedback :validateStatus="validateStatus.input">
                                <a-input v-model:value="formState.input" placeholder="输入文件路径" allow-clear />
                            </a-form-item>
                        </div>
                        <!-- PDF转换 -->
                        <div v-if="currentMenu.at(0) == 'convert'">
                            <a-form-item name="convert_type" label="转换类型">
                                <a-select v-model:value="formState.convert.type" style="width: 200px">
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
                            <a-form-item name="page" label="页码范围" v-if="formState.convert.type.startsWith('pdf')">
                                <a-input v-model:value="formState.page" placeholder="应用的页码范围(留空表示全部), e.g. 1-3,9-10"
                                    allow-clear />
                            </a-form-item>
                            <a-form-item name="input" label="输入" has-feedback :validateStatus="validateStatus.input">
                                <a-input v-model:value="formState.input" placeholder="输入文件路径" allow-clear />
                            </a-form-item>
                        </div>
                        <!-- PDF加解密 -->
                        <div v-if="currentMenu.at(0) == 'encrypt'">
                            <a-form-item name="encrypt_op" label="操作" style="margin-bottom: 1.8vh;">
                                <a-radio-group button-style="solid" v-model:value="formState.encrypt.op">
                                    <a-radio-button value="encrypt">加密</a-radio-button>
                                    <a-radio-button value="decrypt">解密</a-radio-button>
                                </a-radio-group>
                            </a-form-item>
                            <div style="border: 1px solid #dddddd;border-radius: 10px;margin: 0 1vw;"
                                v-if="formState.encrypt.op == 'encrypt'">
                                <a-form-item name="encrypt.is_set_upw" label="设置打开密码"
                                    :disabled="!formState.encrypt.is_set_upw">
                                    <a-checkbox v-model:checked="formState.encrypt.is_set_upw"></a-checkbox>
                                </a-form-item>
                                <a-form-item name="encrypt_upw" label="设置密码" has-feedback
                                    :validateStatus="validateStatus.encrypt_upw">
                                    <a-input-password v-model:value="formState.encrypt.upw" placeholder="不少于6位"
                                        :disabled="!formState.encrypt.is_set_upw" />
                                </a-form-item>
                                <a-form-item name="encrypt_upw_confirm" label="确认密码" has-feedback
                                    :validateStatus="validateStatus.encrypt_upw_confirm">
                                    <a-input-password v-model:value="formState.encrypt.upw_confirm" placeholder="再次输入密码"
                                        :disabled="!formState.encrypt.is_set_upw" />
                                </a-form-item>
                            </div>

                            <div style="border: 1px solid #dddddd;border-radius: 10px;margin: 1vw 1vw;"
                                v-if="formState.encrypt.op == 'encrypt'">
                                <a-form-item name="encrypt.is_set_opw" label="设置权限密码">
                                    <a-checkbox v-model:checked="formState.encrypt.is_set_opw"></a-checkbox>
                                </a-form-item>
                                <a-form-item name="encrypt_opw" label="设置密码" has-feedback
                                    :validateStatus="validateStatus.encrypt_opw">
                                    <a-input-password v-model:value="formState.encrypt.opw" placeholder="不少于6位"
                                        :disabled="!formState.encrypt.is_set_opw" />
                                </a-form-item>
                                <a-form-item name="encrypt_opw_confirm" label="确认密码" has-feedback
                                    :validateStatus="validateStatus.encrypt_opw_confirm">
                                    <a-input-password v-model:value="formState.encrypt.opw_confirm" placeholder="再次输入密码"
                                        :disabled="!formState.encrypt.is_set_opw" />
                                </a-form-item>
                                <a-form-item name="encrypt.perm" label="限制功能"
                                    :rules="[{ required: formState.encrypt.is_set_opw }]">
                                    <a-checkbox v-model:checked="checkAll" :indeterminate="indeterminate"
                                        :disabled="!formState.encrypt.is_set_opw" @change="onCheckAllChange">全选</a-checkbox>
                                    <a-divider type="vertical" />
                                    <a-checkbox-group v-model:value="formState.encrypt.perm" :options="encrypt_perm_options"
                                        :disabled="!formState.encrypt.is_set_opw" />
                                </a-form-item>
                            </div>
                            <a-form-item name="encrypt.upw" label="密码" v-if="formState.encrypt.op == 'decrypt'"
                                :rules="[{ required: true }]">
                                <a-input-password v-model:value="formState.encrypt.upw" placeholder="解密密码" />
                            </a-form-item>
                            <a-form-item name="input" label="输入" has-feedback :validateStatus="validateStatus.input">
                                <a-input v-model:value="formState.input" placeholder="输入文件路径" allow-clear />
                            </a-form-item>
                        </div>

                        <!-- PDF水印 -->
                        <div v-if="currentMenu.at(0) == 'watermark'">
                            <a-form-item name="watermark_op" label="操作">
                                <a-radio-group button-style="solid" v-model:value="formState.watermark.op">
                                    <a-radio-button value="add">添加水印</a-radio-button>
                                    <a-radio-button value="remove">去除水印</a-radio-button>
                                </a-radio-group>
                            </a-form-item>
                            <div v-if="formState.watermark.op === 'add'">
                                <a-form-item name="watermark_type" label="水印类型">
                                    <a-radio-group v-model:value="formState.watermark.type">
                                        <a-radio value="text">文本</a-radio>
                                        <a-radio value="image" disabled>图片</a-radio>
                                    </a-radio-group>
                                </a-form-item>
                                <a-form-item name="watermark_text" label="水印文本">
                                    <a-input v-model:value="formState.watermark.text" placeholder="e.g. 这是水印" allow-clear />
                                </a-form-item>
                                <a-form-item name="watermark_font_size" label="字体属性">
                                    <a-space size="large">
                                        <a-select v-model:value="formState.watermark.font_family" style="width: 200px">
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
                                            <a-input-number v-model:value="formState.watermark.font_size" :min="1">
                                                <template #prefix>
                                                    <font-size-outlined />
                                                </template>
                                            </a-input-number>
                                        </a-tooltip>
                                        <a-tooltip>
                                            <template #title>字体颜色</template>
                                            <a-input v-model:value="formState.watermark.font_color" placeholder="字体颜色"
                                                :defaultValue="formState.watermark.font_color" allow-clear>
                                                <template #prefix>
                                                    <font-colors-outlined />
                                                </template>
                                            </a-input>
                                        </a-tooltip>
                                    </a-space>
                                </a-form-item>
                                <a-form-item name="watermark_font_opacity" label="水印属性">
                                    <a-space size="large">
                                        <a-input-number v-model:value="formState.watermark.font_opacity" :min="0" :max="1"
                                            :step="0.01">
                                            <template #addonBefore>
                                                不透明度
                                            </template>
                                        </a-input-number>
                                        <a-input-number v-model:value="formState.watermark.rotate" :min="0" :max="360">
                                            <template #addonBefore>
                                                旋转角度
                                            </template>
                                        </a-input-number>
                                        <a-input-number v-model:value="formState.watermark.space" :min="0" :max="360">
                                            <template #addonBefore>
                                                文字间距
                                            </template>
                                        </a-input-number>
                                        <a-input-number v-model:value="formState.watermark.quaility" :min="0" :max="360">
                                            <template #addonBefore>
                                                图片质量
                                            </template>
                                        </a-input-number>
                                    </a-space>
                                </a-form-item>
                            </div>
                            <a-form-item name="page" label="页码范围">
                                <a-input v-model:value="formState.page" placeholder="应用的页码范围(留空表示全部), e.g. 1-10"
                                    allow-clear />
                            </a-form-item>
                            <a-form-item name="input" label="输入" has-feedback :validateStatus="validateStatus.input">
                                <a-input v-model:value="formState.input" placeholder="输入文件路径" allow-clear />
                            </a-form-item>
                        </div>

                        <!-- OCR识别 -->
                        <div v-if="currentMenu.at(0) == 'ocr'">
                            <a-form-item label="语言">
                                <a-select v-model:value="formState.ocr.lang" style="width: 200px">
                                    <a-select-option value="ch">中文简体</a-select-option>
                                    <a-select-option value="en">英文</a-select-option>
                                </a-select>
                            </a-form-item>
                            <a-form-item label="是否双栏">
                                <a-checkbox v-model:checked="formState.ocr.double_column"></a-checkbox>
                            </a-form-item>
                            <a-form-item name="page" label="页码范围">
                                <a-input v-model:value="formState.page" placeholder="应用的页码范围(留空表示全部), e.g. 1-10"
                                    allow-clear />
                            </a-form-item>
                            <a-form-item name="input" label="输入" has-feedback :validateStatus="validateStatus.input">
                                <a-input v-model:value="formState.input" placeholder="输入文件路径" allow-clear />
                            </a-form-item>
                        </div>
                        <!-- 通用 -->
                        <div v-if="currentMenu.at(0) != 'settings'">
                            <a-form-item name="output" label="输出">
                                <a-input v-model:value="formState.output" placeholder="输出目录" allow-clear />
                            </a-form-item>
                            <a-form-item :wrapperCol="{ offset: 4 }" style="margin-bottom: 10px;">
                                <a-button type="primary" html-type="submit" @click="onSubmit"
                                    :loading="confirmLoading">确认</a-button>
                                <a-button style="margin-left: 10px" @click="resetFields">重置</a-button>
                            </a-form-item>
                        </div>
                        <div v-else>
                            <a-form-item label="ocr路径">
                                <a-input v-model:value="formState.output" placeholder="填写ocr路径" disabled
                                    allow-clear></a-input>
                            </a-form-item>
                            <a-form-item label="pandoc路径">
                                <a-input v-model:value="formState.output" placeholder="填写ocr路径" disabled
                                    allow-clear></a-input>
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
    SplitCellsOutlined,
    LoginOutlined
} from '@ant-design/icons-vue';
import { message, Modal } from 'ant-design-vue';
import {
    CheckFileExists,
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
import type { FormState } from "./data";

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
        SplitCellsOutlined,
        LoginOutlined
    },
    setup() {
        const formRef = ref<FormInstance>();
        const encrypt_perm_options = [
            "复制", "注释", "打印", "表单", "插入/删除页面"
        ];
        const confirmLoading = ref<boolean>(false);
        const indeterminate = ref<boolean>(false);
        const checkAll = ref<boolean>(false);

        const formState = reactive<FormState>({
            // 合并
            merge: {
                path_list: [],
                sort: "hand",
                sort_direction: "asc",
            },
            // 拆分
            split: {
                op: "span",
                span: 5,
                ranges: "",
                bookmark_level: "1",
            },
            // 插入/替换
            insert: {
                op: "insert",
                src_pos: 1,
                src_path: "",
                dst_path: "",
                src_range: "",
                dst_range: ""
            },
            // 裁剪/分割
            crop: {
                op: "crop",
                unit: "cm",
                up: 0,
                left: 0,
                down: 0,
                right: 0,
                split_h_breakpoints: [],
                split_v_breakpoints: [],
                split_type: "even",
                split_rows: 1,
                split_cols: 1
            },
            // 提取
            extract: {
                op: "page",
            },
            // 加密
            encrypt: {
                op: "encrypt",
                upw: "",
                opw: "",
                perm: ["打开"],
                is_set_upw: false,
                is_set_opw: false,
                upw_confirm: "",
                opw_confirm: "",
            },
            // 转换
            convert: {
                type: "pdf2png",
            },
            // 水印
            watermark: {
                op: "add",
                type: "text",
                text: "",
                font_family: "msyh.ttc",
                font_size: 14,
                font_color: "#808080",
                font_opacity: 0.15,
                quaility: 80,
                rotate: 30,
                space: 75,
            },
            // 缩放
            scale: {
                scale_conf: "",
            },
            // 旋转
            rotate: {
                op: "rotate",
                degree: 90,
                flip_method: "horizontal",
            },
            // 书签
            bookmark: {
                op: "extract",
                file: "",
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
            },
            // ocr
            ocr: {
                lang: "ch",
                double_column: false,
            },
            // 通用
            page: "",
            input: "",
            output: ""
        });

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
            try {
                const values = await formRef.value?.validate();
                console.log('Success:', values);
                confirmLoading.value = true;
                switch (currentMenu.value.at(0)) {
                    case "split": {
                        await handleOps(SplitPDF, [formState.input, formState.split.op, formState.split.span, formState.output]);
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
                    case "insert": {
                        switch (formState.insert.op) {
                            case "insert": {
                                console.log("aaaaaaaaaaa");
                                console.log(formState.insert.src_path);
                                await handleOps(CheckFileExists, [formState.insert.src_path]);
                                confirmLoading.value = false;
                                break;
                            }
                            case "replace": {
                                break;
                            }
                        }
                        break;
                    }
                    case "bookmark": {
                        switch (formState.bookmark.op) {
                            case "extract": {
                                await handleOps(ExtractBookmark, [formState.input, formState.output, formState.bookmark.extract_format]);
                                break;
                            }
                            case "write": {
                                switch (formState.bookmark.write_type) {
                                    case "file": {
                                        await handleOps(WriteBookmarkByFile, [formState.input, formState.output, formState.bookmark.file, formState.bookmark.write_offset]);
                                        break;
                                    }
                                    case "page": {
                                        await handleOps(WriteBookmarkByGap, [formState.input, formState.output, formState.bookmark.write_gap, formState.bookmark.write_format]);
                                        break;
                                    }
                                }
                                break;
                            }
                            case "transform": {
                                await handleOps(TransformBookmark, [formState.input, formState.output, formState.bookmark.transform_indent, formState.bookmark.transform_offset, formState.bookmark.transform_dots]);
                                break;
                            }
                        }
                        break;
                    }
                    case "watermark": {
                        await handleOps(WatermarkPDF, [formState.input, formState.output, formState.watermark.text, formState.watermark.font_family, formState.watermark.font_size, formState.watermark.font_color, formState.watermark.rotate, formState.watermark.space, formState.watermark.font_opacity, formState.watermark.quaility]);
                        break;
                    }
                    case "rotate": {
                        await handleOps(RotatePDF, [formState.input, formState.output, formState.rotate.degree, formState.page]);
                        break;
                    }
                    case "crop": {
                        break;
                    }
                    case "delete": {
                        let pageStr = formState.page.split(",").map(item => {
                            if (item.startsWith("!")) {
                                return item.slice(1).trim();
                            }
                            else {
                                return "!" + item.trim();
                            }
                        }).join(",");
                        console.log({ pageStr });
                        await handleOps(ReorderPDF, [formState.input, formState.output, pageStr]);
                        break;
                    }
                    case "extract": {
                        switch (formState.extract.op) {
                            case "page": {
                                await handleOps(ReorderPDF, [formState.input, formState.output, formState.page]);
                                break;
                            }
                            case "text": {
                                break;
                            }
                            case "image": {
                                break;
                            }
                            case "table": {
                                break;
                            }
                        }
                        break;
                    }
                    case "compress": {
                        await handleOps(CompressPDF, [formState.input, formState.output]);
                        break;
                    }
                    case "convert": {
                        await handleOps(ConvertPDF, [formState.input, formState.output, formState.convert.type, formState.page]);
                        break;
                    }
                    case "scale": {
                        await handleOps(ScalePDF, [formState.input, formState.output, formState.scale.scale_conf, formState.page]);
                        break;
                    }
                    case "encrypt": {
                        switch (formState.encrypt.op) {
                            case "encrypt": {
                                let upw = "", opw = "", perm: string[] = [];
                                if (formState.encrypt.is_set_upw) { upw = formState.encrypt.upw; }
                                if (formState.encrypt.is_set_opw) {
                                    opw = formState.encrypt.opw;
                                    perm = formState.encrypt.perm;
                                }
                                await handleOps(EncryptPDF, [formState.input, formState.output, upw, opw, perm]);
                                break;
                            }
                            case "decrypt": {
                                await handleOps(DecryptPDF, [formState.input, formState.output, formState.encrypt.upw]);
                                break;
                            }
                        }
                        break;
                    }
                    case "ocr": {
                        await handleOps(OCR, [formState.input, formState.output, formState.page, formState.ocr.lang, formState.ocr.double_column]);
                        break;
                    }
                }
                confirmLoading.value = false;
            } catch (error) {
                console.log('validate failed:', error);
                return;
            }

        }
        // 表单验证
        const validateStatus = reactive({
            input: '',
            merge_input: '',
            insert_src_path: '',
            insert_dst_path: '',
            encrypt_upw: '',
            encrypt_upw_confirm: '',
            encrypt_opw: '',
            encrypt_opw_confirm: '',
        });
        let validateFileExists = async (_rule: Rule, value: string) => {
            // @ts-ignore
            validateStatus[_rule.fullField] = 'validating';
            if (value === '') {
                validateStatus.input = 'error';
                return Promise.reject('请填写路径');
            }
            await CheckFileExists(value).then((res: any) => {
                console.log({ res });
                if (res) {
                    // @ts-ignore
                    validateStatus[_rule.fullField] = 'error';
                    return Promise.reject(res);
                }
                // @ts-ignore
                validateStatus[_rule.fullField] = 'success';
                return Promise.resolve();
            }).catch((err: any) => {
                console.log({ err });
                // @ts-ignore
                validateStatus[_rule.fullField] = 'error';
                return Promise.reject("文件不存在--");
            });
        };
        let validatePass = async (_rule: Rule, value: string) => {
            // @ts-ignore
            validateStatus[_rule.fullField] = 'validating';
            if (value === '') {
                // @ts-ignore
                validateStatus[_rule.fullField] = 'error';
                return Promise.reject('请输入密码');
            } else {
                if (value.length < 6) {
                    // @ts-ignore
                    validateStatus[_rule.fullField] = 'error';
                    return Promise.reject('密码长度不能少于6位');
                }
                // @ts-ignore
                validateStatus[_rule.fullField] = 'success';
                return Promise.resolve();
            }
        };

        let validatePassUpwConfirm = async (_rule: Rule, value: string) => {
            validateStatus.encrypt_upw_confirm = 'validating';
            if (value === '') {
                validateStatus.encrypt_upw_confirm = 'error';
                return Promise.reject('请再次输入密码');
            } else if (value !== formState.encrypt.upw) {
                validateStatus.encrypt_upw_confirm = 'error';
                return Promise.reject("两次密码输入不一致");
            } else {
                validateStatus.encrypt_upw_confirm = 'success';
                return Promise.resolve();
            }
        };
        let validatePassOpwConfirm = async (_rule: Rule, value: string) => {
            validateStatus.encrypt_opw_confirm = 'validating';
            if (value === '') {
                validateStatus.encrypt_opw_confirm = 'error';
                return Promise.reject('请再次输入密码');
            } else if (value !== formState.encrypt.opw) {
                validateStatus.encrypt_opw_confirm = 'error';
                return Promise.reject("两次密码输入不一致");
            } else {
                validateStatus.encrypt_opw_confirm = 'success';
                return Promise.resolve();
            }
        };

        const rules: Record<string, Rule[]> = {
            input: [{ required: true, validator: validateFileExists, trigger: 'change' }],
            // merge_input: [{ validator: validateFileExists, trigger: 'change' }],
            insert_src_path: [{ required: true, validator: validateFileExists, trigger: 'change' }],
            insert_dst_path: [{ required: true, validator: validateFileExists, trigger: 'change' }],
            encrypt_upw: [{ required: true, validator: validatePass, trigger: 'change' }],
            encrypt_upw_confirm: [{ required: true, validator: validatePassUpwConfirm, trigger: 'change' }],
            encrypt_opw: [{ required: true, validator: validatePass, trigger: 'change' }],
            encrypt_opw_confirm: [{ required: true, validator: validatePassOpwConfirm, trigger: 'change' }],
        };

        // 重置表单
        const resetFields = () => {
            formRef.value?.resetFields();
        }

        // 加密PDF
        const onCheckAllChange = (e: any) => {
            Object.assign(formState.encrypt, {
                perm: e.target.checked ? encrypt_perm_options : [],
            });
            indeterminate.value = false;
        };
        watch(
            () => formState.encrypt.perm,
            (val: any) => {
                indeterminate.value = !!val.length && val.length < encrypt_perm_options.length;
                checkAll.value = val.length === encrypt_perm_options.length;
            }
        )
        const currentMenu = ref<string[]>(['merge']);

        // 合并PDF
        const addPath = () => {
            formState.merge.path_list.push("");
        }
        const removePath = (item: string) => {
            const index = formState.merge.path_list.indexOf(item);
            if (index != -1) {
                formState.merge.path_list.splice(index, 1);
            }
        }
        // 分割PDF
        const addHBreakpoint = () => {
            formState.crop.split_h_breakpoints.push(0);
        }
        const removeHBreakpoint = (item: number) => {
            const index = formState.crop.split_h_breakpoints.indexOf(item);
            if (index != -1) {
                formState.crop.split_h_breakpoints.splice(index, 1);
            }
        }
        const addVBreakpoint = () => {
            formState.crop.split_v_breakpoints.push(0);
        }
        const removeVBreakpoint = (item: number) => {
            const index = formState.crop.split_v_breakpoints.indexOf(item);
            if (index != -1) {
                formState.crop.split_v_breakpoints.splice(index, 1);
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
            rules,
            validateStatus,
            onSubmit,
            onCheckAllChange,
            addPath,
            removePath,
            resetFields,
            addHBreakpoint,
            removeHBreakpoint,
            addVBreakpoint,
            removeVBreakpoint,
        };
    },
});
</script>