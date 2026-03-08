export interface FileItem {
  name: string
  path: string
  size: string
  mtime: string
  mtime_ts: number
}

export interface FileContent {
  name: string
  content: string
  html: string
}

export interface GitStatus {
  status: 'clean' | 'modified' | 'error'
  message?: string
  changes?: string[]
}

export interface ApiResponse<T = any> {
  success: boolean
  data?: T
  error?: string
  message?: string
}
