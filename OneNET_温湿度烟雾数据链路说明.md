# OneNET 温度/湿度/烟雾数据链路说明

## 1. 目的

本文基于当前项目源码，梳理该 APP 如何通过 OneNET 平台获取温度、湿度、烟雾浓度数据，并说明：

- OneNET 请求鉴权方式
- OneNET 返回报文的字段结构
- 前端页面如何把数据展示出来
- 当前项目中和后续复用相关的注意事项

本文主要依据以下源码文件：

- `key.js`
- `pages/index/index.vue`
- `pages/message/message.vue`
- `pages/project/project.vue`
- `pages/LineChartTemp/LineChartTemp.vue`
- `pages/LineChartHumi/LineChartHumi.vue`
- `pages/lineChartSmoke/lineChartSmoke.vue`

---

## 2. 核心结论

当前项目里真正稳定使用的一条主链路在首页 `pages/index/index.vue`：

1. 前端在 `onLoad()` 中调用 `key.js` 生成 OneNET 的 `authorization` token。
2. 前端在 `onShow()` 中调用 `getRealData()`，并每 3 秒轮询一次。
3. `getRealData()` 通过 `uni.request()` 请求 OneNET 的物模型属性查询接口：
   - `GET https://iot-api.heclouds.com/thingmodel/query-device-property`
4. OneNET 返回设备属性数组后，页面按数组下标取出：
   - 湿度 `data[0].value`
   - 烟雾浓度 `data[1].value`
   - 设备状态 `data[2].value`
   - 温度 `data[3].value`
5. 页面把这几个值分别绑定到首页卡片上显示。

也就是说，当前 APP 采用的是：

`单片机上报属性 -> OneNET 保存设备属性 -> APP 轮询 OneNET HTTP 接口 -> 前端展示`

不是 APP 直接连单片机，也不是 MQTT 长连接直接推送到前端页面。

---

## 3. 鉴权与请求逻辑

### 3.1 token 生成位置

文件：`key.js`

项目通过 `createCommonToken(params)` 生成请求头中的 `authorization` 字段。

主要逻辑如下：

1. 读取参数：
   - `author_key`
   - `version`
   - `user_id`
2. 组装资源字符串：

```text
userid/{user_id}
```

3. 计算过期时间 `et`
4. 使用 `sha1` 进行 HMAC 签名
5. 拼接 token：

```text
version={version}&res={res}&et={et}&method=sha1&sign={sign}
```

### 3.2 首页初始化 token

文件：`pages/index/index.vue`

在 `onLoad()` 中：

```js
const params = {
  author_key: '28f571afc3494b249637acada7cc12a7',
  version: '2022-05-01',
  user_id: '483694',
}
this.token = createCommonToken(params);
```

说明：

- 当前项目是前端直接生成 token
- 后续项目如果要更安全，建议改成后端生成后再下发给前端

### 3.3 OneNET 查询接口

文件：`pages/index/index.vue`

请求代码如下：

```js
uni.request({
  url: 'https://iot-api.heclouds.com/thingmodel/query-device-property',
  method: 'GET',
  data: {
    product_id: my_product_id,
    device_name: my_device_name
  },
  header: {
    'authorization': this.token
  },
  success: (res) => {
    let data = res.data.data;
    this.realHumi = data[0].value;
    this.realSmoke = data[1].value;
    this.deviceStatus = data[2].value === 'true';
    this.realTemp = data[3].value;
  }
});
```

其中当前首页使用的设备信息是：

- `product_id = "61ZnL1etk7"`
- `device_name = "demo"`

---

## 4. OneNET 返回报文结构

### 4.1 当前项目实际请求到的一次返回示例

下面是根据仓库中的鉴权参数和设备参数，实际请求 OneNET 接口后得到的一次响应结构整理版：

