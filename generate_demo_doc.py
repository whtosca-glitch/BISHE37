import zipfile
from pathlib import Path
from xml.sax.saxutils import escape


ROOT = Path(r"d:\37")
OUTPUT = ROOT / "5分钟项目展示话术.docx"

paragraphs = [
    ("title", "设备环境监测平台 5 分钟项目展示流程与话术"),
    ("normal", "适用场景：毕业设计答辩、课程项目展示、论文过程稿汇报。"),
    ("normal", "展示目标：在 5 分钟内，边演示边说明项目功能、技术原理、实现思路和工程亮点，方便直接照着复述。"),

    ("heading1", "一、项目定位"),
    ("normal", "这套系统的定位是一个面向物联网场景的设备环境监测平台，核心目标是把 OneNET 云平台上的设备数据，通过本地服务整合之后，以大屏可视化的形式展示出来，同时支持设备管理、告警中心、状态统计和本地容灾。"),
    ("normal", "从论文过程稿对应的系统架构来看，它不是单纯的前端页面，而是由四层组成：设备与云平台层、本地服务层、数据存储层、可视化展示层。"),
    ("bullet", "设备与云平台层：设备把温度、湿度、烟雾浓度和在线状态上报到 OneNET。"),
    ("bullet", "本地服务层：本地 Python 服务负责统一对接 OneNET、整理数据、鉴权和业务封装。"),
    ("bullet", "数据存储层：系统使用 Excel 做本地保底存储，MySQL 作为可选增强存储。"),
    ("bullet", "可视化展示层：前端用 ECharts 和 jQuery 做大屏图表和交互展示。"),

    ("heading1", "二、5 分钟展示流程"),
    ("heading2", "第 1 分钟：登录与系统入口"),
    ("normal", "我的展示首先从系统入口开始。这里我先打开一键启动文件，系统会自动启动本地 Python 服务，并进入登录页面。"),
    ("normal", "在登录这一层，我用的是本地鉴权机制。用户输入账号 root 和密码 root01，前端把账号密码发到本地 /api/login 接口，后端校验成功之后通过 Cookie 保存登录状态，只有登录成功才能进入主页面。"),
    ("normal", "这一部分体现的技术点主要有两个：第一是前后端分离的登录校验思想，第二是通过本地服务做统一入口控制，保证未登录时不能直接访问主界面。"),

    ("heading2", "第 2 分钟：主页面整体架构展示"),
    ("normal", "进入主页面之后，我先介绍整个界面布局。页面左侧展示统计指标，中间展示天气和趋势图，右侧展示当前设备详情，下方展示最近五天在线统计、设备使用频率以及告警中心。"),
    ("normal", "这部分我会先点出项目思路：不是把 OneNET 接口直接暴露给浏览器，而是由本地 Python 服务统一去访问云端，再把处理后的结果返回前端，这样做的优点是更安全，也更容易做本地缓存、告警计算和多数据源切换。"),

    ("heading2", "第 3 分钟：设备管理与数据持久化"),
    ("normal", "接下来我演示设备管理功能。系统支持新增设备、删减设备，并且可以在新增时填写设备显示名称、IP、产品 ID、用户 ID、AccessKey、鉴权版本、设备秘钥等 OneNET 所需参数。"),
    ("normal", "新增之后，这些参数不会只存在页面里，而是会被持久化到本地 Excel 文件中，必要时还可以同步到 MySQL。"),
    ("normal", "这里我重点说明两个原理。"),
    ("bullet", "第一，本地服务维护了一个 devices.xlsx 文件，里面不仅保存设备基础信息，还保存状态历史、告警阈值、告警记录等多个工作表。"),
    ("bullet", "第二，为了避免刷新页面后数据丢失，系统采用了加锁和原子写入机制：写入时先保存到临时文件，再替换正式文件，从而避免 Excel 被并发写坏。"),
    ("normal", "所以这个模块体现的是设备配置持久化、本地容灾和数据一致性的设计思路。"),

    ("heading2", "第 4 分钟：实时监测与统计展示"),
    ("normal", "然后我演示实时监测部分。右侧面板可以展示当前设备的 IP、名称、ID、温度、湿度、烟雾浓度和在线状态。切换不同设备时，右侧信息会同步切换。"),
    ("normal", "这背后的原理是：本地 Python 服务根据每台设备保存的 AccessKey、用户 ID 和鉴权版本，生成 OneNET 的 authorization，然后调用 query-device-property 接口拉取属性数据。"),
    ("normal", "为了展示这部分技术思路，我会强调三点。"),
    ("bullet", "第一，OneNET 的鉴权不是明文账号密码，而是基于 user_id、过期时间和 AccessKey 做 HMAC-SHA1 签名。"),
    ("bullet", "第二，接口返回的是属性数组，系统在本地把它整理成温度、湿度、烟雾、在线状态这样的业务字段，再交给前端展示。"),
    ("bullet", "第三，前端采用定时轮询机制，每 30 秒刷新一次设备列表、统计指标和趋势图，从而保证大屏数据具有实时性。"),
    ("normal", "在统计方面，左上角的近五日报错数并不是固定值，而是统计本地告警中心最近五天累计记录数；设备数、当前在线数量、本月新增设备数等指标也都来自本地服务的聚合接口。"),

    ("heading2", "第 5 分钟：告警中心与工程亮点"),
    ("normal", "最后我演示告警中心。告警中心支持在页面上直接设置温度、湿度和烟雾阈值，当设备温度、湿度、烟雾超阈值，或者设备状态变成离线、未知时，系统会生成一条本地告警记录。"),
    ("normal", "告警 ID 这里显示的是设备名称，规则名称显示的是当前告警类型，例如温度、湿度、烟雾浓度或在线状态，告警时间读取本地系统时间，告警等级则区分为紧急、重要、次要和提醒。"),
    ("normal", "一旦产生新的活动告警，页面顶部会弹出一个红色确认式提示框，必须人工点击确定才会关闭。"),
    ("normal", "这部分我会强调它体现的工程思路是："),
    ("bullet", "把告警逻辑放到本地服务层，而不是前端硬编码。"),
    ("bullet", "把阈值配置、当前活动告警状态和历史告警日志都持久化到 Excel。"),
    ("bullet", "实现页面展示、业务判断和数据留痕的闭环。"),

    ("heading1", "三、可直接复述的话术"),
    ("normal", "下面是一段可以直接照着讲的完整口述稿。"),
    ("normal", "各位老师好，我展示的项目是一个基于 OneNET 平台和本地 Python 服务实现的设备环境监测平台。这个项目的核心思路是，把设备采集到的温度、湿度、烟雾浓度和在线状态先上传到 OneNET，再由本地服务统一完成数据获取、设备管理、告警判断和本地存储，最后通过大屏页面进行可视化展示。"),
    ("normal", "首先在系统入口部分，我设计了一个登录页，账号是 root，密码是 root01。登录时前端会把账号密码提交到本地登录接口，后端校验通过后再跳转主页面。这样做的目的是保证主系统页面有基本的访问控制。"),
    ("normal", "进入主页面后，可以看到系统按模块分成了统计指标区、趋势图区、设备详情区和告警中心区。整体架构上，浏览器并不直接访问 OneNET，而是访问本地 Python 服务，由本地服务去完成鉴权、数据拉取和业务封装。这种方式的好处是安全性更高，也更方便做本地缓存和离线容灾。"),
    ("normal", "在设备管理部分，系统支持新增和删减设备。新增时除了设备显示名称和 IP，还需要填写 OneNET 所需的产品 ID、用户 ID、AccessKey、设备名称等参数。所有这些信息都会持久化保存在本地 Excel 文件中，所以即使刷新页面，或者切换到强制本地模式，刚刚新增的设备也不会丢失。这里我重点采用了原子写入和加锁机制，避免多个请求同时操作 Excel 时导致文件损坏。"),
    ("normal", "在实时监测部分，系统会根据每台设备的 OneNET 鉴权参数生成 authorization，然后调用云平台接口去查询设备属性。获取到的数据经过本地服务整理后，再展示到页面上，包括温度、湿度、烟雾浓度和在线状态。页面还会每 30 秒做一次轮询刷新，用来保证显示结果和设备真实状态保持同步。"),
    ("normal", "在统计分析部分，系统会汇总当前设备数、在线数量、本月新增设备数，以及近五日报错数。最近五天在线统计图展示的是系统近五天的在线与离线变化趋势，设备使用频率图则展示各设备的启动成功在线次数，并且如果设备离线，还会在标签中额外标记离线状态。"),
    ("normal", "最后是告警中心。这里可以直接设置温度、湿度和烟雾的阈值，本地服务会根据阈值和设备状态判断是否触发告警。告警记录会保存到 Excel 中，页面会以表格形式展示历史告警，同时顶部弹出红色确认提示框，提醒管理员及时处理。这个模块体现的是规则配置、实时判断和本地留痕的完整闭环。"),
    ("normal", "总体来说，这个项目的技术亮点主要有三点。第一，是基于 OneNET 的云端数据获取与 HMAC 鉴权机制；第二，是本地 Python 服务对前端、云接口和本地存储的统一桥接；第三，是设备管理、统计分析、趋势可视化和本地告警中心构成了一个比较完整的物联网监测系统。我的展示到这里结束，谢谢各位老师。"),

    ("heading1", "四、老师追问时可补充的技术点"),
    ("bullet", "为什么不用前端直接连 OneNET：因为后端代理更安全，AccessKey 不直接暴露给浏览器。"),
    ("bullet", "为什么还要保留 Excel：因为 Excel 可以作为本地保底数据源，MySQL 不可用时系统依然能运行。"),
    ("bullet", "为什么告警放本地做：因为本地更适合做阈值配置、状态去重和历史记录沉淀。"),
    ("bullet", "为什么使用轮询：因为这个项目更强调实现稳定、部署简单，轮询比 WebSocket 更适合当前场景。"),

    ("heading1", "五、演示顺序清单"),
    ("bullet", "1. 双击一键启动文件，打开登录页。"),
    ("bullet", "2. 输入 root / root01 登录。"),
    ("bullet", "3. 介绍主页面四大区域。"),
    ("bullet", "4. 演示新增设备，说明 Excel 持久化。"),
    ("bullet", "5. 演示设备详情和 OneNET 实时属性。"),
    ("bullet", "6. 演示最近五天在线统计和设备使用频率。"),
    ("bullet", "7. 演示告警中心阈值配置和告警弹窗。"),
    ("bullet", "8. 用一段总结话术收尾。"),
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
