# 确保node版本
```shell
nvm use 22
```

# capacitor初始化
```shell
# 初始化项目
npx cap init

# ios
npm install @capacitor/ios
npx cap add ios
```

# 前端编译
```shell
# 打包到 kinit/kinit-admin/dist-pro
pnpm run build:pro

# 开发者模式运行
pnpm run dev
```

# capacitor 同步和编译
```shell
# 确保编译名称为为dist，可以手工修改
mv -f dist-pro  dist
npx cap sync ios

# 推荐动态监听
# npx cap run ios -l --external

# xcode打开
npx cap open ios
```

# ios 无 App.xcworkspace
```shell
# 可能基于SPM， XCode打开 kinit/kinit-admin/ios/App/App.xcodeproj
```