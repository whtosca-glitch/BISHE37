//青岛研锦网络科技有限公司   版权所有
$(function () {
    echart_1();
    echart_2();
    echart_3();
    echart_4();
    alarmCenter();
    $('#app_demo_btn').on('click', function () {
        window.location.href = '/app_demo.html';
    });

    function alarmCenter() {
        var state = {
            forceExcelMode: false,
            rules: [],
            activeToastShown: false,
            items: [],
            pageSize: 5,
            pageIndex: 1,
            currentDetailLogId: ''
        };

        bindAlarmEvents();
        loadAlarmConfig();
        loadAlarmList();

        $(document).on('device-force-excel-changed', function (_, enabled) {
            state.forceExcelMode = !!enabled;
            loadAlarmList();
        });

        setInterval(function () {
            loadAlarmList();
        }, 30000);

        function bindAlarmEvents() {
            $('#save_alarm_config_btn').on('click', function () {
                saveAlarmConfig();
            });
            $('#alarm_prev_btn').on('click', function () {
                changePage(-1);
            });
            $('#alarm_next_btn').on('click', function () {
                changePage(1);
            });
            $('#alarm_table_wrap').on('wheel', function (event) {
                event.preventDefault();
                changePage(event.originalEvent.deltaY > 0 ? 1 : -1);
            });
            $('#alarm_toast_confirm').on('click', function () {
                $('#alarm_toast').addClass('hidden');
            });
            $('#alarm_detail_close_btn, #alarm_detail_modal .device_modal_mask').on('click', function () {
                $('#alarm_detail_modal').addClass('hidden');
            });
            $('#alarm_table_body').on('click', '.alarm_row', function () {
                var logId = $(this).data('logId');
                if (logId) {
                    processAlarm(logId);
                }
            });
            $('#alarm_table_body').on('click', '.alarm_detail_btn', function (event) {
                event.stopPropagation();
                var logId = $(this).data('logId');
                if (logId) {
                    loadAlarmDetail(logId);
                }
            });
        }

        function loadAlarmConfig() {
            $.ajax({
                url: '/api/alarm-config',
                method: 'GET'
            }).then(function (res) {
                if (!res || res.code !== 0 || !res.data) {
                    return;
                }
                state.rules = res.data.rules || [];
                renderAlarmConfig(state.rules);
            }).fail(function (xhr) {
                console.error('获取告警阈值失败:', xhr);
            });
        }

        function loadAlarmList() {
            $.ajax({
                url: '/api/alarms',
                method: 'GET',
                data: {
                    force_excel: state.forceExcelMode ? 1 : 0,
                    limit: 200
                }
            }).then(function (res) {
                if (!res || res.code !== 0) {
                    state.items = [];
                    state.pageIndex = 1;
                    renderAlarmRows([]);
                    return;
                }
                state.rules = (res.data && res.data.config && res.data.config.rules) || state.rules;
                renderAlarmConfig(state.rules);
                state.items = (res.data && res.data.items) || [];
                ensurePageInRange();
                renderAlarmRows(state.items);
                showAlarmPopup(
                    (res.data && res.data.new_alarm_items) || [],
                    (res.data && res.data.active_alarm_items) || []
                );
            }).fail(function (xhr) {
                console.error('获取告警列表失败:', xhr);
                state.items = [];
                state.pageIndex = 1;
                renderAlarmRows([]);
            });
        }

        function saveAlarmConfig() {
            var payload = {
                rules: buildRulePayload()
            };
            $.ajax({
                url: '/api/alarm-config',
                method: 'POST',
                contentType: 'application/json; charset=utf-8',
                data: JSON.stringify(payload)
            }).then(function (res) {
                if (!res || res.code !== 0 || !res.data) {
                    showAlarmToast('阈值保存失败', 'red');
                    return;
                }
                state.rules = res.data.rules || [];
                renderAlarmConfig(state.rules);
                showAlarmToast(res.msg || '阈值已保存', 'blue');
                loadAlarmList();
            }).fail(function (xhr) {
                console.error('保存告警阈值失败:', xhr);
                showAlarmToast('阈值保存失败', 'red');
            });
        }

        function buildRulePayload() {
            var rules = state.rules.slice();
            if (!rules.length) {
                rules = [
                    { rule_key: 'temp', enabled: 1 },
                    { rule_key: 'humi', enabled: 1 },
                    { rule_key: 'smoke', enabled: 1 },
                    { rule_key: 'status', enabled: 1 }
                ];
            }
            return $.map(rules, function (rule) {
                var nextRule = $.extend({}, rule);
                if (rule.rule_key === 'temp') {
                    nextRule.threshold_value = $('#alarm_temp_threshold').val();
                } else if (rule.rule_key === 'humi') {
                    nextRule.threshold_value = $('#alarm_humi_threshold').val();
                } else if (rule.rule_key === 'smoke') {
                    nextRule.threshold_value = $('#alarm_smoke_threshold').val();
                }
                nextRule.enabled = 1;
                return nextRule;
            });
        }

        function renderAlarmConfig(rules) {
            $.each(rules || [], function (_, rule) {
                if (rule.rule_key === 'temp') {
                    $('#alarm_temp_threshold').val(rule.threshold_value);
                } else if (rule.rule_key === 'humi') {
                    $('#alarm_humi_threshold').val(rule.threshold_value);
                } else if (rule.rule_key === 'smoke') {
                    $('#alarm_smoke_threshold').val(rule.threshold_value);
                }
            });
        }

        function renderAlarmRows(items) {
            var rows = [];
            var pageItems = getCurrentPageItems(items);
            if (!pageItems.length) {
                rows.push('<tr><td colspan="6">暂无告警数据</td></tr>');
            } else {
                $.each(pageItems, function (_, item) {
                    var levelClass = getAlarmLevelClass(item.alarm_status);
                    var processClass = item.process_status === '已处理' ? 'alarm_process_done' : 'alarm_process_pending';
                    rows.push(
                        '<tr class="alarm_row" data-log-id="' + escapeHtml(item.log_id || '') + '">'
                        + '<td>' + escapeHtml(item.alarm_id || '--') + '</td>'
                        + '<td>' + escapeHtml(item.rule_name || '--') + '</td>'
                        + '<td>' + escapeHtml(item.alarm_time || '--') + '</td>'
                        + '<td><span class="alarm_level_badge ' + levelClass + '">' + escapeHtml(item.alarm_status || '--') + '</span></td>'
                        + '<td><span class="alarm_process_badge ' + processClass + '">' + escapeHtml(item.process_status || '未处理') + '</span></td>'
                        + '<td><button type="button" class="device_action_btn alarm_detail_btn" data-log-id="' + escapeHtml(item.log_id || '') + '">详情</button></td>'
                        + '</tr>'
                    );
                });
            }
            $('#alarm_table_body').html(rows.join(''));
            renderPager(items.length);
        }

        function processAlarm(logId) {
            $.ajax({
                url: '/api/alarm-process',
                method: 'POST',
                contentType: 'application/json; charset=utf-8',
                data: JSON.stringify({ log_id: logId })
            }).then(function (res) {
                if (!res || res.code !== 0) {
                    return;
                }
                updateAlarmItemFromDetail(logId, res.data);
                renderAlarmRows(state.items);
                if (state.currentDetailLogId === logId) {
                    openAlarmDetail(res.data);
                }
            }).fail(function (xhr) {
                console.error('处理告警失败:', xhr);
            });
        }

        function loadAlarmDetail(logId) {
            $.ajax({
                url: '/api/alarm-detail',
                method: 'GET',
                data: { log_id: logId }
            }).then(function (res) {
                if (!res || res.code !== 0) {
                    return;
                }
                openAlarmDetail(res.data);
            }).fail(function (xhr) {
                console.error('获取告警详情失败:', xhr);
            });
        }

        function openAlarmDetail(detail) {
            var current = (detail && detail.current) || {};
            state.currentDetailLogId = current.log_id || '';
            $('#alarm_detail_summary').html(
                '告警设备：' + escapeHtml(current.alarm_id || '--')
                + '<br>告警类型：' + escapeHtml(current.rule_name || '--')
                + '<br>告警等级：' + escapeHtml(current.alarm_status || '--')
                + '<br>处理状态：' + escapeHtml(current.process_status || '未处理')
                + '<br>告警时间：' + escapeHtml(current.alarm_time || '--')
                + '<br>最新数值：' + escapeHtml(current.metric_value || '--')
            );
            $('#alarm_process_records').html(renderProcessRecords(current.process_records || []));
            $('#alarm_history_records').html(renderHistoryRecords((detail && detail.history) || []));
            $('#alarm_detail_modal').removeClass('hidden');
        }

        function renderProcessRecords(records) {
            if (!records.length) {
                return '<div class="alarm_detail_item">暂无处理记录</div>';
            }
            return $.map(records, function (item) {
                return '<div class="alarm_detail_item">'
                    + '处理时间：' + escapeHtml(item.time || '--')
                    + '<br>处理动作：' + escapeHtml(item.action || '--')
                    + '<br>处理人：' + escapeHtml(item.operator || '--')
                    + '<br>说明：' + escapeHtml(item.note || '--')
                    + '</div>';
            }).join('');
        }

        function renderHistoryRecords(records) {
            if (!records.length) {
                return '<div class="alarm_detail_item">暂无历史告警</div>';
            }
            return $.map(records, function (item) {
                return '<div class="alarm_detail_item">'
                    + '告警时间：' + escapeHtml(item.alarm_time || '--')
                    + '<br>告警等级：' + escapeHtml(item.alarm_status || '--')
                    + '<br>处理状态：' + escapeHtml(item.process_status || '--')
                    + '<br>监测值：' + escapeHtml(item.metric_value || '--')
                    + '</div>';
            }).join('');
        }

        function updateAlarmItemFromDetail(logId, detail) {
            var current = (detail && detail.current) || {};
            $.each(state.items, function (index, item) {
                if (item.log_id === logId) {
                    state.items[index] = $.extend({}, item, current);
                    return false;
                }
            });
        }

        function getAlarmLevelClass(level) {
            if (level === '紧急') {
                return 'alarm_level_emergency';
            }
            if (level === '重要') {
                return 'alarm_level_important';
            }
            if (level === '次要') {
                return 'alarm_level_minor';
            }
            return 'alarm_level_notice';
        }

        function showAlarmPopup(items, activeItems) {
            var textList = [];
            var sourceItems = items;
            if (!sourceItems.length && !state.activeToastShown && activeItems && activeItems.length) {
                sourceItems = activeItems;
            }
            if (!sourceItems.length) {
                return;
            }
            $.each(sourceItems, function (_, item) {
                textList.push((item.alarm_id || '--') + ' ' + (item.rule_name || '--') + '报警');
            });
            state.activeToastShown = true;
            showAlarmToast(textList.join('；'), 'red');
        }

        function showAlarmToast(text, color) {
            var $toast = $('#alarm_toast');
            if (!text) {
                return;
            }
            $toast.removeClass('hidden');
            $toast.find('.alarm_notice_inner')
                .toggleClass('alarm_notice_inner_red', color === 'red')
                .toggleClass('alarm_notice_inner_blue', color !== 'red');
            $('#alarm_toast_text').text(text);
        }

        function changePage(step) {
            var totalPages = getTotalPages();
            if (totalPages <= 1) {
                state.pageIndex = 1;
                renderAlarmRows(state.items);
                return;
            }
            state.pageIndex += step;
            if (state.pageIndex < 1) {
                state.pageIndex = 1;
            }
            if (state.pageIndex > totalPages) {
                state.pageIndex = totalPages;
            }
            renderAlarmRows(state.items);
        }

        function getCurrentPageItems(items) {
            var list = items || [];
            var start = (state.pageIndex - 1) * state.pageSize;
            return list.slice(start, start + state.pageSize);
        }

        function getTotalPages() {
            return Math.max(1, Math.ceil((state.items || []).length / state.pageSize));
        }

        function ensurePageInRange() {
            var totalPages = getTotalPages();
            if (state.pageIndex > totalPages) {
                state.pageIndex = totalPages;
            }
            if (state.pageIndex < 1) {
                state.pageIndex = 1;
            }
        }

        function renderPager(totalCount) {
            var totalPages = Math.max(1, Math.ceil(totalCount / state.pageSize));
            $('#alarm_page_info').text(state.pageIndex + ' / ' + totalPages);
            $('#alarm_prev_btn').prop('disabled', state.pageIndex <= 1);
            $('#alarm_next_btn').prop('disabled', state.pageIndex >= totalPages);
        }

        function escapeHtml(text) {
            return String(text || '')
                .replace(/&/g, '&amp;')
                .replace(/</g, '&lt;')
                .replace(/>/g, '&gt;')
                .replace(/"/g, '&quot;')
                .replace(/'/g, '&#39;');
        }
    }

    /*青岛研锦网络科技有限公司   版权所有*/
    function echart_1() {
        // 基于准备好的dom，初始化echarts实例
        var myChart = echarts.init(document.getElementById('chart_1'));
        option = {
            title: {
                text: '本月设备状态统计',
                top: 35,
                left: 20,
                textStyle: {
                    fontSize: 18,
                    color: '#fff'
                }
            },
            tooltip: {
                trigger: 'item',
                formatter: "{a} <br/>{b}: {c} ({d}%)",

            },
            legend: {
                right: 20,
                top: 35,
                data: ['故障', '正常'],
                textStyle: {
                    color: '#fff'
                }
            },
            series: [{
                name: '设备状态',
                type: 'pie',
                radius: ['0', '60%'],
                center: ['50%', '60%'],
                color: ['#e72325', '#98e002', '#2ca3fd'],
                label: {
                    normal: {
                        formatter: '{b}\n{d}%'
                    },

                },
                data: [{
                        value: 6,
                        name: '故障'
                    },
                    {
                        value: 50,
                        name: '正常',
                        selected: true
                    }
                ]
            }]
        };
        // 使用刚指定的配置项和数据显示图表。
        myChart.setOption(option);
        window.addEventListener("resize", function () {
            myChart.resize();
        });
    }
    /*青岛研锦网络科技有限公司   版权所有*/
    function echart_2() {
        var myChart = echarts.init(document.getElementById('chart_2'));
        var forceExcelMode = false;

        fetchStatusTrend();

        $(document).on('device-force-excel-changed', function (_, enabled) {
            forceExcelMode = !!enabled;
            fetchStatusTrend();
        });

        setInterval(function () {
            fetchStatusTrend();
        }, 30000);

        function fetchStatusTrend() {
            $.ajax({
                url: '/api/status-trend',
                method: 'GET',
                data: {
                    force_excel: forceExcelMode ? 1 : 0
                }
            }).then(function (res) {
                if (!res || res.code !== 0 || !res.data) {
                    return;
                }
                renderStatusTrend(res.data);
            }).fail(function (xhr) {
                console.error('获取最近五天在线统计失败:', xhr);
            });
        }

        function renderStatusTrend(data) {
            var items = data.items || [];
            var today = data.today || {};
            var xAxisData = [];
            var onlineData = [];
            var offlineData = [];

            $.each(items, function (_, item) {
                xAxisData.push(item.label || item.date || '--');
                onlineData.push(Number(item.online_count) || 0);
                offlineData.push(Number(item.offline_count) || 0);
            });

            myChart.setOption({
                title: {
                    show: true,
                    top: '10%',
                    left: '3%',
                    text: '最近五天在线统计',
                    textStyle: {
                        fontSize: 18,
                        color: '#fff'
                    }
                },
                tooltip: {
                    trigger: 'axis',
                    formatter: function (params) {
                        var lines = [params[0].name];
                        $.each(params, function (_, item) {
                            lines.push(item.seriesName + '：' + item.value);
                        });
                        if (params.length && params[0].axisValue === xAxisData[xAxisData.length - 1]) {
                            lines.push('今日总设备：' + (today.total_devices || 0));
                        }
                        return lines.join('<br/>');
                    },
                    axisPointer: {
                        type: 'shadow'
                    }
                },
                legend: {
                    top: '12%',
                    right: '5%',
                    itemGap: 16,
                    itemWidth: 10,
                    itemHeight: 10,
                    data: ['在线机数', '离线机数'],
                    textStyle: {
                        color: '#fff',
                        fontStyle: 'normal',
                        fontFamily: '微软雅黑',
                        fontSize: 12
                    }
                },
                grid: {
                    x: 30,
                    y: 80,
                    x2: 30,
                    y2: 45
                },
                xAxis: {
                    type: 'category',
                    data: xAxisData,
                    axisTick: {
                        show: false
                    },
                    axisLine: {
                        show: true,
                        lineStyle: {
                            color: '#1AA1FD'
                        },
                        symbol: ['none', 'arrow']
                    },
                    axisLabel: {
                        show: true,
                        interval: 0,
                        color: '#1AA1FD',
                        fontSize: 12
                    }
                },
                yAxis: {
                    axisLine: {
                        show: true,
                        lineStyle: {
                            color: '#1AA1FD'
                        },
                        symbol: ['none', 'arrow']
                    },
                    type: 'value',
                    axisTick: {
                        show: false
                    },
                    axisLabel: {
                        show: true,
                        color: '#fff'
                    },
                    splitLine: {
                        show: false
                    }
                },
                series: [{
                    name: '在线机数',
                    type: 'bar',
                    data: onlineData,
                    barWidth: 12,
                    itemStyle: {
                        normal: {
                            barBorderRadius: 4,
                            color: '#3FA7DC'
                        }
                    },
                    label: {
                        normal: {
                            show: true,
                            position: 'top',
                            color: '#fff'
                        }
                    }
                }, {
                    name: '离线机数',
                    type: 'bar',
                    data: offlineData,
                    barWidth: 12,
                    itemStyle: {
                        normal: {
                            barBorderRadius: 4,
                            color: '#7091C4'
                        }
                    },
                    label: {
                        normal: {
                            show: true,
                            position: 'top',
                            color: '#fff'
                        }
                    }
                }]
            }, true);
        }

        window.addEventListener("resize", function () {
            myChart.resize();
        });
    }

    function echart_3() {
        var myChart = echarts.init(document.getElementById('chart_3'));
        var state = {
            viewMode: 'weather',
            devices: [],
            selectedSlotIndex: 1,
            selectedRecordId: '',
            forceExcelMode: false
        };
        var slotPositions = [
            { left: 12, top: 18 }, { left: 29, top: 18 }, { left: 46, top: 18 }, { left: 63, top: 18 }, { left: 80, top: 18 },
            { left: 12, top: 38 }, { left: 29, top: 38 }, { left: 46, top: 38 }, { left: 63, top: 38 }, { left: 80, top: 38 },
            { left: 12, top: 58 }, { left: 29, top: 58 }, { left: 46, top: 58 }, { left: 63, top: 58 }, { left: 80, top: 58 },
            { left: 12, top: 78 }, { left: 29, top: 78 }, { left: 46, top: 78 }, { left: 63, top: 78 }, { left: 80, top: 78 }
        ];

        bindViewEvents();
        fetchWeatherAndRender();
        loadMapDevices();

        $(document).on('device-list-updated', function (_, devices, extra) {
            state.devices = devices || [];
            if (extra && typeof extra.forceExcelMode !== 'undefined') {
                state.forceExcelMode = !!extra.forceExcelMode;
            }
            ensureSelectedSlot();
            renderMapSlots();
            refreshSelectedSlot(true);
        });

        $(document).on('device-force-excel-changed', function (_, enabled) {
            state.forceExcelMode = !!enabled;
            loadMapDevices();
        });

        window.addEventListener("resize", function () {
            myChart.resize();
        });

        function bindViewEvents() {
            $('#weather_view_btn').on('click', function () {
                switchView('weather');
            });
            $('#rcs_view_btn').on('click', function () {
                switchView('rcs');
            });
            $('#rcs_slot_layer').on('click', '.rcs_slot', function () {
                state.selectedSlotIndex = Number($(this).data('slotIndex')) || 1;
                state.selectedRecordId = $(this).data('recordId') || '';
                renderMapSlots();
                refreshSelectedSlot(true);
            });
            $('#rcs_add_btn').on('click', function () {
                $(document).trigger('rcs-slot-add', [state.selectedSlotIndex]);
            });
            $('#rcs_edit_btn').on('click', function () {
                if (state.selectedRecordId) {
                    $(document).trigger('rcs-device-edit', [state.selectedRecordId]);
                }
            });
            $('#rcs_delete_btn').on('click', function () {
                if (state.selectedRecordId) {
                    $(document).trigger('rcs-device-delete', [state.selectedRecordId]);
                }
            });
        }

        function switchView(mode) {
            state.viewMode = mode;
            $('#weather_view').toggleClass('hidden', mode !== 'weather');
            $('#rcs_map_view').toggleClass('hidden', mode !== 'rcs');
            $('#weather_view_btn').toggleClass('force_btn', mode === 'weather');
            $('#rcs_view_btn').toggleClass('force_btn', mode === 'rcs');
            if (mode === 'weather') {
                myChart.resize();
            } else {
                renderMapSlots();
                refreshSelectedSlot(true);
            }
        }

        function fetchWeatherAndRender() {
            $.ajax({
                url: '/api/weather',
                method: 'GET'
            }).then(function (res) {
                if (!res || res.code !== 0 || !res.data || !res.data.forecast) {
                    console.error('天气数据加载失败', res);
                    return;
                }

                var forecast = res.data.forecast.slice(0, 5);

                if (forecast.length > 0) {
                    $('#metric_weather_today').text(forecast[0].type);
                }

                var xData = [];
                var highData = [];
                var lowData = [];

                $.each(forecast, function (index, day) {
                    xData.push(day.date + '日\n' + day.type);
                    var highTemp = parseInt(day.high.replace(/[^0-9-]/ig, ''), 10);
                    var lowTemp = parseInt(day.low.replace(/[^0-9-]/ig, ''), 10);
                    highData.push(highTemp);
                    lowData.push(lowTemp);
                });

                renderWeatherChart(xData, highData, lowData);
            }).fail(function (xhr) {
                console.error('天气数据请求失败', xhr);
            });
        }

        function renderWeatherChart(xData, highData, lowData) {
            var option = {
                title: {
                    text: '5天天气预报',
                    x: 'center',
                    textStyle: {
                        color: '#FFF',
                        fontSize: 16
                    },
                    top: '10%'
                },
                tooltip: {
                    trigger: 'axis',
                    formatter: function (params) {
                        var html = params[0].name.replace('\n', ' ') + '<br/>';
                        for (var i = 0; i < params.length; i++) {
                            html += params[i].seriesName + ': ' + params[i].value + '℃<br/>';
                        }
                        return html;
                    }
                },
                legend: {
                    data: ['高温', '低温'],
                    top: '10%',
                    right: '5%',
                    textStyle: {
                        color: '#fff'
                    }
                },
                grid: {
                    top: '30%',
                    left: '10%',
                    right: '10%',
                    bottom: '15%',
                    containLabel: true
                },
                xAxis: {
                    type: 'category',
                    boundaryGap: false,
                    data: xData,
                    axisLine: {
                        lineStyle: {
                            color: '#1AA1FD'
                        }
                    },
                    axisLabel: {
                        textStyle: {
                            color: '#fff',
                            fontSize: 12
                        },
                        margin: 15
                    }
                },
                yAxis: {
                    type: 'value',
                    axisLine: {
                        show: false
                    },
                    axisTick: {
                        show: false
                    },
                    splitLine: {
                        lineStyle: {
                            color: 'rgba(26, 161, 253, 0.2)',
                            type: 'dashed'
                        }
                    },
                    axisLabel: {
                        textStyle: {
                            color: '#fff'
                        },
                        formatter: '{value} ℃'
                    }
                },
                series: [
                    {
                        name: '高温',
                        type: 'line',
                        data: highData,
                        smooth: true,
                        symbol: 'circle',
                        symbolSize: 8,
                        itemStyle: {
                            normal: {
                                color: '#F57474',
                                lineStyle: {
                                    width: 3
                                }
                            }
                        },
                        label: {
                            normal: {
                                show: true,
                                position: 'top',
                                formatter: '{c}℃',
                                textStyle: {
                                    color: '#fff'
                                }
                            }
                        }
                    },
                    {
                        name: '低温',
                        type: 'line',
                        data: lowData,
                        smooth: true,
                        symbol: 'circle',
                        symbolSize: 8,
                        itemStyle: {
                            normal: {
                                color: '#1089E7',
                                lineStyle: {
                                    width: 3
                                }
                            }
                        },
                        label: {
                            normal: {
                                show: true,
                                position: 'bottom',
                                formatter: '{c}℃',
                                textStyle: {
                                    color: '#fff'
                                }
                            }
                        }
                    }
                ]
            };
            myChart.setOption(option, true);
        }

        function loadMapDevices() {
            $.ajax({
                url: '/api/devices',
                method: 'GET',
                data: {
                    force_excel: state.forceExcelMode ? 1 : 0
                }
            }).then(function (res) {
                if (!res || res.code !== 0) {
                    return;
                }
                state.devices = (res.data && res.data.devices) || [];
                ensureSelectedSlot();
                renderMapSlots();
                refreshSelectedSlot(true);
            }).fail(function (xhr) {
                console.error('RCS地图设备加载失败:', xhr);
            });
        }

        function ensureSelectedSlot() {
            var slotMap = buildSlotMap();
            if (!slotMap[state.selectedSlotIndex]) {
                var firstDevice = state.devices[0];
                if (firstDevice && Number(firstDevice.slot_index)) {
                    state.selectedSlotIndex = Number(firstDevice.slot_index);
                    state.selectedRecordId = firstDevice.record_id || '';
                    return;
                }
            }
            state.selectedRecordId = slotMap[state.selectedSlotIndex] ? slotMap[state.selectedSlotIndex].record_id : '';
        }

        function buildSlotMap() {
            var slotMap = {};
            $.each(state.devices, function (_, device) {
                var slotIndex = Number(device.slot_index) || 0;
                if (slotIndex >= 1 && slotIndex <= 20) {
                    slotMap[slotIndex] = device;
                }
            });
            return slotMap;
        }

        function renderMapSlots() {
            var slotMap = buildSlotMap();
            var html = [];
            $.each(slotPositions, function (index, position) {
                var slotIndex = index + 1;
                var device = slotMap[slotIndex];
                var statusClass = 'rcs_slot_empty';
                var statusText = '空位';
                var deviceName = '空位';
                var recordId = '';
                if (device) {
                    recordId = device.record_id || '';
                    deviceName = device.name || device.device_name || ('设备' + slotIndex);
                    if (device.online === true) {
                        statusClass = 'rcs_slot_online';
                        statusText = '在线';
                    } else if (device.online === false) {
                        statusClass = 'rcs_slot_offline';
                        statusText = '离线';
                    } else {
                        statusClass = 'rcs_slot_unknown';
                        statusText = '未知';
                    }
                }
                html.push(
                    '<button type="button" class="rcs_slot ' + statusClass + (state.selectedSlotIndex === slotIndex ? ' rcs_slot_active' : '') + '"'
                    + ' data-slot-index="' + slotIndex + '" data-record-id="' + escapeHtml(recordId) + '"'
                    + ' style="left:' + position.left + '%;top:' + position.top + '%;">'
                    + '<span class="rcs_slot_dot"></span>'
                    + '<span class="rcs_slot_index">' + slotIndex + '号位</span>'
                    + '<span class="rcs_slot_name">' + escapeHtml(deviceName) + '</span>'
                    + '<span class="hidden">' + statusText + '</span>'
                    + '</button>'
                );
            });
            $('#rcs_slot_layer').html(html.join(''));
        }

        function refreshSelectedSlot(needFetch) {
            var device = buildSlotMap()[state.selectedSlotIndex];
            if (!device) {
                state.selectedRecordId = '';
                renderEmptySlotDetail();
                return;
            }
            state.selectedRecordId = device.record_id || '';
            renderDeviceBaseDetail(device);
            if (needFetch === false) {
                return;
            }
            loadSlotDeviceProperties(device);
        }

        function renderEmptySlotDetail() {
            $('#rcs_slot_title').text('当前为 ' + state.selectedSlotIndex + ' 号空位');
            $('#rcs_slot_state').text('空位');
            $('#rcs_device_name').text('--');
            $('#rcs_device_id').text('--');
            $('#rcs_device_ip').text('--');
            $('#rcs_device_temp').text('--');
            $('#rcs_device_humi').text('--');
            $('#rcs_device_smoke').text('--');
            $('#rcs_detail_tip').text('点击“新增到此”后，将直接把新设备绑定到当前空位。');
            $('#rcs_add_btn').removeClass('hidden');
            $('#rcs_edit_btn, #rcs_delete_btn').addClass('hidden');
        }

        function renderDeviceBaseDetail(device) {
            $('#rcs_slot_title').text((device.slot_index || state.selectedSlotIndex) + ' 号槽位');
            $('#rcs_slot_state').text(getDeviceStateText(device));
            $('#rcs_device_name').text(device.name || device.device_name || '--');
            $('#rcs_device_id').text(device.id || '--');
            $('#rcs_device_ip').text(device.ip || '--');
            $('#rcs_device_temp').text('加载中...');
            $('#rcs_device_humi').text('加载中...');
            $('#rcs_device_smoke').text('加载中...');
            $('#rcs_detail_tip').text('当前设备已绑定到此槽位，可在地图中直接修改或删减。');
            $('#rcs_add_btn').addClass('hidden');
            $('#rcs_edit_btn, #rcs_delete_btn').removeClass('hidden');
        }

        function loadSlotDeviceProperties(device) {
            var recordId = device.record_id;
            $.ajax({
                url: '/api/device-properties',
                method: 'GET',
                data: {
                    record_id: recordId,
                    force_excel: state.forceExcelMode ? 1 : 0
                }
            }).then(function (res) {
                if (!res || res.code !== 0 || state.selectedRecordId !== recordId) {
                    return;
                }
                var data = res.data || {};
                $('#rcs_device_temp').text(formatMetricValue(data.temp, '℃'));
                $('#rcs_device_humi').text(formatMetricValue(data.humi, '%'));
                $('#rcs_device_smoke').text(formatMetricValue(data.smoke, 'ppm'));
                $('#rcs_slot_state').text(data.status === 'true' ? '在线' : '离线');
            }).fail(function (xhr) {
                console.error('获取RCS地图设备属性失败:', xhr);
                if (state.selectedRecordId === recordId) {
                    $('#rcs_device_temp').text('获取失败');
                    $('#rcs_device_humi').text('获取失败');
                    $('#rcs_device_smoke').text('获取失败');
                }
            });
        }

        function getDeviceStateText(device) {
            if (!device) {
                return '空位';
            }
            if (device.online === true) {
                return '在线';
            }
            if (device.online === false) {
                return '离线';
            }
            return '未知';
        }

        function formatMetricValue(value, unit) {
            if (value === undefined || value === null || value === '') {
                return '--';
            }
            return value + unit;
        }

        function escapeHtml(text) {
            return String(text || '')
                .replace(/&/g, '&amp;')
                .replace(/</g, '&lt;')
                .replace(/>/g, '&gt;')
                .replace(/"/g, '&quot;')
                .replace(/'/g, '&#39;');
        }
    }

    function echart_4() {
        // 基于准备好的dom，初始化echarts实例
        var myChart = echarts.init(document.getElementById('chart_4'));
        var myColor = ['#1089E7', '#F57474', '#56D0E3', '#F8B448', '#8B78F6'];
        var state = {
            devices: [],
            selectedIndex: 0,
            timer: null,
            forceExcelMode: false,
            modalMode: 'add',
            editingRecordId: '',
            toastTimer: null,
            weatherTimer: null
        };

        bindActionEvents();
        initDevicePanel();

        myChart.on('click', function (params) {
            if (typeof params.dataIndex === 'number') {
                state.selectedIndex = params.dataIndex;
                syncCurrentDevice();
            }
        });
        myChart.on('dblclick', function (params) {
            if (typeof params.dataIndex === 'number') {
                state.selectedIndex = params.dataIndex;
                openModal('edit', state.devices[params.dataIndex]);
            }
        });

        window.addEventListener("resize", function () {
            myChart.resize();
        });

        function initDevicePanel() {
            setMetricText('--', '--', '--', '未知');
            loadDeviceList().then(function (devices) {
                if (devices.length) {
                    syncCurrentDevice();
                }
                startPolling();
            }, function (error) {
                handleLoadError(error);
            });
            loadMetrics();
        }

        function loadMetrics() {
            $.ajax({
                url: '/api/metrics',
                method: 'GET',
                data: {
                    force_excel: state.forceExcelMode ? 1 : 0
                }
            }).then(function (res) {
                if (!res || res.code !== 0) {
                    return;
                }
                var data = res.data || {};
                $('#metric_error_count').text(data.error_count !== undefined ? data.error_count : '--');
                $('#metric_new_devices').text(data.new_devices_this_month !== undefined ? data.new_devices_this_month : '--');
                $('#metric_online_devices_1').text(data.online_devices !== undefined ? data.online_devices : '--');
                $('#metric_online_devices_2').text(data.online_devices !== undefined ? data.online_devices : '--');
                $('#metric_total_devices').text(data.total_devices !== undefined ? data.total_devices : '--');
            }).fail(function (xhr) {
                console.error('获取监控指标失败:', xhr);
            });
        }

        function startPolling() {
            if (state.timer) {
                clearInterval(state.timer);
            }
            state.timer = setInterval(function () {
                loadMetrics();
                loadDeviceList({
                    silentStorageStatus: true
                }).then(function (devices) {
                    if (!devices.length) {
                        resetCurrentDevicePanel();
                        return;
                    }
                    syncCurrentDevice();
                }, function (error) {
                    console.error('轮询刷新设备列表失败:', error);
                });
            }, 30000);
        }

        function loadDeviceList(options) {
            options = options || {};
            return $.ajax({
                url: '/api/devices',
                method: 'GET',
                data: {
                    force_excel: state.forceExcelMode ? 1 : 0
                }
            }).then(function (res) {
                if (!res || res.code !== 0) {
                    return $.Deferred().reject(new Error((res && res.msg) || '设备列表加载失败')).promise();
                }
                state.devices = (res.data && res.data.devices) || [];
                if (state.selectedIndex >= state.devices.length) {
                    state.selectedIndex = 0;
                }
                renderUsageChart(state.devices);
                updateDeleteSelect();
                if (!options.silentStorageStatus) {
                    applyStorageStatus(res.data && res.data.storage);
                }
                if (!state.devices.length) {
                    resetCurrentDevicePanel();
                }
                triggerDeviceListUpdated();
                return state.devices;
            });
        }

        function syncCurrentDevice() {
            var currentDevice = state.devices[state.selectedIndex];
            if (!currentDevice) {
                return;
            }
            syncPanelBaseInfo(currentDevice);
            setMetricText('加载中...', '加载中...', '加载中...', currentDevice.online ? '在线' : '离线');

            fetchDeviceProperty(currentDevice.record_id).then(function (propertyMap) {
                currentDevice.online = propertyMap.status === 'true';
                currentDevice.id = propertyMap.device_id || currentDevice.id;
                currentDevice.ip = propertyMap.ip || currentDevice.ip;
                renderUsageChart(state.devices);
                triggerDeviceListUpdated();
                syncPanelBaseInfo(currentDevice);
                setMetricText(
                    formatMetric(propertyMap.temp, '℃'),
                    formatMetric(propertyMap.humi, '%'),
                    formatMetric(propertyMap.smoke, 'ppm'),
                    currentDevice.online ? '在线' : '离线'
                );
            }, function (error) {
                console.error('获取设备属性失败:', error);
                setMetricText('获取失败', '获取失败', '获取失败', currentDevice.online ? '在线' : '未知');
            });
        }

        function fetchDeviceProperty(recordId) {
            return $.ajax({
                url: '/api/device-properties',
                method: 'GET',
                data: {
                    record_id: recordId,
                    force_excel: state.forceExcelMode ? 1 : 0
                }
            }).then(function (res) {
                if (!res || res.code !== 0) {
                    return $.Deferred().reject(new Error((res && res.msg) || '设备属性获取失败')).promise();
                }
                return res.data || {};
            });
        }

        function renderUsageChart(devices) {
            var totalStarts = getTotalStarts(devices);
            var titleData = [];
            var valueData = [];
            var percentData = [];
            var borderData = [];
            var statusFlags = [];

            $.each(devices, function (_, device) {
                var isOnline = !!device.online;
                titleData.push(device.id + ' ' + device.name + (isOnline ? '' : ' [离线]'));
                valueData.push(device.starts);
                percentData.push(totalStarts ? Number((device.starts / totalStarts * 100).toFixed(2)) : 0);
                borderData.push(100);
                statusFlags.push(isOnline);
            });

            $('#total_starts').html(totalStarts + '<span>次</span>');

            myChart.setOption({
                title: {
                    text: '设备使用频率',
                    x: 'center',
                    textStyle: {
                        color: '#FFF'
                    },
                    left: '6%',
                    top: '10%'
                },
                grid: {
                    top: '20%',
                    left: '32%'
                },
                xAxis: {
                    show: false
                },
                yAxis: [{
                    show: true,
                    data: titleData,
                    inverse: true,
                    axisLine: {
                        show: false
                    },
                    splitLine: {
                        show: false
                    },
                    axisTick: {
                        show: false
                    },
                    axisLabel: {
                        color: '#fff',
                        formatter: function (value, index) {
                            return ['{lg|' + (index + 1) + '}  ' + '{title|' + value + '} '].join('\n');
                        },
                        rich: {
                            lg: {
                                backgroundColor: '#339911',
                                color: '#fff',
                                borderRadius: 15,
                                align: 'center',
                                width: 15,
                                height: 15
                            }
                        }
                    }
                }, {
                    show: true,
                    inverse: true,
                    data: valueData,
                    axisLabel: {
                        textStyle: {
                            fontSize: 12,
                            color: '#fff'
                        }
                    },
                    axisLine: {
                        show: false
                    },
                    splitLine: {
                        show: false
                    },
                    axisTick: {
                        show: false
                    }
                }],
                series: [{
                    name: '条',
                    type: 'bar',
                    yAxisIndex: 0,
                    data: percentData,
                    barWidth: 10,
                    itemStyle: {
                        normal: {
                            barBorderRadius: 20,
                            color: function (params) {
                                if (!statusFlags[params.dataIndex]) {
                                    return '#6c7a89';
                                }
                                return myColor[params.dataIndex % myColor.length];
                            }
                        }
                    },
                    label: {
                        normal: {
                            show: true,
                            position: 'inside',
                            formatter: '{c}%'
                        }
                    }
                }, {
                    name: '框',
                    type: 'bar',
                    yAxisIndex: 1,
                    barGap: '-100%',
                    data: borderData,
                    barWidth: 15,
                    itemStyle: {
                        normal: {
                            color: 'none',
                            borderColor: '#00c1de',
                            borderWidth: 3,
                            barBorderRadius: 15
                        }
                    }
                }]
            }, true);
        }

        function getTotalStarts(devices) {
            var total = 0;
            $.each(devices, function (_, device) {
                total += Number(device.starts) || 0;
            });
            return total;
        }

        function syncPanelBaseInfo(device) {
            $('#dev_ip').text(device.ip || '未配置');
            $('#dev_name').text(device.name || '--');
            $('#dev_id').text(device.id || '--');
        }

        function setMetricText(temp, humi, smoke, online) {
            $('#dev_temp').text(temp);
            $('#dev_humi').text(humi);
            $('#dev_smoke').text(smoke);
            $('#dev_online').text(online);
        }

        function formatMetric(value, unit) {
            if (value === undefined || value === null || value === '') {
                return '--';
            }
            return value + unit;
        }

        function bindActionEvents() {
            $(document).on('rcs-slot-add', function (_, slotIndex) {
                openModal('add', {
                    slot_index: slotIndex
                });
            });
            $(document).on('rcs-device-edit', function (_, recordId) {
                var device = findDeviceByRecordId(recordId);
                if (device) {
                    openModal('edit', device);
                }
            });
            $(document).on('rcs-device-delete', function (_, recordId) {
                openDeleteForRecord(recordId);
            });

            $('#add_device_btn').on('click', function () {
                openModal('add');
            });

            $('#delete_device_btn').on('click', function () {
                openModal('delete');
            });

            $('#force_excel_btn').on('click', function () {
                state.forceExcelMode = true;
                $('#force_excel_btn').text('已强制本地');
                showToast('已切换本地数据模式', 'blue');
                $(document).trigger('device-force-excel-changed', [state.forceExcelMode]);
                loadMetrics();
                loadDeviceList().then(function (devices) {
                    if (devices.length) {
                        syncCurrentDevice();
                    }
                }, function (error) {
                    handleLoadError(error);
                });
            });

            $('#device_cancel_btn, .device_modal_mask').on('click', function () {
                closeModal();
            });

            $('#device_form').on('submit', function (event) {
                event.preventDefault();
                if (state.modalMode === 'delete') {
                    submitDeleteDevice();
                    return;
                }
                submitSaveDevice();
            });
        }

        function openModal(mode, device) {
            state.modalMode = mode;
            $('#device_modal').removeClass('hidden');
            if (mode === 'delete') {
                state.editingRecordId = '';
                $('#device_modal_title').text('删减设备');
                $('.device_form_grid').addClass('hidden');
                $('#delete_device_block').removeClass('hidden');
                $('#device_submit_btn').text('确认删减');
                updateDeleteSelect();
                if (device && device.record_id) {
                    $('#delete_device_select').val(device.record_id);
                }
            } else if (mode === 'edit') {
                state.editingRecordId = device && device.record_id ? device.record_id : '';
                $('#device_modal_title').text('修改设备');
                $('.device_form_grid').removeClass('hidden');
                $('#delete_device_block').addClass('hidden');
                $('#device_submit_btn').text('保存修改');
                fillEditForm(device);
            } else {
                state.editingRecordId = '';
                $('#device_modal_title').text('新增设备');
                $('.device_form_grid').removeClass('hidden');
                $('#delete_device_block').addClass('hidden');
                $('#device_submit_btn').text('确定');
                resetAddForm();
                if (device && device.slot_index) {
                    $('#slot_index').val(String(device.slot_index));
                }
            }
        }

        function closeModal() {
            $('#device_modal').addClass('hidden');
            resetAddForm();
        }

        function resetAddForm() {
            $('#device_form')[0].reset();
            $('#device_record_id').val('');
            $('#auth_version').val('2020-05-29');
            $('#start_success_count').val('1');
            $('#slot_index').val('');
        }

        function fillEditForm(device) {
            resetAddForm();
            if (!device) {
                return;
            }
            var raw = findRawDevice(device.record_id);
            $('#device_record_id').val(raw.record_id || '');
            $('#display_name').val(raw.display_name || device.name || '');
            $('#device_ip').val(raw.ip || device.ip || '');
            $('#start_success_count').val(raw.start_success_count !== undefined ? raw.start_success_count : (device.starts || 0));
            $('#slot_index').val(raw.slot_index !== undefined && raw.slot_index !== null && raw.slot_index !== '' ? raw.slot_index : (device.slot_index || ''));
            $('#onenet_device_name').val(raw.onenet_device_name || device.device_name || '');
            $('#product_id').val(raw.product_id || '');
            $('#user_id').val(raw.user_id || '');
            $('#access_key').val(raw.access_key || '');
            $('#auth_version').val(raw.auth_version || '2020-05-29');
            $('#device_secret').val(raw.device_secret || '');
            $('#device_id_input').val(raw.device_id || device.id || '');
            $('#device_notes').val(raw.notes || '');
        }

        function updateDeleteSelect() {
            var options = [];
            $.each(state.devices, function (_, device) {
                options.push(
                    '<option value="' + escapeHtml(device.record_id) + '">'
                    + escapeHtml((device.id || '--') + ' / ' + (device.name || device.device_name || '--'))
                    + '</option>'
                );
            });
            $('#delete_device_select').html(options.join(''));
        }

        function submitSaveDevice() {
            var payload = getFormPayload();
            var isEdit = state.modalMode === 'edit' && state.editingRecordId;
            $.ajax({
                url: isEdit ? '/api/devices/' + encodeURIComponent(state.editingRecordId) : '/api/devices',
                method: isEdit ? 'PUT' : 'POST',
                contentType: 'application/json; charset=utf-8',
                data: JSON.stringify(payload)
            }).then(function (res) {
                if (!res || res.code !== 0) {
                    showToast((res && res.msg) || (isEdit ? '修改设备失败' : '新增设备失败'), 'blue');
                    return;
                }
                closeModal();
                showToast(res.msg || (isEdit ? '设备已更新' : '设备已保存'), getToastColor(res.data && res.data.storage));
                loadMetrics();
                loadDeviceList().then(function () {
                    if (isEdit) {
                        state.selectedIndex = findDeviceIndex(state.editingRecordId);
                    } else {
                        state.selectedIndex = state.devices.length ? state.devices.length - 1 : 0;
                    }
                    if (state.devices.length) {
                        syncCurrentDevice();
                    }
                }, function (error) {
                    handleLoadError(error);
                });
            }).fail(function (xhr) {
                showToast(parseXhrMessage(xhr, isEdit ? '修改设备失败' : '新增设备失败'), 'blue');
            });
        }

        function submitDeleteDevice() {
            var recordId = $('#delete_device_select').val();
            if (!recordId) {
                showToast('请先选择需要删减的设备', 'blue');
                return;
            }
            $.ajax({
                url: '/api/devices/' + encodeURIComponent(recordId),
                method: 'DELETE'
            }).then(function (res) {
                if (!res || res.code !== 0) {
                    showToast((res && res.msg) || '删减设备失败', 'blue');
                    return;
                }
                closeModal();
                state.selectedIndex = 0;
                showToast(res.msg || '设备已删减', getToastColor(res.data && res.data.storage));
                loadMetrics();
                loadDeviceList().then(function (devices) {
                    if (devices.length) {
                        syncCurrentDevice();
                    } else {
                        resetCurrentDevicePanel();
                    }
                }, function (error) {
                    handleLoadError(error);
                });
            }).fail(function (xhr) {
                showToast(parseXhrMessage(xhr, '删减设备失败'), 'blue');
            });
        }

        function getFormPayload() {
            var formData = {};
            $.each($('#device_form').serializeArray(), function (_, item) {
                formData[item.name] = $.trim(item.value);
            });
            return formData;
        }

        function findDeviceIndex(recordId) {
            var matchedIndex = 0;
            $.each(state.devices, function (index, device) {
                if (device.record_id === recordId) {
                    matchedIndex = index;
                    return false;
                }
            });
            return matchedIndex;
        }

        function findRawDevice(recordId) {
            var matched = null;
            $.each(state.devices, function (_, device) {
                if (device.record_id === recordId) {
                    matched = device.raw || {};
                    return false;
                }
            });
            return matched || {};
        }

        function findDeviceByRecordId(recordId) {
            var matched = null;
            $.each(state.devices, function (_, device) {
                if (device.record_id === recordId) {
                    matched = device;
                    return false;
                }
            });
            return matched;
        }

        function openDeleteForRecord(recordId) {
            var device = findDeviceByRecordId(recordId);
            openModal('delete', device || { record_id: recordId });
        }

        function triggerDeviceListUpdated() {
            $(document).trigger('device-list-updated', [state.devices, {
                forceExcelMode: state.forceExcelMode
            }]);
        }

        function applyStorageStatus(storage) {
            if (!storage) {
                return;
            }
            showToast(storage.toast_text, storage.toast_color);
        }

        function getToastColor(storage) {
            return storage && storage.toast_color ? storage.toast_color : 'blue';
        }

        function showToast(text, color) {
            var $toast = $('#device_toast');
            if (!text) {
                return;
            }
            $toast
                .removeClass('hidden device_toast_green device_toast_blue')
                .addClass(color === 'green' ? 'device_toast_green' : 'device_toast_blue')
                .text(text);
            if (state.toastTimer) {
                clearTimeout(state.toastTimer);
            }
            state.toastTimer = setTimeout(function () {
                $toast.addClass('hidden');
            }, 2600);
        }

        function resetCurrentDevicePanel() {
            $('#total_starts').html('0<span>次</span>');
            $('#dev_ip').text('--');
            $('#dev_name').text('--');
            $('#dev_id').text('--');
            setMetricText('--', '--', '--', '--');
        }

        function handleLoadError(error) {
            console.error('加载设备列表失败:', error);
            state.devices = [];
            renderUsageChart(state.devices);
            resetCurrentDevicePanel();
            updateDeleteSelect();
            triggerDeviceListUpdated();
            showToast('请先运行本地设备服务', 'blue');
        }

        function parseXhrMessage(xhr, fallbackText) {
            if (xhr && xhr.responseJSON && xhr.responseJSON.msg) {
                return xhr.responseJSON.msg;
            }
            return fallbackText;
        }

        function escapeHtml(text) {
            return String(text || '')
                .replace(/&/g, '&amp;')
                .replace(/</g, '&lt;')
                .replace(/>/g, '&gt;')
                .replace(/"/g, '&quot;')
                .replace(/'/g, '&#39;');
        }
    }
});
