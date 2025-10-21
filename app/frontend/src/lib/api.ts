import axios from 'axios'

export const api = axios.create({
  baseURL: '',
})

export function fileDownload(url: string) {
  const link = document.createElement('a')
  link.href = url
  link.target = '_blank'
  document.body.appendChild(link)
  link.click()
  link.remove()
}
