<template>
  <div class="file-edit-page">
    <!-- 头部 -->
    <header class="page-header">
      <div class="header-content">
        <el-button @click="handleBack" :icon="ArrowLeft">返回</el-button>
        <h1>{{ isNew ? '📝 新建文档' : '✏️ 编辑文档' }}</h1>
        <span v-if="filename" class="filename-tag">{{ filename }}</span>
      </div>
      <div class="header-actions">
        <el-button @click="togglePreview" :icon="View">
          {{ showPreview ? '编辑' : '预览' }}
        </el-button>
        <el-button type="primary" @click="handleSave" :loading="saving" :icon="Check">
          保存
        </el-button>
        <el-button type="warning" @click="handlePublish" :loading="publishing" :icon="Upload">
          保存并发布
        </el-button>
      </div>
    </header>

    <!-- 主内容 -->
    <main class="page-content">
      <div class="editor-container" :class="{ 'split-view': showPreview }">
        <!-- 编辑器 -->
        <div class="editor-panel">
          <el-input
            v-if="isNew"
            v-model="newFilename"
            placeholder="输入文件名（不含 .md 后缀）"
            class="filename-input"
            :prefix-icon="Document"
          />
          
          <el-input
            v-model="content"
            type="textarea"
            :rows="30"
            placeholder="开始编写 Markdown 内容..."
            class="editor-textarea"
          />
        </div>

        <!-- 预览 -->
        <div v-if="showPreview" class="preview-panel">
          <div class="markdown-preview" v-html="previewHtml"></div>
        </div>
      </div>
    </main>

    <!-- 发布对话框 -->
    <el-dialog
      v-model="publishDialogVisible"
      title="📤 发布到 GitHub"
      width="500px"
    >
      <el-form :model="publishForm" label-width="80px">
        <el-form-item label="提交信息">
          <el-input
            v-model="publishForm.message"
            placeholder="请输入提交信息，例如：更新投资笔记"
          />
        </el-form-item>
      </el-form>

      <template #footer>
        <el-button @click="publishDialogVisible = false">取消</el-button>
        <el-button
          type="primary"
          @click="confirmPublish"
          :loading="publishing"
          :disabled="!publishForm.message"
        >
          确认发布
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { ElMessage } from 'element-plus'
import { fileApi, gitApi } from '@/services/api'
import MarkdownIt from 'markdown-it'
import {
  ArrowLeft,
  View,
  Check,
  Upload,
  Document
} from '@element-plus/icons-vue'

const router = useRouter()
const route = useRoute()

const md = new MarkdownIt({
  html: true,
  linkify: true,
  typographer: true
})

// 响应式数据
const isNew = ref(false)
const filename = ref('')
const newFilename = ref('')
const content = ref('')
const saving = ref(false)
const publishing = ref(false)
const showPreview = ref(false)
const publishDialogVisible = ref(false)
const publishForm = ref({ message: '' })
const previewHtml = ref('')

// 计算预览 HTML
watch(content, (newContent) => {
  previewHtml.value = md.render(newContent || '')
}, { immediate: true })

// 方法
const loadFile = async () => {
  const fname = route.params.filename as string
  
  if (!fname) {
    isNew.value = true
    return
  }
  
  try {
    const res = await fileApi.get(fname)
    if (res.success) {
      filename.value = fname
      content.value = res.data.content
      isNew.value = false
    }
  } catch (error) {
    ElMessage.error('加载文件失败')
  }
}

const handleBack = () => {
  router.push('/')
}

const togglePreview = () => {
  showPreview.value = !showPreview.value
}

const handleSave = async () => {
  if (!content.value.trim()) {
    ElMessage.warning('内容不能为空')
    return
  }
  
  if (isNew.value && !newFilename.value.trim()) {
    ElMessage.warning('请输入文件名')
    return
  }
  
  saving.value = true
  try {
    const fname = isNew.value ? `${newFilename.value.trim()}.md` : filename.value
    
    if (isNew.value) {
      await fileApi.create(fname, content.value)
      ElMessage.success('创建成功')
      isNew.value = false
      filename.value = fname
      router.push(`/edit/${encodeURIComponent(fname)}`)
    } else {
      await fileApi.update(fname, content.value)
      ElMessage.success('保存成功')
    }
  } catch (error: any) {
    ElMessage.error(`保存失败：${error.response?.data?.error || error.message}`)
  } finally {
    saving.value = false
  }
}

