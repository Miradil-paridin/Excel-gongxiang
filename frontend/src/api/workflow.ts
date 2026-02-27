import request from '@/utils/request'

export function getTemplates() {
  return request({
    url: '/templates/',
    method: 'get'
  })
}

export function createTemplate(formData: FormData) {
  return request({
    url: '/templates/',
    method: 'post',
    data: formData,
    headers: {
      'Content-Type': 'multipart/form-data'
    }
  })
}

export function getTasks() {
  return request({
    url: '/tasks/',
    method: 'get'
  })
}

export function createTask(data: any) {
  return request({
    url: '/tasks/',
    method: 'post',
    data
  })
}

export function getTaskProgress(id: number) {
  return request({
    url: `/tasks/${id}/progress/`,
    method: 'get'
  })
}

export function getMyTaskAssignments(params?: any) {
  return request({
    url: '/submissions/my-tasks/',
    method: 'get',
    params
  })
}

export function createSubmission(data: any) {
  return request({
    url: '/submissions/',
    method: 'post',
    data
  })
}

export function submitSubmission(id: number) {
  return request({
    url: `/submissions/${id}/submit/`,
    method: 'post'
  })
}

export function withdrawSubmission(id: number) {
  return request({
    url: `/submissions/${id}/withdraw/`,
    method: 'post'
  })
}
