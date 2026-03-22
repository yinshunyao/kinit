/// <reference types="vite/client" />

declare module '*.vue' {
  import { DefineComponent } from 'vue'
  // eslint-disable-next-line @typescript-eslint/no-explicit-any, @typescript-eslint/ban-types
  const component: DefineComponent<{}, {}, any>
  export default component
}

interface ImportMetaEnv {
  readonly VITE_NODE_ENV: string
  readonly VITE_APP_TITLE: string
  /** axios 请求的 API 根路径或完整 URL */
  readonly VITE_API_BASE_URL: string
  /** 开发时 Vite 将接口代理到该后端地址（仅 vite.config 读取） */
  readonly VITE_DEV_PROXY_TARGET: string
  /** 开发时媒体资源代理路径前缀（仅 vite.config 读取） */
  readonly VITE_DEV_PROXY_MEDIA_PATH: string
  /** 浏览器直接访问的后端基址（媒体/静态），空为同源根相对 */
  readonly VITE_PUBLIC_BACKEND_URL?: string
  readonly VITE_BASE_PATH: string
  readonly VITE_DROP_DEBUGGER: string
  readonly VITE_DROP_CONSOLE: string
  readonly VITE_SOURCEMAP: string
  readonly VITE_OUT_DIR: string
  readonly VITE_USE_BUNDLE_ANALYZER: string
  readonly VITE_USE_ALL_ELEMENT_PLUS_STYLE: string
  readonly VITE_USE_MOCK: string
  readonly VITE_USE_CSS_SPLIT: string
  readonly VITE_USE_ONLINE_ICON: string
}

declare global {
  interface ImportMeta {
    readonly env: ImportMetaEnv
  }
}