```json
{
  "code": 0,
  "msg": "succ",
  "request_id": "96f6900123fa444289539b8be7d991b3",
  "data": [
    {
      "identifier": "humi",
      "time": 1776266552575,
      "value": "90",
      "data_type": "int32",
      "access_mode": "读写",
      "name": "湿度"
    },
    {
      "identifier": "smoke",
      "time": 1776266552575,
      "value": "729",
      "data_type": "int32",
      "access_mode": "读写",
      "name": "烟雾浓度"
    },
    {
      "identifier": "status",
      "time": 1776266552575,
      "value": "true",
      "data_type": "bool",
      "access_mode": "读写",
      "name": "设备状态",
      "description": "0"
    },
    {
      "identifier": "temp",
      "time": 1776266552575,
      "value": "67.00",
      "data_type": "float",
      "access_mode": "读写",
      "name": "温度"
    }
  ]
}
```

### 4.2 字段说明

最外层字段：

- `code`: 接口状态码，`0` 表示成功
- `msg`: 接口返回消息
- `request_id`: 本次请求 ID
- `data`: 设备属性数组

`data` 数组内单个属性对象字段：

- `identifier`: 属性标识符，程序最应该依赖这个字段
- `time`: 属性更新时间，通常是时间戳
- `value`: 属性值，注意这里返回的是字符串形式
- `data_type`: 属性数据类型，如 `int32`、`float`、`bool`
- `access_mode`: 访问模式，如 `读写`
- `name`: 属性中文名称
- `description`: 个别属性可能会附带说明字段，不一定每项都有

### 4.3 当前项目中的属性映射关系

根据真实返回结果，当前设备属性顺序为：

1. `humi` -> 湿度
2. `smoke` -> 烟雾浓度
3. `status` -> 设备状态
4. `temp` -> 温度

因此首页源码中采用了如下映射：

```js
this.realHumi = data[0].value;
this.realSmoke = data[1].value;
this.deviceStatus = data[2].value === 'true';
this.realTemp = data[3].value;
```

---

## 5. 前端展示逻辑

## 5.1 首页实时展示

文件：`pages/index/index.vue`

### 数据状态

首页 `data()` 中定义了以下字段：

```js
return {
  realTemp: '',
  realHumi: '',
  realSmoke: '',
  deviceStatus: false,
  setTemp: 30,
  setHumi: 50,
  setSmoke: 200,
  token: '',
}
```

其中：

- `realTemp`、`realHumi`、`realSmoke` 是 OneNET 返回的实时值
- `deviceStatus` 是设备状态
- `setTemp`、`setHumi`、`setSmoke` 是下发给云平台的阈值

### 页面模板绑定

首页模板中，实时数据显示区域如下：

```html
<view class="dev-cart" @click="goLineChartTemp">
  <view>
    <view class="dev-name">温度</view>
    <image class="dev-logo" src="../../static/temp.png"></image>
  </view>
  <view class="dev-data">{{realTemp}} ℃</view>
</view>

<view class="dev-cart">
  <view>
    <view class="dev-name">湿度</view>
    <image class="dev-logo" src="../../static/soil-humi.png"></image>
  </view>
  <view class="dev-data">{{realHumi}} %</view>
</view>

<view class="dev-cart">
  <view>
    <view class="dev-name">烟雾浓度</view>
    <image class="dev-logo" src="../../static/air.png"></image>
  </view>
  <view class="dev-data">{{realSmoke}} ppm</view>
</view>
```

这说明前端展示方式非常直接：

1. `getRealData()` 更新组件状态
2. Vue/uni-app 响应式系统检测到 `realTemp`、`realHumi`、`realSmoke` 变化
3. 页面重新渲染
4. 卡片文本显示最新数值

### 逻辑结构图

```text
onLoad()
  -> createCommonToken()
  -> token 就绪

onShow()
  -> getRealData()
  -> setInterval(每3秒执行一次 getRealData)

getRealData()
  -> uni.request(query-device-property)
  -> res.data.data
  -> 提取 humi/smoke/status/temp
  -> 更新 realHumi/realSmoke/deviceStatus/realTemp
  -> 首页卡片自动刷新
```

