import zipfile
from pathlib import Path
from xml.sax.saxutils import escape


ROOT = Path(r"d:\37")
OUTPUT = ROOT / "readme_答辩.docx"


paragraphs = [
    ("title", "设备环境监测平台毕业答辩参考稿"),
    ("normal", "说明：本稿结合论文过程稿与当前项目实际实现整理，适用于毕业答辩口述参考。内容按照“从登录页开始，逐步讲系统功能、实现原理、关键技术、数据库设计”的思路编写。按答辩口径要求，涉及数据持久化和数据模型时统一按 MySQL 技术体系回答。"),

    ("heading1", "一、项目概述与总体架构"),
    ("normal", "本项目是一个面向物联网场景的设备环境监测平台，目标是把温度、湿度、烟雾浓度和设备在线状态等信息从 OneNET 平台拉取下来，再经过本地服务处理后，以可视化大屏和控制页面的形式展示出来，同时提供设备管理、统计分析、告警中心和远程控制等功能。"),
    ("normal", "从整体结构上看，这个系统可以概括为四层架构。"),
    ("bullet", "第一层是设备接入层，主要负责采集温度、湿度、烟雾浓度和开关状态，并把数据上报到云平台。"),
    ("bullet", "第二层是云平台层，项目中使用的是 OneNET 平台，负责设备连接、属性上报、属性查询和控制指令下发。"),
    ("bullet", "第三层是业务服务层，使用 Python 编写本地服务，负责登录鉴权、OneNET 接口封装、业务数据聚合、MySQL 数据管理和告警逻辑计算。"),
    ("bullet", "第四层是前端展示层，采用 HTML、CSS、jQuery 和 ECharts 实现登录页面、大屏页面和设备控制页面。"),
    ("normal", "这个架构最大的特点是“前端不直接访问 OneNET，而是统一通过本地服务访问”。这样做可以把 AccessKey 和鉴权逻辑放在服务端，提升安全性，同时让统计、告警、设备管理、趋势分析这些逻辑都集中在后端处理，便于系统扩展。"),

    ("heading1", "二、从登录页开始，逐个功能讲答辩内容"),
    ("heading2", "1. 登录页面的实现原理与技术"),
    ("normal", "项目展示的入口是登录页。登录页本身用原生 HTML 编写，表单中包含账号和密码输入框，前端通过 JavaScript 把表单数据封装成 JSON，然后提交给本地 Python 服务的 /api/login 接口。"),
    ("normal", "后端在接收到账号和密码之后，会先进行参数读取和字符串清洗，再与系统中预设的 root 和 root01 进行比较。如果校验通过，后端会返回 code 等于 0 的成功响应，并通过 Set-Cookie 把登录状态写到浏览器里；如果校验失败，则返回 401 状态码，并提示“登陆失败”。"),
    ("normal", "登录成功之后，前端会自动跳转到首页。这一部分使用的技术并不复杂，但答辩时要强调两个点。"),
    ("bullet", "第一，登录的核心是前后端分离式会话控制，不是前端自己判断，而是由后端发 Cookie 管理登录状态。"),
    ("bullet", "第二，服务端对页面和接口都做了登录保护，未登录访问主页时会自动跳转回登录页，访问业务接口时会直接返回 401，这说明系统不是静态页面，而是具备基础安全控制的。"),
    ("normal", "如果老师问为什么没有做复杂权限系统，可以回答：本项目定位是毕业设计演示系统，登录模块重点在于体现完整的访问控制链路，而不是企业级 RBAC 权限体系。"),

    ("heading2", "2. 主页面总体展示是如何实现的"),
    ("normal", "登录成功后进入主页面。主页面的布局采用大屏风格，页面上方是头部导航，中间是核心监测区域，下方是趋势图、使用频率和告警中心。"),
    ("normal", "主页面并不是直接把 OneNET 返回的原始数据堆到页面里，而是通过本地服务先做了一次业务聚合。具体流程是：前端页面打开后，会分别调用 /api/devices、/api/device-properties、/api/metrics、/api/status-trend、/api/alarms、/api/weather 等接口；这些接口全部由本地 Python 服务统一对外提供。"),
    ("normal", "也就是说，主页面实际上是一个前后端协同的仪表盘系统。前端负责渲染，后端负责业务组织和数据清洗。"),
    ("normal", "这部分的主要技术是："),
    ("bullet", "前端使用 jQuery 做 Ajax 请求和事件处理。"),
    ("bullet", "图表使用 ECharts 做可视化展示。"),
    ("bullet", "后端使用 Python ThreadingHTTPServer 提供轻量化 HTTP 服务。"),
    ("bullet", "后端使用 requests 访问 OneNET 和天气接口。"),
    ("normal", "答辩时可以强调，这种架构比前端直连云平台更适合毕业设计，因为它既能体现系统完整性，也便于后续扩展。"),

    ("heading2", "3. 设备管理功能是如何实现的"),
    ("normal", "设备管理模块支持新增设备和删减设备。新增设备时，前端弹出表单，让用户填写显示名称、IP、设备名称、产品 ID、用户 ID、AccessKey、鉴权版本、设备秘钥和设备 ID 等信息。"),
    ("normal", "这些字段本质上就是设备接入档案。在数据库设计上，我统一按 MySQL 来描述。可以理解为系统设计了一张设备主表 onenet_devices，这张表主要保存设备基础信息和 OneNET 接入信息，核心字段包括 record_id、display_name、onenet_device_name、product_id、user_id、access_key、device_secret、device_id、ip、start_success_count、created_at、updated_at 等。"),
    ("normal", "前端点击新增设备后，会把表单数据提交到 /api/devices。后端接收到数据后，会做三件事。"),
    ("bullet", "第一，校验必填字段是否完整，例如设备名称、产品 ID、用户 ID 和 AccessKey 是否为空。"),
    ("bullet", "第二，生成内部唯一标识 record_id，保证每台设备在数据库中都有唯一主键。"),
    ("bullet", "第三，把设备记录写入 MySQL 中的设备主表，并更新服务端当前设备列表。"),
    ("normal", "删减设备的过程与之对应，前端只传 record_id，后端根据这个唯一主键删除对应设备记录。"),
    ("normal", "这里的技术亮点不是单纯的增删改查，而是把 OneNET 平台的接入参数与系统内部设备台账做了绑定，使设备管理不只是显示层逻辑，而是真正的数据持久化管理。"),

    ("heading2", "4. 实时温度、湿度、烟雾浓度和在线状态是如何实现的"),
    ("normal", "项目中的温度、湿度、烟雾浓度和在线状态，实时数据源来自 OneNET，而不是直接从 MySQL 读取。数据库在这里负责保存设备档案和统计结果，不保存每次刷新时的实时属性值。"),
    ("normal", "具体实现过程是这样的：前端点击某个设备或页面定时轮询时，会请求 /api/device-properties，并把当前设备的 record_id 传给后端。后端先通过 record_id 去设备主表中查出这台设备的 product_id、user_id、access_key 和 onenet_device_name，然后生成 OneNET 所要求的 authorization 鉴权头。"),
    ("normal", "鉴权的核心原理是 HMAC-SHA1 签名。后端会根据用户 ID、AccessKey、过期时间和资源标识拼接签名内容，再进行 HMAC-SHA1 运算，最后生成 authorization 字符串。然后服务端再调用 OneNET 的 query-device-property 接口，把 product_id 和 device_name 发出去。"),
    ("normal", "OneNET 返回的是属性数组，后端会进一步把它解析成更符合业务语义的字段。比如把温度属性映射为 temp，把湿度属性映射为 humi，把烟雾属性映射为 smoke，把 status 属性转成在线或离线。前端接收到这些业务字段后，再填充到右侧设备详情卡片中。"),
    ("normal", "答辩时如果老师问“为什么不直接在前端请求 OneNET”，可以回答：因为 AccessKey 和签名逻辑必须保留在后端，本地服务统一代理访问 OneNET，可以保护密钥，同时便于在后端做数据格式整理。"),

    ("heading2", "5. 首页统计指标和趋势图是如何实现的"),
    ("normal", "首页上的设备总数、当前在线数量、本月新增设备数和近五日报错数，都是通过后端聚合接口 /api/metrics 统一返回的。"),
    ("normal", "从数据库角度回答时，可以把这些指标理解成对 MySQL 业务表的统计。"),
    ("bullet", "设备总数来自设备主表 onenet_devices 的总记录数。"),
    ("bullet", "本月新增设备数来自设备主表按 created_at 进行月份过滤后的计数结果。"),
    ("bullet", "当前在线数量来自设备状态表，或由后端轮询 OneNET 后计算再回写到状态快照表。"),
    ("bullet", "近五日报错数来自告警日志表中最近五天告警记录的累计总数。"),
    ("normal", "最近五天在线统计图的实现思路，是后端每次刷新设备状态时，将当前在线数、离线数、未知状态数和总设备数按日期维度汇总，再存入状态历史表。前端调用 /api/status-trend 后，使用 ECharts 绘制最近五天的在线、离线柱状图。"),
    ("normal", "设备使用频率图的实现思路，是将每台设备的启动成功在线次数作为横向条形图的数据源。前端渲染图表时，还会结合设备当前 online 状态决定条形颜色和标签文字，例如离线设备会加上离线标记。"),
    ("normal", "从技术实现角度，这部分体现的是前端轮询 + 后端聚合 + 图表重绘的组合模式。页面不会手动刷新，而是通过 JavaScript 定时调用接口，再通过 ECharts 的 setOption 更新图表。"),

    ("heading2", "6. 告警中心是如何实现的"),
    ("normal", "告警中心是本项目最能体现业务逻辑的模块之一。这个模块不是前端单纯写 if 判断，而是后端完成告警规则匹配、告警状态维护和告警日志沉淀。"),
    ("normal", "从 MySQL 设计角度，这里可以统一讲为三张核心表。"),
    ("bullet", "第一张是 alarm_config 告警配置表，用于保存温度、湿度、烟雾和设备状态这四类规则的阈值。"),
    ("bullet", "第二张是 alarm_state 告警状态表，用于记录每台设备在每个规则维度下当前是否处于激活状态。"),
    ("bullet", "第三张是 alarm_logs 告警日志表，用于记录历史告警事件，包括告警 ID、规则名称、告警时间、告警等级和设备名称。"),
    ("normal", "后端每次执行告警刷新时，会遍历设备主表中的设备记录，再实时查询 OneNET 返回的温度、湿度、烟雾和在线状态。之后把这些值与 alarm_config 表中的阈值逐项比较。"),
    ("normal", "例如温度超过设定值就生成温度告警，湿度超过阈值就生成湿度告警，烟雾浓度超过阈值就生成烟雾告警，设备离线或未知就生成状态告警。"),
    ("normal", "这里的实现关键点是，后端不是每次都重复插入日志，而是先读取 alarm_state 表判断当前规则是否已经处于激活状态。如果原来没有激活、这次新激活，才写入一条新的告警日志；如果已经激活，就只更新状态而不重复写日志。这个设计可以避免轮询系统无限生成重复告警。"),
    ("normal", "前端部分则负责显示阈值设置区、告警列表、分页按钮和告警弹窗。当出现新告警时，页面顶部会弹出红色提示框，要求用户手动确认。"),

    ("heading2", "7. 天气模块是如何实现的"),
    ("normal", "天气模块看起来是一个展示功能，但实现方式和设备数据链路类似，也是通过后端代理第三方接口完成的。"),
    ("normal", "原因是浏览器直接访问第三方天气接口容易遇到跨域问题，因此系统由本地 Python 服务统一请求天气接口，再把 JSON 数据转发给前端。前端接收到最近五天的天气信息后，用 ECharts 绘制天气趋势图，同时在顶部指标区域显示当天的天气情况。"),
    ("normal", "这部分的技术重点是服务端代理和前端图表渲染，不涉及复杂数据库逻辑，因此答辩时可以作为系统功能扩展说明。"),

    ("heading2", "8. 设备控制页是如何实现的"),
    ("normal", "在主页面左上角，系统还单独提供了一个设备控制页入口。设备控制页的作用是模拟物联网 APP 的控制能力，在 Web 页面中实现监听和控制的双向链路。"),
    ("normal", "页面打开后，前端会先请求 /api/devices 获取设备列表，然后默认选择一台设备。之后前端每三秒调用一次 /api/app-demo-device，用来持续监听当前设备的温度、湿度、烟雾和设备状态。"),
    ("normal", "同时，页面上还提供了打开设备、关闭设备以及设置温度、湿度、烟雾值的操作按钮。用户点击这些按钮后，前端会把控制数据发送到 /api/device-control。后端收到请求后，会先根据 record_id 去设备主表查询这台设备的 OneNET 连接参数，然后调用 OneNET 的 set-device-property 接口，把 temp、humi、smoke、status 作为属性下发出去。"),
    ("normal", "这个模块体现的是物联网系统的完整闭环：前端负责发指令，本地服务负责鉴权和协议转换，OneNET 负责控制指令透传，最终设备侧接收并执行。"),
    ("normal", "如果老师问“控制页为什么重要”，可以回答：因为一个完整的物联网项目不能只有监测链路，还应该体现控制链路，这样系统才形成感知、传输、分析、控制的完整闭环。"),

    ("heading1", "三、关键技术详细说明"),
    ("heading2", "1. 前端页面技术"),
    ("normal", "前端页面主要使用的是 HTML、CSS、JavaScript、jQuery 和 ECharts。HTML 负责页面结构，CSS 负责大屏风格、布局和弹窗样式，jQuery 负责 Ajax 请求、事件绑定和 DOM 更新，ECharts 负责趋势图、柱状图和使用频率图。"),
    ("normal", "这种技术选型的优点是实现简单、部署轻量、调试方便，适合毕业设计项目。虽然没有使用 Vue 或 React 这类大型框架，但依然实现了完整的页面交互、图表渲染和异步刷新机制。"),

    ("heading2", "2. 后端服务技术"),
    ("normal", "后端服务使用 Python 原生的 BaseHTTPRequestHandler 和 ThreadingHTTPServer 实现，而不是使用 Flask 或 Django。这样做的好处是代码结构更直接，也便于答辩时讲清楚每个接口是怎么接收请求、怎么返回响应的。"),
    ("normal", "本地服务负责三类工作。"),
    ("bullet", "第一类是登录与路由控制，例如 /api/login、未登录重定向。"),
    ("bullet", "第二类是业务接口，例如 /api/devices、/api/device-properties、/api/metrics、/api/status-trend、/api/alarms、/api/device-control。"),
    ("bullet", "第三类是外部接口代理，例如 OneNET 和天气接口。"),
    ("normal", "因为使用的是 ThreadingHTTPServer，所以后端可以并发处理多个前端请求，例如页面同时刷新设备列表、统计指标和告警信息时，服务端可以并行响应。"),

    ("heading2", "3. OneNET 接入技术"),
    ("normal", "项目与 OneNET 平台的对接主要涉及两类接口，一类是查询接口，例如设备属性查询；另一类是控制接口，例如 set-device-property。"),
    ("normal", "OneNET 的核心技术点在于鉴权。项目采用 HMAC-SHA1 的授权方式，生成 authorization 请求头。具体做法是：使用 user_id、到期时间、访问资源和 AccessKey 组合成签名原文，再经过 HMAC-SHA1 运算，最终生成 OneNET 接口要求的签名字符串。"),
    ("normal", "在查询接口中，系统主要用 query-device-property 获取实时属性；在控制接口中，系统主要用 set-device-property 完成温度、湿度、烟雾和开关状态下发。"),

    ("heading2", "4. MySQL 数据库技术"),
    ("normal", "数据库部分答辩时统一按 MySQL 口径回答。MySQL 在本项目中的角色主要有两个：一是保存系统主数据，二是保存业务过程数据。"),
    ("normal", "主数据的核心就是设备主表 onenet_devices，用于管理每台设备的基础信息和 OneNET 接入参数。业务过程数据则包括设备状态快照、状态历史、告警配置、告警状态和告警日志等。"),
    ("normal", "MySQL 设计的意义在于："),
    ("bullet", "第一，设备参数可以长期保存，刷新页面或重启服务后不会丢失。"),
    ("bullet", "第二，统计图表可以依赖历史数据而不是只依赖当前实时值。"),
    ("bullet", "第三，告警中心可以保存历史告警日志，具备追溯能力。"),
    ("bullet", "第四，设备控制和设备管理都可以建立在统一设备主档数据之上。"),

    ("heading2", "5. 前后端交互技术"),
    ("normal", "本项目前后端交互采用的是典型的 HTTP + JSON 模式。前端通过 Ajax 或 fetch 提交请求，后端统一返回 code、msg 和 data 结构，前端再根据返回结果决定是更新界面还是弹出错误提示。"),
    ("normal", "这种统一响应格式的优点是接口风格一致，错误处理简单，前端很容易扩展新的页面和新的功能模块。"),

    ("heading2", "6. 轮询与实时刷新技术"),
    ("normal", "因为项目是物联网监测平台，所以实时性非常重要。系统采用的是定时轮询机制。页面每隔固定时间请求一次本地接口，再更新显示内容。"),
    ("normal", "选择轮询而不是 WebSocket，主要是因为轮询方案更简单、更稳定、更适合毕业设计环境。它不需要维护长连接，实现复杂度低，也便于老师现场演示和理解。"),

    ("heading1", "四、数据库部分统一 MySQL 口径回答"),
    ("normal", "如果老师问数据库设计、表结构或者存储逻辑，可以统一按以下 MySQL 模型回答。"),
    ("bullet", "设备主表 onenet_devices：保存设备基础信息和 OneNET 接入参数，是整个系统的主档表。"),
    ("bullet", "设备状态表 device_status：保存每台设备当前在线状态、最后一次状态更新时间，用于在线状态判断。"),
    ("bullet", "状态历史表 status_history：按日期存储在线数、离线数、未知数和总设备数，用于最近五天在线统计。"),
    ("bullet", "告警配置表 alarm_config：保存温度、湿度、烟雾和状态四类告警规则的阈值和等级。"),
    ("bullet", "告警状态表 alarm_state：保存每台设备在每种规则下是否处于激活态，用于告警去重。"),
    ("bullet", "告警日志表 alarm_logs：保存告警历史记录，用于告警中心分页展示和近五日报错数统计。"),
    ("normal", "如果老师进一步追问为什么要分这么多表，可以回答：这是为了把主数据、实时状态、历史统计和告警日志分层管理，避免所有信息混在一张表里，既不利于查询，也不利于后期扩展。"),

    ("heading1", "五、毕业答辩时可直接复述的完整讲稿"),
    ("normal", "各位老师好，我的毕业设计项目名称是设备环境监测平台。这个系统主要面向物联网应用场景，核心目标是把设备采集到的温度、湿度、烟雾浓度和在线状态数据，通过 OneNET 平台与本地 Python 服务进行整合，再展示到可视化大屏和设备控制页面中。同时，系统还实现了设备管理、告警中心、统计分析和远程控制等功能。"),
    ("normal", "项目首先从登录页开始。登录页的作用是系统统一入口。用户输入账号和密码之后，前端会把表单数据提交到本地服务的登录接口。后端校验成功后，通过 Cookie 保存登录状态，再跳转到首页；如果校验失败，页面会提示登陆失败。这里我采用的是前后端分离式登录方案，重点在于体现完整的访问控制链路。"),
    ("normal", "进入首页之后，页面采用大屏布局，左侧展示统计指标，中间展示天气和趋势图，右侧展示当前设备详情，下方展示最近五天在线统计、设备使用频率和告警中心。整个系统的设计思想是：前端不直接访问 OneNET，而是统一访问本地 Python 服务，再由后端去访问 OneNET 和 MySQL。这样做可以保护 AccessKey，也方便把设备数据、统计数据和告警数据统一聚合。"),
    ("normal", "在设备管理模块中，系统支持新增设备和删减设备。新增时，用户需要填写设备名称、IP、OneNET 设备名称、产品 ID、用户 ID、AccessKey、设备秘钥等参数。这些参数会统一保存到 MySQL 的设备主表中，从而形成完整的设备接入档案。这样一来，即使页面刷新或者服务重启，设备数据仍然可以保留。"),
    ("normal", "在实时监测部分，系统会根据设备主表中的 OneNET 参数生成 authorization，然后调用 OneNET 的设备属性查询接口，获取温度、湿度、烟雾浓度和在线状态。后端把这些原始属性映射成 temp、humi、smoke、status 等业务字段，再返回给前端显示。所以这部分的核心技术包括 OneNET HTTP API、HMAC-SHA1 鉴权和 Python 后端代理查询。"),
    ("normal", "在统计分析部分，系统会统计设备总数、当前在线数量、本月新增设备数和近五日报错数。最近五天在线统计图来源于后端对设备状态的日维度汇总，并保存到 MySQL 的状态历史表中。设备使用频率图则根据设备启动成功在线次数绘制，并且能区分在线和离线设备。图表部分主要使用 ECharts 来完成可视化展示。"),
    ("normal", "告警中心模块支持温度、湿度、烟雾浓度和设备状态四类告警。前端可以设置阈值，但真正的告警判断逻辑在后端完成。后端会把告警阈值保存到 MySQL 的告警配置表，把当前激活状态保存到告警状态表，把历史告警保存到告警日志表。每次刷新时，系统会实时获取设备属性并和阈值比较，如果检测到新的告警，就写入日志，同时页面顶部弹出红色提示框提醒用户。"),
    ("normal", "除了监测功能外，我还设计了一个设备控制页面。用户可以选择设备，并实时监听温度、湿度、烟雾和开关状态；同时也可以通过页面直接下发打开设备、关闭设备或设置温度、湿度、烟雾值的控制指令。前端把指令提交给本地服务，再由本地服务调用 OneNET 的 set-device-property 接口完成下发。这一部分体现的是物联网系统中的控制链路，也就是前端发指令、本地服务统一鉴权、云平台完成设备控制。"),
    ("normal", "总体来说，这个项目的亮点主要有三个。第一，是完成了 OneNET 云平台接入，并通过本地 Python 服务实现统一聚合。第二，是围绕设备管理、统计分析、告警管理和控制页面形成了完整业务闭环。第三，是数据库部分采用 MySQL 口径进行建模，体现了设备主数据、状态历史、告警配置和告警日志分层管理的设计思想。我的汇报完毕，谢谢各位老师。"),

    ("heading1", "六、老师追问时的标准回答"),
    ("bullet", "如果老师问为什么不让前端直接访问 OneNET：可以回答后端代理模式更安全，因为 AccessKey 和鉴权算法不暴露在浏览器里，同时也便于统一做 MySQL 数据管理和业务聚合。"),
    ("bullet", "如果老师问数据库怎么设计：就按设备主表、设备状态表、状态历史表、告警配置表、告警状态表、告警日志表这 6 张 MySQL 业务表来回答。"),
    ("bullet", "如果老师问为什么告警逻辑放后端：可以回答因为告警属于业务规则，应该和阈值配置、状态去重、日志保存一起放在服务端，方便统一管理。"),
    ("bullet", "如果老师问为什么系统还要做设备控制页：可以回答因为一个完整的物联网系统不仅要监测，还要能控制设备，这样才能体现感知、传输、分析、控制的完整闭环。"),
    ("bullet", "如果老师问轮询为什么选 3 秒或 30 秒：可以回答监测页和控制页对实时性要求不同，控制页强调近实时监听，所以轮询更密；大屏侧强调稳定和总览，所以轮询间隔相对更长。"),
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
