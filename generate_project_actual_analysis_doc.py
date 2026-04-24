import zipfile
from pathlib import Path
from xml.sax.saxutils import escape


ROOT = Path(r"d:\37")
OUTPUT = ROOT / "项目实际前后端技术功能分析.docx"


paragraphs = [
    ("title", "项目实际前后端技术、功能与平台 Key 分析"),
    ("normal", "说明：本文件基于当前项目代码实际实现整理，不按论文方案回答。分析范围主要包括前端页面、后端服务、接口设计、功能模块、关键代码、平台相关 key 与配置项。"),

    ("heading1", "一、项目实际架构结论"),
    ("normal", "当前项目实际采用的是轻量级前后端分离架构。前端以静态页面为主，后端由本地 Python 服务统一提供接口，并代理访问 OneNET 与天气接口。"),
    ("bullet", "前端技术栈：HTML、CSS、JavaScript、jQuery、ECharts。"),
    ("bullet", "后端技术栈：Python、BaseHTTPRequestHandler、ThreadingHTTPServer、requests、openpyxl、可选 pymysql。"),
    ("bullet", "数据存储：Excel 为默认本地持久化，MySQL 为可选增强存储。"),
    ("bullet", "页面组成：login.html 登录页、index.html 大屏主页、app_demo.html 设备控制页。"),
    ("bullet", "后端主文件：device_service.py。"),

    ("heading1", "二、前端要求与实际使用技术"),
    ("normal", "从当前项目实际实现来看，前端并没有使用 Vue 或 React，而是以传统静态页面加脚本驱动的方式实现。"),
    ("bullet", "HTML：负责页面骨架，定义登录页、主页、设备控制页、弹窗、表单、告警详情区和 RCS 地图容器。"),
    ("bullet", "CSS：负责大屏布局、按钮样式、告警颜色、弹窗样式、RCS 地图样式与状态光点。"),
    ("bullet", "JavaScript：负责事件绑定、定时轮询、接口调用、表单提交、页面状态管理与图表渲染。"),
    ("bullet", "jQuery：负责 Ajax 请求、DOM 更新、事件代理。"),
    ("bullet", "ECharts：负责最近五天在线统计、设备使用频率、天气趋势等可视化图表。"),

    ("heading1", "三、后端要求与实际使用技术"),
    ("normal", "后端由一个本地 Python 服务承担全部核心业务能力，既负责登录、设备、告警、统计等业务接口，也负责访问 OneNET 和天气服务。"),
    ("bullet", "HTTP 服务：使用 BaseHTTPRequestHandler + ThreadingHTTPServer。"),
    ("bullet", "云平台访问：使用 requests 调用 OneNET HTTP API 与天气接口。"),
    ("bullet", "本地持久化：使用 openpyxl 读写 Excel，多 Sheet 保存设备、状态历史、告警配置、告警状态、告警日志。"),
    ("bullet", "数据库增强：使用 pymysql 连接 MySQL，在可用时同步设备主表。"),
    ("bullet", "鉴权与安全：使用 Cookie 维护登录态，使用 HMAC-SHA1 生成 OneNET authorization。"),

    ("heading1", "四、项目要实现的核心功能"),
    ("bullet", "登录鉴权。"),
    ("bullet", "设备新增、修改、删减。"),
    ("bullet", "设备实时属性读取。"),
    ("bullet", "设备控制页监听与控制。"),
    ("bullet", "主页统计指标展示。"),
    ("bullet", "最近五天在线统计图。"),
    ("bullet", "设备使用频率图。"),
    ("bullet", "告警中心、阈值管理、告警详情、处理记录。"),
    ("bullet", "天气预报与 RCS 地图切换。"),
    ("bullet", "RCS 地图 20 槽位设备增删改。"),
    ("bullet", "Excel / MySQL 双模式持久化。"),
    ("bullet", "一键启动。"),

    ("heading1", "五、每个功能对应的前后端技术"),
    ("heading2", "1. 登录鉴权"),
    ("bullet", "前端：login.html 使用原生 JavaScript 和 fetch 向 /api/login 提交账号密码。"),
    ("bullet", "后端：device_service.py 中 _handle_login 校验用户名密码，成功后通过 Set-Cookie 写入 device_dashboard_auth=authenticated。"),
    ("bullet", "相关技术：fetch、JSON、Cookie、HTTP 401、重定向。"),

    ("heading2", "2. 设备管理"),
    ("bullet", "前端：index.html 中设备表单负责录入显示名称、IP、OneNET 设备名称、product_id、user_id、access_key、auth_version、device_secret、device_id、slot_index 等字段。"),
    ("bullet", "前端：js/index.js 中 submitSaveDevice、submitDeleteDevice 负责调用 POST /api/devices、PUT /api/devices/{id}、DELETE /api/devices/{id}。"),
    ("bullet", "后端：DeviceRepository.add_device、update_device、delete_device 负责设备台账的校验、保存、更新和删除。"),
    ("bullet", "相关技术：jQuery Ajax、JSON、Excel 持久化、MySQL 同步、RCS 槽位校验。"),

    ("heading2", "3. 实时属性监测"),
    ("bullet", "前端：js/index.js 中 fetchDeviceProperty、syncCurrentDevice 拉取 /api/device-properties。"),
    ("bullet", "后端：get_device_properties 根据 record_id 找到设备档案，再调用 OneNET /thingmodel/query-device-property。"),
    ("bullet", "相关技术：OneNET HTTP API、authorization 签名、属性解析、定时轮询。"),

    ("heading2", "4. 设备控制页"),
    ("bullet", "前端：app_demo.html 周期性请求 /api/app-demo-device 监听温度、湿度、烟雾、开关状态。"),
    ("bullet", "前端：app_demo.html 中 sendControl 通过 /api/device-control 下发 temp、humi、smoke、status。"),
    ("bullet", "后端：set_device_properties 调用 OneNET /thingmodel/set-device-property。"),
    ("bullet", "相关技术：fetch、JSON、OneNET 控制接口、轮询刷新、输入与监听值分离。"),

    ("heading2", "5. 指标统计与图表"),
    ("bullet", "前端：ECharts 负责天气图、最近五天在线统计、设备使用频率图。"),
    ("bullet", "后端：get_metrics 汇总设备总数、在线数量、本月新增设备数、近五日报错数。"),
    ("bullet", "后端：get_status_trend 从状态历史表生成最近五天在线与离线数据。"),
    ("bullet", "相关技术：ECharts setOption、聚合统计、状态历史快照、定时轮询。"),

    ("heading2", "6. 告警中心"),
    ("bullet", "前端：alarmCenter 模块负责阈值表单、分页告警表格、顶部告警弹窗、告警详情弹窗、处理状态更新。"),
    ("bullet", "后端：save_alarm_config、get_alarm_list、get_alarm_detail、mark_alarm_processed 负责规则保存、日志生成、详情查询、处理记录写入。"),
    ("bullet", "后端：_build_alarm_evaluations 负责把温度、湿度、烟雾、状态与阈值比较并判定告警。"),
    ("bullet", "相关技术：Excel 多 Sheet、规则配置、状态去重、JSON 处理记录、颜色徽标、手动确认弹窗。"),

    ("heading2", "7. RCS 地图"),
    ("bullet", "前端：index.html 定义天气/地图切换区、20 个地图槽位详情面板和地图内操作按钮。"),
    ("bullet", "前端：js/index.js 中 echart_3 实现天气与地图切换、槽位点击、新增到此、修改设备、删减设备。"),
    ("bullet", "后端：设备记录新增 slot_index 字段，并在 add/update 时校验占用冲突。"),
    ("bullet", "相关技术：DOM 动态渲染、状态光点、槽位持久化、设备与地图联动。"),

    ("heading2", "8. 本地存储与数据库"),
    ("bullet", "后端：Excel 为主存储，文件路径是 data/devices.xlsx。"),
    ("bullet", "后端：MySQL 可选启用，通过 mysql_config.json 配置。"),
    ("bullet", "后端：_save_workbook_atomic 使用临时文件 + os.replace 保证原子写入。"),
    ("bullet", "相关技术：openpyxl、文件锁、pymysql、自动建表、双写同步。"),

    ("heading2", "9. 一键启动"),
    ("bullet", "前端：无独立前端逻辑。"),
    ("bullet", "后端与运维：start_project.bat 调起 start_project.ps1，自动检测 Python、安装依赖、启动 device_service.py，并打开登录页。"),
    ("bullet", "相关技术：PowerShell、pip、日志重定向、端口检测、自动打开浏览器。"),

    ("heading1", "六、项目实际关键接口"),
    ("bullet", "POST /api/login：登录。"),
    ("bullet", "GET /api/devices：获取设备列表。"),
    ("bullet", "POST /api/devices：新增设备。"),
    ("bullet", "PUT /api/devices/{id}：修改设备。"),
    ("bullet", "DELETE /api/devices/{id}：删减设备。"),
    ("bullet", "GET /api/device-properties：获取设备实时属性。"),
    ("bullet", "GET /api/metrics：获取首页指标。"),
    ("bullet", "GET /api/status-trend：获取最近五天在线统计。"),
    ("bullet", "GET /api/alarms：获取告警列表。"),
    ("bullet", "GET /api/alarm-config：读取告警阈值。"),
    ("bullet", "POST /api/alarm-config：保存告警阈值。"),
    ("bullet", "GET /api/alarm-detail：获取告警详情。"),
    ("bullet", "POST /api/alarm-process：处理告警。"),
    ("bullet", "GET /api/app-demo-device：设备控制页监听当前设备。"),
    ("bullet", "POST /api/device-control：控制下发。"),
    ("bullet", "GET /api/weather：获取天气数据。"),

    ("heading1", "七、平台相关 Key、账号、配置项"),
    ("heading2", "1. 登录相关"),
    ("bullet", "登录账号：root。"),
    ("bullet", "登录密码：root01。"),
    ("bullet", "Cookie 名：device_dashboard_auth。"),
    ("bullet", "Cookie 值：authenticated。"),

    ("heading2", "2. OneNET 默认演示设备 Key"),
    ("bullet", "默认 record_id：default-demo-device。"),
    ("bullet", "默认显示名：demo。"),
    ("bullet", "默认 OneNET 设备名：demo。"),
    ("bullet", "默认 product_id：61ZnL1etk7。"),
    ("bullet", "默认 user_id：483694。"),
    ("bullet", "默认 access_key：28f571afc3494b249637acada7cc12a7。"),
    ("bullet", "默认 auth_version：2020-05-29。"),
    ("bullet", "默认 device_secret：Y2Vrdmc5cHZVWGdRb2RMektNME9NNUVKOFlaTHFQMVM=。"),
    ("bullet", "默认 device_id：2575390487。"),
    ("normal", "说明：这些值来自当前仓库中 device_service.py 的默认演示设备配置。"),

    ("heading2", "3. MySQL 配置 Key"),
    ("bullet", "配置文件：mysql_config.json。"),
    ("bullet", "server.host：127.0.0.1。"),
    ("bullet", "server.port：8000。"),
    ("bullet", "mysql.enabled：false。"),
    ("bullet", "mysql.host：YOUR_MYSQL_HOST。"),
    ("bullet", "mysql.port：3306。"),
    ("bullet", "mysql.user：YOUR_MYSQL_USER。"),
    ("bullet", "mysql.password：YOUR_MYSQL_PASSWORD。"),
    ("bullet", "mysql.database：YOUR_MYSQL_DATABASE。"),
    ("bullet", "mysql.table：onenet_devices。"),
    ("bullet", "mysql.charset：utf8mb4。"),
    ("bullet", "mysql.connect_timeout：30。"),

    ("heading2", "4. 其他平台配置"),
    ("bullet", "天气默认城市代码：101010100。"),
    ("bullet", "本地服务地址：http://127.0.0.1:8000/。"),
    ("bullet", "登录页地址：http://127.0.0.1:8000/login.html。"),
    ("bullet", "依赖包：pymysql、requests、openpyxl。"),

    ("heading1", "八、相关技术实现核心代码"),
    ("heading2", "1. 登录鉴权核心代码"),
    ("code", "device_service.py"),
    ("code", "LOGIN_USERNAME = \"root\""),
    ("code", "LOGIN_PASSWORD = \"root01\""),
    ("code", "AUTH_COOKIE_NAME = \"device_dashboard_auth\""),
    ("code", "AUTH_COOKIE_VALUE = \"authenticated\""),
    ("code", "if username == LOGIN_USERNAME and password == LOGIN_PASSWORD:"),
    ("code", "    self._send_json(..., extra_headers=[(\"Set-Cookie\", f\"{AUTH_COOKIE_NAME}={AUTH_COOKIE_VALUE}; Path=/; HttpOnly; SameSite=Lax\")])"),

    ("heading2", "2. OneNET authorization 生成核心代码"),
    ("code", "def _create_authorization(self, access_key, user_id, version):"),
    ("code", "    method = \"sha1\""),
    ("code", "    res = f\"userid/{user_id}\""),
    ("code", "    et = str(int(datetime.now().timestamp()) + 3600)"),
    ("code", "    sign_text = et + \"\\n\" + method + \"\\n\" + res + \"\\n\" + version"),
    ("code", "    key = base64.b64decode(access_key)  # 失败则退回 utf-8"),
    ("code", "    sign = base64.b64encode(hmac.new(key, sign_text.encode(\"utf-8\"), hashlib.sha1).digest()).decode(\"utf-8\")"),
    ("code", "    return \"version={}&res={}&et={}&method={}&sign={}\".format(...)"),

    ("heading2", "3. 实时属性读取核心代码"),
    ("code", "def get_device_properties(self, record_id, force_excel=False):"),
    ("code", "    record = self._find_record(record_id, force_excel=force_excel)"),
    ("code", "    property_data = self._query_onenet(record, \"/thingmodel/query-device-property\", {\"product_id\": record[\"product_id\"], \"device_name\": record[\"onenet_device_name\"]})"),
    ("code", "    for item in property_data.get(\"data\") or []:"),
    ("code", "        property_map[item.get(\"identifier\")] = item.get(\"value\")"),
    ("code", "    return {\"temp\": property_map.get(\"temp\", \"\"), \"humi\": property_map.get(\"humi\", \"\"), \"smoke\": property_map.get(\"smoke\", \"\"), \"status\": property_map.get(\"status\", \"false\")}"),

    ("heading2", "4. 控制下发核心代码"),
    ("code", "def set_device_properties(self, record_id, payload, force_excel=False):"),
    ("code", "    for key in (\"temp\", \"humi\", \"smoke\", \"status\"):"),
    ("code", "        params[key] = value"),
    ("code", "    response = requests.post(\"https://iot-api.heclouds.com/thingmodel/set-device-property\", json={\"product_id\": record[\"product_id\"], \"device_name\": record[\"onenet_device_name\"], \"params\": params}, headers={\"authorization\": authorization, \"Content-Type\": \"application/json\"}, timeout=15)"),

    ("heading2", "5. 设备表单保存核心代码"),
    ("code", "js/index.js"),
    ("code", "function submitSaveDevice() {"),
    ("code", "    var payload = getFormPayload();"),
    ("code", "    var isEdit = state.modalMode === 'edit' && state.editingRecordId;"),
    ("code", "    $.ajax({"),
    ("code", "        url: isEdit ? '/api/devices/' + encodeURIComponent(state.editingRecordId) : '/api/devices',"),
    ("code", "        method: isEdit ? 'PUT' : 'POST',"),
    ("code", "        contentType: 'application/json; charset=utf-8',"),
    ("code", "        data: JSON.stringify(payload)"),
    ("code", "    })"),

    ("heading2", "6. 告警处理核心代码"),
    ("code", "function processAlarm(logId) {"),
    ("code", "    $.ajax({ url: '/api/alarm-process', method: 'POST', contentType: 'application/json; charset=utf-8', data: JSON.stringify({ log_id: logId }) })"),
    ("code", "def mark_alarm_processed(self, log_id):"),
    ("code", "    item['process_status'] = '已处理'"),
    ("code", "    item['process_records'].append({'time': now_stamp, 'action': '已处理', 'operator': 'root', 'note': item['process_note']})"),

    ("heading2", "7. RCS 地图槽位核心代码"),
    ("code", "EXCEL_HEADERS 中新增 slot_index 字段。"),
    ("code", "def _apply_slot_assignment(self, record, records, exclude_record_id=None):"),
    ("code", "    if normalize_slot_index(item.get('slot_index')) == slot_index and slot_index:"),
    ("code", "        raise ValueError(f'RCS地图槽位 {slot_index} 已被占用')"),
    ("code", "js/index.js 中 echart_3 通过 slotPositions 渲染 20 个槽位。"),

    ("heading2", "8. 一键启动核心代码"),
    ("code", "start_project.bat"),
    ("code", "powershell -NoProfile -ExecutionPolicy Bypass -File \"%~dp0start_project.ps1\""),
    ("code", "start_project.ps1"),
    ("code", "& $pythonPath -c \"import pymysql, requests, openpyxl\""),
    ("code", "Start-Process -FilePath $pythonPath -ArgumentList $pythonStartArgs -WorkingDirectory $projectRoot -RedirectStandardOutput $stdoutLog -RedirectStandardError $stderrLog -WindowStyle Hidden"),

    ("heading1", "九、数据库与本地表结构实际情况"),
    ("bullet", "Excel 主表头：record_id、display_name、onenet_device_name、product_id、user_id、access_key、auth_version、device_secret、device_id、ip、start_success_count、slot_index、notes、created_at、updated_at。"),
    ("bullet", "Excel 还包含：status_history、device_status、alarm_config、alarm_logs、alarm_state 五个业务 Sheet。"),
    ("bullet", "MySQL 当前自动维护主表 onenet_devices。"),
    ("bullet", "注意：sql/device_registry.sql 当前未包含 slot_index 字段，但运行时 device_service.py 会自动检测并补列。"),

    ("heading1", "十、最终分析结论"),
    ("normal", "当前项目的实际实现是一套以 Python 本地服务为核心的物联网监测平台，而不是传统的 Java Web 项目。前端采用 HTML、CSS、jQuery、ECharts 构建登录页、大屏页和设备控制页；后端使用 BaseHTTPRequestHandler、ThreadingHTTPServer、requests、openpyxl 和可选 pymysql 完成登录鉴权、OneNET 对接、设备管理、告警处理、统计聚合、本地持久化和一键启动支撑。平台相关 key 主要包括登录账号密码、Cookie 名值、OneNET 的 product_id、user_id、access_key、auth_version、device_secret、device_id，以及 mysql_config.json 中的连接参数。"),
]