---

## 5.2 历史数据的本地缓存链路

文件：`pages/index/index.vue`、`pages/message/message.vue`、`pages/project/project.vue`

首页在请求成功后，还额外发出了一个全局事件：

```js
uni.$emit('sensorDataUpdate', {
  temp: this.realTemp,
  humi: this.realHumi,
});
```

这表示：

- 首页除了实时展示外
- 还把部分实时数据广播给其他页面使用

### `message.vue` 的处理方式

`pages/message/message.vue` 中：

1. `onLoad()` 里监听 `sensorDataUpdate`
2. 收到事件后执行 `addRecord(data)`
3. 把数据写入本地存储 `sensor_history_records`

对应逻辑：

```js
uni.$on('sensorDataUpdate', this.addRecord);
```

```js
const newRecord = {
  time: new Date().toLocaleString('zh-CN', { hour12: false }),
  temp: typeof data.temp !== 'undefined' ? data.temp : '--',
  humi: typeof data.humi !== 'undefined' ? data.humi : '--',
  light: typeof data.light !== 'undefined' ? data.light : '--',
  distance: typeof data.distance !== 'undefined' ? data.distance : '--'
};
```

注意：

- 当前这里只缓存了 `temp` 和 `humi`
- 没有缓存 `smoke`
- 所以烟雾浓度虽然能在首页实时显示，但没有进入这套本地历史记录结构

### `project.vue` 的处理方式

`pages/project/project.vue` 不直接请求 OneNET，而是：

1. 周期性读取本地存储 `sensor_history_records`
2. 把历史记录转换成图表 `categories` 和 `series`
3. 用 `qiun-data-charts` 绘制趋势图

也就是说：

- 首页实时卡片 = 直接读 OneNET
- 历史表格/历史趋势 = 读首页保存到本地的数据

---

## 6. 设备控制与数据下发

首页除了获取实时数据，还可以向 OneNET 下发属性。

### 6.1 设备开关

接口：

- `POST https://iot-api.heclouds.com/thingmodel/set-device-property`

下发内容：

```json
{
  "product_id": "61ZnL1etk7",
  "device_name": "demo",
  "params": {
    "status": true
  }
}
```

### 6.2 温度/湿度/烟雾阈值下发

同样调用 `set-device-property`，只是参数不同：

```json
{
  "product_id": "61ZnL1etk7",
  "device_name": "demo",
  "params": {
    "temp": 30
  }
}
```

或：

```json
{
  "product_id": "61ZnL1etk7",
  "device_name": "demo",
  "params": {
    "humi": 50
  }
}
```

或：

```json
{
  "product_id": "61ZnL1etk7",
  "device_name": "demo",
  "params": {
    "smoke": 200
  }
}
```

说明：

- 这些阈值在当前页面中属于“前端写 OneNET”
- OneNET 再把对应属性同步给设备侧

---

## 7. 当前项目里的旧逻辑与注意事项

### 7.1 旧图表页使用了另一套设备参数

以下页面也在直接请求 OneNET：

- `pages/LineChartTemp/LineChartTemp.vue`
- `pages/LineChartHumi/LineChartHumi.vue`
- `pages/lineChartSmoke/lineChartSmoke.vue`

但它们使用的设备信息是：

- `product_id = "CNHpdX7Y1n"`
- `device_name = "esp32"`

和首页当前使用的：

- `product_id = "61ZnL1etk7"`
- `device_name = "demo"`

不是同一套设备。

因此这几页更像旧版本残留代码，不能直接作为当前首页链路的补充依据。

### 7.2 旧图表页依赖本地 token，但源码里没有存 token

这些旧图表页中有：

```js
this.token = uni.getStorageSync('token');
```

但当前源码里没有发现：

```js
uni.setStorageSync('token', ...)
```

因此这些页面即使打开，也可能拿不到有效 token。

### 7.3 首页跳转地址和实际页面注册不一致

首页中：