const handlePublish = async () => {
  if (!content.value.trim()) {
    ElMessage.warning('内容不能为空')
    return
  }
  
  if (isNew.value && !newFilename.value.trim()) {
    ElMessage.warning('请输入文件名')
    return
  }
  
  // 先保存
  await handleSave()
  
  // 打开发布对话框
  publishForm.value.message = isNew.value 
    ? `新建文档：${newFilename.value}`
    : `更新文档：${filename.value}`
  publishDialogVisible.value = true
}

const confirmPublish = async () => {
  if (!publishForm.value.message) return
  
  publishing.value = true
  try {
    const res = await gitApi.publish(publishForm.value.message)
    if (res.success) {
      ElMessage.success('发布成功！已提交到 GitHub')
      publishDialogVisible.value = false
    } else {
      ElMessage.error(`发布失败：${res.message}`)
    }
  } catch (error: any) {
    ElMessage.error(`发布失败：${error.response?.data?.message || error.message}`)
  } finally {
    publishing.value = false
  }
}

// 生命周期
onMounted(() => {
  loadFile()
})
</script>

<style scoped>
.file-edit-page {
  min-height: 100vh;
  padding: 20px;
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px;
  background: #16213e;
  border-radius: 10px;
  border-bottom: 2px solid #e94560;
}

.header-content {
  display: flex;
  align-items: center;
  gap: 15px;
}

.header-content h1 {
  color: #e94560;
  font-size: 1.5rem;
  margin: 0;
}

.filename-tag {
  background: #0f3460;
  padding: 5px 15px;
  border-radius: 5px;
  font-family: monospace;
  color: #4ecca3;
}

.header-actions {
  display: flex;
  gap: 10px;
}

.page-content {
  flex: 1;
  background: #0f3460;
  border-radius: 10px;
  padding: 20px;
  overflow: hidden;
}

.editor-container {
  height: calc(100vh - 250px);
  display: flex;
  gap: 20px;
}

.editor-container.split-view {
  grid-template-columns: 1fr 1fr;
}

.editor-panel {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 15px;
  height: 100%;
}

.filename-input {
  width: 400px;
}

.filename-input :deep(.el-input__wrapper) {
  background: #1a1a2e;
  border-color: #2a2a4a;
}

.editor-textarea {
  flex: 1;
}

.editor-textarea :deep(.el-textarea__inner) {
  background: #1a1a2e;
  border: 1px solid #2a2a4a;
  color: #eee;
  font-family: 'Fira Code', Consolas, monospace;
  font-size: 14px;
  line-height: 1.6;
  resize: none;
}

.preview-panel {
  flex: 1;
  background: #1a1a2e;
  border-radius: 8px;
  padding: 20px;
  overflow-y: auto;
  border: 1px solid #2a2a4a;
}

.markdown-preview {
  line-height: 1.8;
}

.markdown-preview :deep(h1),
.markdown-preview :deep(h2),
.markdown-preview :deep(h3) {
  color: #e94560;
  margin-top: 1.5em;
  margin-bottom: 0.8em;
}

.markdown-preview :deep(h1) {
  border-bottom: 2px solid #e94560;
  padding-bottom: 10px;
}

.markdown-preview :deep(h2) {
  border-bottom: 1px solid #2a2a4a;
  padding-bottom: 8px;
}

.markdown-preview :deep(p) {
  margin-bottom: 1em;
}

.markdown-preview :deep(code) {
  background: #16213e;
  padding: 2px 6px;
  border-radius: 4px;
  font-family: 'Fira Code', Consolas, monospace;
  font-size: 0.9em;
  color: #4ecca3;
}

.markdown-preview :deep(pre) {
  background: #16213e;
  padding: 20px;
  border-radius: 8px;
  overflow-x: auto;
  margin: 1em 0;
  border: 1px solid #2a2a4a;
}

.markdown-preview :deep(pre code) {
  background: none;
  padding: 0;
  color: #eee;
}

.markdown-preview :deep(a) {
  color: #4ecca3;
}

.markdown-preview :deep(blockquote) {
  border-left: 4px solid #e94560;
  padding-left: 20px;
  margin: 1em 0;
  color: #aaa;
  background: #16213e;
  padding: 15px 20px;
  border-radius: 0 8px 8px 0;
}

.markdown-preview :deep(ul),
.markdown-preview :deep(ol) {
  margin-left: 2em;
  margin-bottom: 1em;
}

.markdown-preview :deep(img) {
  max-width: 100%;
  border-radius: 8px;
}
</style>