def make_paragraph(text, style="normal"):
    text = escape(text)
    if style == "title":
        return (
            "<w:p><w:pPr><w:jc w:val=\"center\"/></w:pPr>"
            "<w:r><w:rPr><w:b/><w:sz w:val=\"34\"/></w:rPr>"
            f"<w:t>{text}</w:t></w:r></w:p>"
        )
    if style == "heading1":
        return (
            "<w:p><w:pPr><w:spacing w:before=\"240\" w:after=\"120\"/></w:pPr>"
            "<w:r><w:rPr><w:b/><w:sz w:val=\"30\"/></w:rPr>"
            f"<w:t>{text}</w:t></w:r></w:p>"
        )
    if style == "heading2":
        return (
            "<w:p><w:pPr><w:spacing w:before=\"160\" w:after=\"80\"/></w:pPr>"
            "<w:r><w:rPr><w:b/><w:sz w:val=\"26\"/></w:rPr>"
            f"<w:t>{text}</w:t></w:r></w:p>"
        )
    if style == "bullet":
        return (
            "<w:p><w:r><w:rPr><w:b/></w:rPr><w:t>• </w:t></w:r>"
            f"<w:r><w:t>{text}</w:t></w:r></w:p>"
        )
    if style == "code":
        return (
            "<w:p><w:pPr><w:spacing w:before=\"20\" w:after=\"20\"/></w:pPr>"
            "<w:r><w:rPr><w:rFonts w:ascii=\"Consolas\" w:hAnsi=\"Consolas\"/><w:sz w:val=\"20\"/></w:rPr>"
            f"<w:t xml:space=\"preserve\">{text}</w:t></w:r></w:p>"
        )
    return f"<w:p><w:r><w:t>{text}</w:t></w:r></w:p>"


