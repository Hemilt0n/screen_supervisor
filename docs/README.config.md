# 配置详解

## 配置来源优先级
1. CLI 参数（例如 --config 指定文件）
2. 环境变量（SCREEN_SUP_*）
3. config.toml 文件
4. 默认值

## 字段说明
| 字段 | 类型 | 说明 |
| --- | --- | --- |
| interval_seconds | float | 截屏间隔，建议 ≥0.5 以避免堆积 |
| capture_root | str | 截图根目录，自动生成日期子目录 |
| image_format | str | 保存格式，如 png、jpg、webp |
| monitor_index | int | mss 中 monitors 的索引，0 代表整屏 |
| retention_days | int | 需要保留的最近天数，<=0 关闭自动清理 |
| log_level | str | DEBUG/INFO/WARNING/ERROR |

## 环境变量
- SCREEN_SUP_INTERVAL
- SCREEN_SUP_CAPTURE_ROOT
- SCREEN_SUP_IMAGE_FORMAT
- SCREEN_SUP_MONITOR
- SCREEN_SUP_RETENTION_DAYS
- SCREEN_SUP_LOG_LEVEL

## 示例
~~~toml
interval_seconds = 1.5
capture_root = "D:/captures"
image_format = "jpg"
monitor_index = 1
retention_days = 30
log_level = "DEBUG"
~~~

## 校验逻辑
- interval_seconds ≤ 0 将被拒绝
- capture_root 与 logs 目录若不存在会自动创建
- image_format 会被标准化为大写扩展名
- retention_days 为大于 0 时才会启用清理机制
