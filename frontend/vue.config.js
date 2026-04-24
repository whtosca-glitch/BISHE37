module.exports = {
  publicPath: '/',
  outputDir: 'dist',
  assetsDir: 'assets',
  pages: {
    index: {
      entry: 'src/main-dashboard.js',
      template: 'public/index.html',
      filename: 'index.html',
      title: '设备环境监测平台'
    },
    login: {
      entry: 'src/main-login.js',
      template: 'public/login.html',
      filename: 'login.html',
      title: '登录 - 设备环境监测平台'
    },
    app_demo: {
      entry: 'src/main-app-demo.js',
      template: 'public/app_demo.html',
      filename: 'app_demo.html',
      title: '设备控制页'
    }
  }
}