body_xml = "".join(make_paragraph(text, style) for style, text in paragraphs)

document_xml = f"""<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<w:document xmlns:wpc="http://schemas.microsoft.com/office/word/2010/wordprocessingCanvas"
 xmlns:mc="http://schemas.openxmlformats.org/markup-compatibility/2006"
 xmlns:o="urn:schemas-microsoft-com:office:office"
 xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships"
 xmlns:m="http://schemas.openxmlformats.org/officeDocument/2006/math"
 xmlns:v="urn:schemas-microsoft-com:vml"
 xmlns:wp14="http://schemas.microsoft.com/office/word/2010/wordprocessingDrawing"
 xmlns:wp="http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing"
 xmlns:w10="urn:schemas-microsoft-com:office:word"
 xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main"
 xmlns:w14="http://schemas.microsoft.com/office/word/2010/wordml"
 xmlns:wpg="http://schemas.microsoft.com/office/word/2010/wordprocessingGroup"
 xmlns:wpi="http://schemas.microsoft.com/office/word/2010/wordprocessingInk"
 xmlns:wne="http://schemas.microsoft.com/office/word/2006/wordml"
 xmlns:wps="http://schemas.microsoft.com/office/word/2010/wordprocessingShape"
 mc:Ignorable="w14 wp14">
 <w:body>
 {body_xml}
 <w:sectPr>
  <w:pgSz w:w="11906" w:h="16838"/>
  <w:pgMar w:top="1440" w:right="1440" w:bottom="1440" w:left="1440" w:header="708" w:footer="708" w:gutter="0"/>
 </w:sectPr>
 </w:body>
</w:document>
"""

content_types = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">
 <Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>
 <Default Extension="xml" ContentType="application/xml"/>
 <Override PartName="/word/document.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml"/>
</Types>
"""

rels = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
 <Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="word/document.xml"/>
</Relationships>
"""

doc_rels = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"></Relationships>
"""


with zipfile.ZipFile(OUTPUT, "w", compression=zipfile.ZIP_DEFLATED) as zf:
    zf.writestr("[Content_Types].xml", content_types)
    zf.writestr("_rels/.rels", rels)
    zf.writestr("word/document.xml", document_xml)
    zf.writestr("word/_rels/document.xml.rels", doc_rels)


print(str(OUTPUT))
