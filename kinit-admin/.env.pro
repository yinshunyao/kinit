# 环境
VITE_NODE_ENV=production

# 接口 baseURL（axios）。与网关/Nginx 同域反代时填 /api；跨域直连后端时填完整地址如 https://api.example.com
VITE_API_BASE_URL=/api

# 生产构建不使用 Vite 代理；以下两项仅 dev 使用，pro 可保留默认值或删除
VITE_DEV_PROXY_TARGET=http://127.0.0.1:46000
VITE_DEV_PROXY_MEDIA_PATH=/media

# 后端对外基址（Logo、上传资源等）。前后端不同域时填写后端根地址，无尾斜杠
# VITE_PUBLIC_BACKEND_URL=https://api.example.com

# 打包路径
VITE_BASE_PATH=/

# 是否删除debugger
VITE_DROP_DEBUGGER=true

# 是否删除console.log
VITE_DROP_CONSOLE=true

# 是否sourcemap
VITE_SOURCEMAP=false

# 输出路径
VITE_OUT_DIR=dist

# 标题
VITE_APP_TITLE=后台系统

# 是否切割css
VITE_USE_CSS_SPLIT=true

# 是否使用在线图标
VITE_USE_ONLINE_ICON=true

# 是否包分析
VITE_USE_BUNDLE_ANALYZER=true

# 是否全量引入element-plus样式
VITE_USE_ALL_ELEMENT_PLUS_STYLE=false
