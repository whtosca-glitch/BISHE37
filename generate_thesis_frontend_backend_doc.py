import zipfile
from pathlib import Path
from xml.sax.saxutils import escape


ROOT = Path(r"d:\37")
SOURCE = ROOT / "24_计科专升本赵人赔202414957_重庆城科毕业设计论文过程稿-2.docx"
OUTPUT = ROOT / "环境监测平台论文前后端技术功能分析_仅论文.docx"


paragraphs = [
    ("title", "环境监测平台论文前后端技术与功能分析"),
    ("normal", "说明：本分析文档只基于《24_计科专升本赵人赔202414957_重庆城科毕业设计论文过程稿-2.docx》整理，不结合当前代码仓库的实际实现，不引用答辩稿、README 或其他项目文件。"),
    ("normal", f"论文来源：{SOURCE.name}"),

    ("heading1", "一、论文给出的总体结论"),
    ("normal", "论文将系统定位为“基于 OneNet 平台的仓库环境监控大屏系统”，总体采用前后端分离架构，整体结构由设备接入层、数据处理层和界面呈现层组成。"),
    ("bullet", "设备接入层：负责温湿度、烟雾等环境参数采集，终端通过 MQTT 或 HTTP 与 OneNet 平台交互。"),
    ("bullet", "数据处理层：负责数据传输、接口调用、认证校验、业务处理、数据存储和预警逻辑。"),
    ("bullet", "界面呈现层：负责可视化大屏、交互式仪表盘、趋势图、状态展示和用户操作入口。"),
    ("normal", "论文明确提出：系统目标不仅是展示实时数据，还要实现数据采集、实时监控、智能告警、远程控制、认证安全和可视化分析等完整业务闭环。"),

    ("heading1", "二、论文中的前端要求与技术选型"),
    ("normal", "根据论文“开发环境与工具选型”部分，前端部分的主要要求是承担界面开发、交互逻辑和可视化展示，并与后端 RESTful API 进行数据交互。"),
    ("bullet", "开发工具：Visual Studio Code。"),
    ("bullet", "核心语言：JavaScript。"),
    ("bullet", "前端框架：Vue.js。"),
    ("bullet", "脚手架：Vue CLI。"),
    ("bullet", "可视化技术：ECharts。"),
    ("bullet", "工程化工具：Webpack。"),
    ("bullet", "依赖管理：npm。"),
    ("normal", "论文对前端能力的要求主要体现在三个方面。"),
    ("bullet", "第一，搭建动态可视化监控界面，展示温度、湿度、烟雾浓度、设备状态等信息。"),
    ("bullet", "第二，提供交互能力，例如查看状态、触发控制、查看告警、展示仪表盘和趋势图。"),
    ("bullet", "第三，保证页面具备动态刷新能力和较好的用户操作便利性。"),

    ("heading1", "三、论文中的后端要求与技术选型"),
    ("normal", "根据论文“开发环境与工具选型”部分，后端部分的职责是提供 API 服务、承载业务逻辑、对接 OneNet 平台、管理数据库并完成安全控制。"),
    ("bullet", "开发工具：IntelliJ IDEA。"),
    ("bullet", "后端语言：Java。"),
    ("bullet", "后端框架：Spring Boot。"),
    ("bullet", "接口风格：RESTful API。"),
    ("bullet", "云平台对接：OneNet 官方 Java SDK。"),
    ("bullet", "数据库：MySQL。"),
    ("bullet", "数据库管理工具：Navicat。"),
    ("bullet", "版本管理：Git + GitHub 或 GitLab。"),
    ("bullet", "测试工具：JUnit + Postman。"),
    ("bullet", "部署方式：Docker + Nginx。"),
    ("normal", "论文对后端能力的要求可以总结为五类。"),
    ("bullet", "第一，接收和处理前端请求，并向前端输出统一业务数据。"),
    ("bullet", "第二，负责 OneNet API 调用、设备认证、状态查询和远程控制。"),
    ("bullet", "第三，负责历史记录、参数设置、状态数据和告警数据存储。"),
    ("bullet", "第四，负责阈值判断、异常识别、预警通知和权限控制。"),
    ("bullet", "第五，负责测试、部署、反向代理和环境迁移。"),

    ("heading1", "四、论文要求实现的核心功能"),
    ("normal", "论文内容中反复出现的核心功能主要包括以下几个模块。"),
    ("bullet", "多传感器数据采集。"),
    ("bullet", "设备接入与管理。"),
    ("bullet", "实时环境监测。"),
    ("bullet", "状态可视化展示。"),
    ("bullet", "智能告警与预警通知。"),
    ("bullet", "远程控制。"),
    ("bullet", "数据存储与历史记录管理。"),
    ("bullet", "认证与权限控制。"),
    ("bullet", "测试与部署。"),

    ("heading1", "五、各功能对应的前后端技术分析"),
    ("heading2", "1. 多传感器数据采集"),
    ("normal", "功能目标：接入温湿度传感器、烟雾报警装置等设备，实现高频次采样和环境参数上传。"),
    ("bullet", "前端技术：前端不直接参与采集，但需要提供数据展示界面和刷新后的可视化结果。"),
    ("bullet", "后端技术：需要使用 OneNet 平台、MQTT/HTTP 通信协议、设备认证机制、JSON 数据封装能力。"),
    ("bullet", "论文依据：论文明确提出传感设备通过 MQTT 实现采集，并通过 OneNet API 完成高效传输。"),

    ("heading2", "2. 设备接入与管理"),
    ("normal", "功能目标：完成设备注册、凭证管理、协议选择、设备状态查看和参数配置。"),
    ("bullet", "前端技术：需要提供设备信息展示、配置界面和管理入口，适合用 Vue.js 做页面组织与交互。"),
    ("bullet", "后端技术：需要用 Spring Boot 提供设备管理 API，调用 OneNet Java SDK，完成 DeviceID、APIKey 等凭证处理。"),
    ("bullet", "数据库技术：MySQL 需要保存设备档案、参数设置和设备状态历史。"),

    ("heading2", "3. 实时环境监测"),
    ("normal", "功能目标：实时查看温度、湿度、烟雾浓度和设备运行状态。"),
    ("bullet", "前端技术：Vue.js 负责页面组件化，ECharts 负责温湿度曲线、状态仪表盘和动态图表，JavaScript 负责轮询或异步请求。"),
    ("bullet", "后端技术：Spring Boot 提供实时监测接口，OneNet API 返回实时属性数据，后端完成数据清洗与业务封装。"),
    ("bullet", "性能要求：论文提出实时展示刷新延迟应控制在 3 秒以内。"),

    ("heading2", "4. 状态可视化展示"),
    ("normal", "功能目标：以大屏形式展示系统运行情况、时间序列变化和空间分布信息。"),
    ("bullet", "前端技术：ECharts 是论文明确指定的核心可视化技术，用于时间序列曲线图、交互式仪表盘、统计图等。"),
    ("bullet", "后端技术：后端负责把原始设备数据转换成适合图表展示的数据结构，通过 RESTful API 提供给前端。"),
    ("bullet", "工程化技术：Webpack 与 npm 用于前端资源打包、依赖管理和性能优化。"),

    ("heading2", "5. 智能告警与预警通知"),
    ("normal", "功能目标：当温湿度、烟雾浓度或设备状态异常时，根据阈值触发告警并形成通知。"),
    ("bullet", "前端技术：需要提供阈值设置界面、告警列表、状态提示、图形化异常展示和消息查看入口。"),
    ("bullet", "后端技术：需要在服务端实现阈值比较、异常判断、告警生成、告警记录保存和多渠道通知逻辑。"),
    ("bullet", "数据库技术：MySQL 需要保存告警规则、历史告警记录和异常事件信息。"),
    ("bullet", "论文依据：论文提到用户可自定义告警规则，并支持短信、邮箱、平台内部消息等通知方式。"),

    ("heading2", "6. 远程控制"),
    ("normal", "功能目标：通过统一界面对通风设备、照明系统等执行单元进行远程指令下发和反馈。"),
    ("bullet", "前端技术：需要提供控制按钮、状态回显和交互反馈界面。"),
    ("bullet", "后端技术：Spring Boot 调用 OneNet API 或 Java SDK，下发控制指令并处理执行结果。"),
    ("bullet", "平台技术：OneNet 提供双向通信能力，是控制链路的核心平台支撑。"),

    ("heading2", "7. 数据存储与历史记录"),
    ("normal", "功能目标：保存历史记录、参数配置、监测数据和统计结果，支撑后续分析与追溯。"),
    ("bullet", "前端技术：主要负责历史数据查询界面、统计报表和图表展示。"),
    ("bullet", "后端技术：负责数据入库、查询接口、分析处理和数据组织。"),
    ("bullet", "数据库技术：论文明确指定 MySQL 保存历史记录和参数设置，Navicat 用于可视化管理。"),

    ("heading2", "8. 认证与权限控制"),
    ("normal", "功能目标：保证系统访问安全和核心资源保护。"),
    ("bullet", "前端技术：需要提供登录入口、认证提示和权限控制后的跳转流程。"),
    ("bullet", "后端技术：需要通过 API 网关或认证模块实现身份校验、权限控制和安全防护。"),
    ("bullet", "论文依据：论文明确提出系统自带认证模块，并采用 API 网关进行权限控制规则管理。"),

    ("heading2", "9. 测试与部署"),
    ("normal", "功能目标：保障系统稳定运行、接口正确和部署可迁移。"),
    ("bullet", "前端技术：前端资源由 Nginx 分发，部署时与后端服务进行联调。"),
    ("bullet", "后端技术：JUnit 用于单元测试，Postman 用于接口测试，Docker 用于容器化部署，Nginx 用于反向代理和负载均衡。"),

    ("heading1", "六、论文中的前后端功能分工"),
    ("normal", "从论文表述来看，前后端职责分工非常清晰。"),
    ("bullet", "前端更偏向“展示与交互”：页面结构、状态展示、图表可视化、控制界面、告警展示。"),
    ("bullet", "后端更偏向“连接与处理”：OneNet 对接、协议处理、业务逻辑、数据存储、告警判断、安全认证。"),
    ("bullet", "数据库承担“沉淀与支撑”：保存历史记录、参数设置、告警数据和设备状态。"),
    ("normal", "因此，论文要求的系统不是单纯网页展示，而是一套完整的“设备接入 + 平台通信 + 业务服务 + 可视化前端”的分层系统。"),

    ("heading1", "七、可直接用于汇报的归纳结论"),
    ("bullet", "论文明确要求采用前后端分离架构，前端负责可视化与交互，后端负责业务处理与 OneNet 平台对接。"),
    ("bullet", "前端技术路线为：JavaScript + Vue.js + Vue CLI + ECharts + Webpack + npm。"),
    ("bullet", "后端技术路线为：Java + Spring Boot + RESTful API + OneNet Java SDK + MySQL + Navicat。"),
    ("bullet", "测试与部署路线为：JUnit + Postman + Docker + Nginx。"),
    ("bullet", "核心功能包括：数据采集、设备管理、实时监测、可视化大屏、智能告警、远程控制、历史存储、认证安全。"),
    ("bullet", "每个功能都需要前端与后端协同完成，其中前端负责页面与图表，后端负责接口、平台对接、业务规则和数据管理。"),

    ("heading1", "八、最终分析结果"),
    ("normal", "如果严格按照论文内容来回答“系统用了什么前后端技术、要实现哪些功能、每个功能要用到哪些技术”，则可以概括为：论文设计的是一个基于 OneNet 平台的智能仓库环境监控系统，采用 Vue.js 前端 + Spring Boot 后端 + MySQL 数据库的技术组合，通过 MQTT/HTTP 与物联网平台通信，再借助 ECharts 实现大屏可视化，并围绕监测、告警、控制、存储和安全构建完整业务闭环。"),
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
