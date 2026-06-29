/// <reference types="vite/client" />

interface ImportMetaEnv {
  readonly VITE_HB_PROXY_PREFIX: string
  readonly VITE_HB_API_TARGET: string
  readonly VITE_HB_API_USER: string
  readonly VITE_HB_API_PASSWORD: string
  readonly VITE_PP_API_TARGET: string
}

interface ImportMeta {
  readonly env: ImportMetaEnv
}
