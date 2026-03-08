import axios from 'axios'

const api = axios.create({
  baseURL: '/api',
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json'
  }
})

export const fileApi = {
  // 获取文件列表
  getAll: () => api.get('/files').then(res => res.data),
  
  // 获取单个文件
  get: (filename: string) => api.get(`/file/${encodeURIComponent(filename)}`).then(res => res.data),
  
  // 创建文件
  create: (filename: string, content: string) => 
    api.post(`/file/${encodeURIComponent(filename)}`, { content }).then(res => res.data),
  
  // 更新文件
  update: (filename: string, content: string) => 
    api.put(`/file/${encodeURIComponent(filename)}`, { content }).then(res => res.data),
  
  // 删除文件
  delete: (filename: string) => 
    api.delete(`/file/${encodeURIComponent(filename)}`).then(res => res.data)
}

export const gitApi = {
  // 获取 Git 状态
  getStatus: () => api.get('/git/status').then(res => res.data),
  
  // 提交并发布
  publish: (message: string, files?: string[]) => 
    api.post('/git/publish', { message, files }).then(res => res.data),
  
  // 获取 diff
  getDiff: () => api.get('/git/diff').then(res => res.data)
}

export default api
