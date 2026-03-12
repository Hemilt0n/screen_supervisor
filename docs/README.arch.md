# 架构说明

## 总览
Screen Supervisor 由配置、截屏器、存储器和调度器四个核心组件组成：
1. **Config**：加载 TOML/环境变量，统一生成 SupervisorConfig。
2. **ScreenCapturer**：基于 mss 截取指定显示区域，返回 Pillow 图像对象。
3. **StorageManager**：负责创建日期目录、保存图像文件、按保留策略清理旧目录。
4. **IntervalScheduler**：使用线程安全的循环维持固定间隔执行任务。
5. **ScreenSupervisor**：绑定上述组件，实现一次迭代捕获→保存→清理→日志的完整流程。

## 运行流程
1. CLI 解析配置路径，调用 config.load_config。
2. ScreenSupervisor 初始化捕获器与存储器，创建调度器。
3. 调度器循环：
   - 记录当次开始时间
   - 调用 supervisor.capture_once（执行截屏与保存）
   - 根据耗时 sleep，确保与 interval_seconds 对齐
4. 每轮结束后根据 retention_days 异步触发清理任务。

## 并发与资源
- 默认单线程循环，避免多线程占用。
- 通过 threading.Event 控制退出，支持 Ctrl+C 安全关闭。
- mss 在每次 capture 内部申请/释放句柄，避免长时间握住资源。

## 扩展点
- **多显示器**：ScreenCapturer 接收 monitor_index，可扩展为多实例并行。
- **远端同步**：StorageManager 可以新增钩子上传到对象存储。
- **不同调度策略**：IntervalScheduler 接口简单，可替换为 asyncio 或 APScheduler。
- **日志输出**：当前使用标准 logging，可在配置中增加文件 handler 或结构化日志。
