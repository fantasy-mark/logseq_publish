<template>
  <div class="file-list-page">
    <!-- 头部 -->
    <header class="page-header">
      <div class="header-content">
        <h1>📚 Logseq Publish</h1>
        <p class="subtitle">Markdown 文档管理与发布</p>
      </div>
      <div class="header-actions">
        <el-button type="success" @click="handleCreate">
          <el-icon><Plus /></el-icon>
          新建文档
        </el-button>
        <el-button type="warning" @click="showGitStatus">
          <el-icon><Upload /></el-icon>
          发布到 GitHub
        </el-button>
      </div>
    </header>

    <!-- 主内容 -->
    <main class="page-content">
      <!-- 搜索栏 -->
      <div class="search-bar">
        <el-input
          v-model="searchQuery"
          placeholder="搜索文件名..."
          :prefix-icon="Search"
          clearable
          style="width: 300px"
        />
        <el-tag v-if="gitStatus" :type="gitStatus.status === 'clean' ? 'success' : 'warning'">
          {{ gitStatus.status === 'clean' ? '✅ 工作区干净' : '⚠️ 有待提交的修改' }}
        </el-tag>
      </div>

      <!-- 文件列表 -->
      <el-table
        :data="filteredFiles"
        :loading="loading"
        stripe
        style="width: 100%"
        @row-dblclick="handleEdit"
      >
        <el-table-column prop="name" label="文件名" min-width="200">
          <template #default="{ row }">
            <el-link @click="handleEdit(row)" type="primary" :underline="false">
              📄 {{ row.name }}
            </el-link>
          </template>
        </el-table-column>
        
        <el-table-column prop="size" label="大小" width="100" />
        
        <el-table-column prop="mtime" label="修改时间" width="180" />
        
        <el-table-column label="操作" width="220" fixed="right">
          <template #default="{ row }">
            <el-button size="small" @click="handleEdit(row)">
              编辑
            </el-button>
            <el-button size="small" type="danger" @click="handleDelete(row)">
              删除
            </el-button>
          </template>
        </el-table-column>
      </el-table>

      <!-- 空状态 -->
      <el-empty v-if="!loading && files.length === 0" description="暂无文档">
        <el-button type="primary" @click="handleCreate">创建第一个文档</el-button>
      </el-empty>
    </main>

    <!-- Git 状态对话框 -->
    <el-dialog
      v-model="gitDialogVisible"
      title="📤 发布到 GitHub"
      width="500px"
    >
      <div v-if="gitStatus" class="git-status">
        <el-alert
          :title="gitStatus.status === 'clean' ? '工作区干净，无需提交' : '有待提交的修改'"
          :type="gitStatus.status === 'clean' ? 'success' : 'warning'"
          show-icon
          :closable="false"
        />
        
        <div v-if="gitStatus.changes && gitStatus.changes.length > 0" class="git-changes">
          <h4>变更文件：</h4>
          <ul>
            <li v-for="change in gitStatus.changes" :key="change">{{ change }}</li>
          </ul>
        </div>
      </div>

      <el-form :model="publishForm" label-width="80px" style="margin-top: 20px">
        <el-form-item label="提交信息">
          <el-input
            v-model="publishForm.message"
            placeholder="请输入提交信息，例如：更新投资笔记"
            :disabled="gitStatus?.status === 'clean'"
          />
        </el-form-item>
      </el-form>

      <template #footer>
        <el-button @click="gitDialogVisible = false">取消</el-button>
        <el-button
          type="primary"
          @click="handlePublish"
          :loading="publishing"
          :disabled="gitStatus?.status === 'clean' || !publishForm.message"
        >
          确认发布
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import type { FileItem, GitStatus } from '@/types'
import { fileApi, gitApi } from '@/services/api'
import { Search, Plus, Upload } from '@element-plus/icons-vue'

const router = useRouter()

// 响应式数据
const files = ref<FileItem[]>([])
const loading = ref(false)
const searchQuery = ref('')
const gitStatus = ref<GitStatus | null>(null)
const gitDialogVisible = ref(false)
const publishing = ref(false)
const publishForm = ref({
  message: ''
})

// 计算属性
const filteredFiles = computed(() => {
  if (!searchQuery.value) return files.value
  const query = searchQuery.value.toLowerCase()
  return files.value.filter(f => f.name.toLowerCase().includes(query))
})

// 方法
const fetchFiles = async () => {
  loading.value = true
  try {
    const res = await fileApi.getAll()
    if (res.success) {
      files.value = res.data
    }
  } catch (error) {
    ElMessage.error('获取文件列表失败')
  } finally {
    loading.value = false
  }
}

const fetchGitStatus = async () => {
  try {
    const res = await gitApi.getStatus()
    gitStatus.value = res
  } catch (error) {
    console.error('获取 Git 状态失败:', error)
  }
}

const handleCreate = () => {
  router.push('/create')
}

const handleEdit = (file: FileItem) => {
  router.push(`/edit/${encodeURIComponent(file.name)}`)
}

const handleDelete = async (file: FileItem) => {
  try {
    await ElMessageBox.confirm(
      `确定要删除文档 "${file.name}" 吗？此操作会同时删除本地和远程文件。`,
      '确认删除',
      { confirmButtonText: '删除', cancelButtonText: '取消', type: 'warning' }
    )

    await fileApi.delete(file.name)
    ElMessage.success('删除成功')
    await fetchFiles()
    await fetchGitStatus()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('删除失败')
    }
  }
}

const showGitStatus = async () => {
  await fetchGitStatus()
  publishForm.value.message = ''
  gitDialogVisible.value = true
}

const handlePublish = async () => {
  if (!publishForm.value.message) return

  publishing.value = true
  try {
    const res = await gitApi.publish(publishForm.value.message)
    if (res.success) {
      ElMessage.success('发布成功！已提交到 GitHub')
      gitDialogVisible.value = false
      await fetchGitStatus()
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
  fetchFiles()
  fetchGitStatus()
})
</script>

<style scoped>
.file-list-page {
  min-height: 100vh;
  padding: 20px;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 30px;
  padding: 20px;
  background: #16213e;
  border-radius: 10px;
  border-bottom: 2px solid #e94560;
}

.header-content h1 {
  color: #e94560;
  font-size: 1.8rem;
  margin-bottom: 5px;
}

.subtitle {
  color: #aaa;
  font-size: 0.9rem;
}

.header-actions {
  display: flex;
  gap: 10px;
}

.page-content {
  background: #0f3460;
  border-radius: 10px;
  padding: 20px;
}

.search-bar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  gap: 15px;
}

.git-status {
  margin-bottom: 15px;
}

.git-changes {
  margin-top: 15px;
  padding: 10px;
  background: #1a1a2e;
  border-radius: 5px;
}

.git-changes h4 {
  margin-bottom: 10px;
  color: #e94560;
}

.git-changes ul {
  list-style: none;
  padding-left: 0;
}

.git-changes li {
  padding: 5px 0;
  color: #aaa;
  font-family: monospace;
}
</style>