```js
uni.navigateTo({
  url: "/pages/chart/temp"
})
```

但 `pages.json` 中注册的实际页面路径是：

- `pages/LineChartTemp/LineChartTemp`
- `pages/LineChartHumi/LineChartHumi`
- `pages/lineChartSmoke/lineChartSmoke`

说明这个跳转逻辑也有旧代码残留问题。

### 7.4 当前首页按数组下标取值，有顺序依赖风险

当前首页这样写：

```js
this.realHumi = data[0].value;
this.realSmoke = data[1].value;
this.deviceStatus = data[2].value === 'true';
this.realTemp = data[3].value;
```

问题：

- 代码依赖 OneNET 返回数组的固定顺序
- 如果平台返回顺序变化，页面就会错位显示

更稳妥的写法应该按 `identifier` 映射，例如：

```js
const propertyMap = {};
for (const item of res.data.data || []) {
  propertyMap[item.identifier] = item.value;
}

this.realHumi = propertyMap.humi || '';
this.realSmoke = propertyMap.smoke || '';
this.deviceStatus = propertyMap.status === 'true';
this.realTemp = propertyMap.temp || '';
```

---

## 8. 适合后续项目复用的推荐结构

如果后续项目还要接 OneNET，建议按照下面结构组织：

### 8.1 建议的数据拉取层

```text
services/
  onenet.js
```

职责：

- 生成 token
- 发起 `query-device-property`
- 发起 `set-device-property`
- 统一把返回数组转成 `identifier -> value` 的对象

### 8.2 建议的统一返回格式

前端业务层最好不要直接依赖 OneNET 原始数组，而是转成：

```js
{
  temp: '67.00',
  humi: '90',
  smoke: '729',
  status: 'true'
}
```

这样页面层只关心：

- `temp`
- `humi`
- `smoke`
- `status`

不用关心 OneNET 的数组顺序。

### 8.3 建议的展示链路

```text
OneNET API
  -> 数据服务层统一解析
  -> 页面状态 data/reactive
  -> 首页卡片显示
  -> 可选：写入本地缓存
  -> 历史表格/历史趋势图读取缓存
```

---

## 9. 本项目可直接复用的关键代码片段

### 9.1 查询 OneNET 属性

```js
uni.request({
  url: 'https://iot-api.heclouds.com/thingmodel/query-device-property',
  method: 'GET',
  data: {
    product_id: my_product_id,
    device_name: my_device_name
  },
  header: {
    authorization: this.token
  },
  success: (res) => {
    const propertyMap = {};
    for (const item of res.data.data || []) {
      propertyMap[item.identifier] = item.value;
    }

    this.realTemp = propertyMap.temp || '';
    this.realHumi = propertyMap.humi || '';
    this.realSmoke = propertyMap.smoke || '';
    this.deviceStatus = propertyMap.status === 'true';
  }
});
```

### 9.2 前端模板展示

```html
<view class="dev-data">{{realTemp}} ℃</view>
<view class="dev-data">{{realHumi}} %</view>
<view class="dev-data">{{realSmoke}} ppm</view>
```

---

## 10. 最终总结

当前项目通过 OneNET 获取温度、湿度、烟雾浓度数据的核心方式是：

1. `key.js` 生成 OneNET 鉴权 token
2. 首页 `pages/index/index.vue` 调用 `query-device-property`
3. OneNET 返回属性数组 `data`
4. 前端从数组中取出 `humi`、`smoke`、`status`、`temp`
5. 把值绑定到页面中的 `realHumi`、`realSmoke`、`deviceStatus`、`realTemp`
6. 通过模板插值直接显示在首页卡片上

当前项目里最适合后续参考的部分是：

- `key.js` 的 token 生成逻辑
- `pages/index/index.vue` 的实时查询与展示逻辑

当前项目里需要谨慎参考的部分是：

- 旧图表页中的另一套设备参数
- 依赖数组下标的属性取值方式
- 历史记录中未保存烟雾浓度的问题

