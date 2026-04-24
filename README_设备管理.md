# 设备管理本地服务说明

## 1. 功能说明

当前项目新增了一个本地 Python 服务：

- 主页面通过本地服务读取设备列表
- 支持手动新增设备
- 支持按指定设备删减设备
- 支持 MySQL 与本地 Excel 双写
- MySQL 不可用或 30 秒内未连接成功时，自动回退到本地 Excel
- 页面点击“强制启动”后，本次刷新前只读 Excel，不再读 MySQL
- 每次 MySQL 成功连接后，都会用 Excel 表内容同步 MySQL，保证两边一致

## 2. 你现在需要填写的 MySQL 占位符

请打开文件：

- [mysql_config.json](file:///d:/37/mysql_config.json)

把下面几个占位符改成你自己的 MySQL 信息：

- `YOUR_MYSQL_HOST`
- `YOUR_MYSQL_USER`
- `YOUR_MYSQL_PASSWORD`
- `YOUR_MYSQL_DATABASE`

还要把：

- `"enabled": false`

改成：

- `"enabled": true`

## 3. 推荐填写示例

```json
{
  "server": {
    "host": "127.0.0.1",
    "port": 8000
  },
  "mysql": {
    "enabled": true,
    "host": "127.0.0.1",
    "port": 3306,
    "user": "root",
    "password": "123456",
    "database": "onenet_screen",
    "table": "onenet_devices",
    "charset": "utf8mb4",
    "connect_timeout": 30
  }
}
```

## 4. MySQL 建表方式

如果你希望手动先建表，可以执行：

- [device_registry.sql](file:///d:/37/sql/device_registry.sql)

如果你不手动执行也可以，本地服务启动后会自动尝试创建表。

## 5. Excel 本地表位置

本地 Excel 文件会自动生成在：

- `d:\37\data\devices.xlsx`

说明：

- 第一次启动服务时如果文件不存在，会自动创建
- 如果 MySQL 不可用，页面会直接读写这个 Excel
- 删除设备时，会先删 Excel，再把 MySQL 同步成和 Excel 一样

## 6. 如何启动

推荐直接双击项目根目录下的一键启动文件：

- `start_project.bat`

它会自动：

- 启动本地 Python 服务
- 首次缺少依赖时自动安装 `pymysql`、`requests`、`openpyxl`
- 自动打开登录页
- 通过登录后进入主页面

如果你希望手动启动，也可以在项目根目录 `d:\37` 执行：

```bash
python device_service.py
```

启动成功后打开：

```text
http://127.0.0.1:8000/
```

## 7. 强制启动说明

页面中的“强制启动”按钮不是启动 OneNET 设备，而是：

- 强制当前页面后续设备列表读取 Excel
- 本次页面不再读取 MySQL
- 刷新页面后恢复默认逻辑

## 8. 当前默认设备

为了保证你一启动就能看到数据，系统会自动在 Excel 中预置一条默认设备：

- 设备显示名：`demo`
- OneNET 设备名：`demo`
- 产品 ID：`61ZnL1etk7`
- 用户 ID：`483694`

你后续可以继续新增自己的设备。
