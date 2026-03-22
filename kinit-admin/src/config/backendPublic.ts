/** 后端对外基址（媒体、静态资源等），空字符串表示与前端同源（由部署或 dev 代理转发） */
const raw = import.meta.env.VITE_PUBLIC_BACKEND_URL?.trim() ?? ''
export const backendPublicBase = raw.replace(/\/$/, '')

/** 拼接后端可访问的绝对或根相对 URL */
export function joinBackendPublic(path: string): string {
  const normalized = path.startsWith('/') ? path : `/${path}`
  return backendPublicBase ? `${backendPublicBase}${normalized}` : normalized
}
