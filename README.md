# Algo Daily · LeetCode 每日两题

中文手机优先学习网站：50 天固定题单、每天两题，按北京时间自动显示，查看历史、题目提示、C++17 答案、个人学习进度及笔记。

## 访问网页

网站预计地址：<https://shushudoudou.github.io/leetcode-daily/>

首次发布前，仓库管理员须前往 [Settings → Pages](https://github.com/shushudoudou/leetcode-daily/settings/pages)，在 **Build and deployment → Source** 选择 **GitHub Actions**。仓库内已提供 `.github/workflows/deploy.yml`，任何推送到 main 都会触发发布。请在 [Actions](https://github.com/shushudoudou/leetcode-daily/actions) 确认成功后再使用公网网址。

网站为单文件静态实现，`index.html` 已内嵌题库与目前存在的答案，CSS/JS 均已内置，无需额外构建或 NPM 依赖。

## 时间与题库

- 2026-10-26 为 Day 1，以 Asia/Shanghai（UTC+08:00）计算自然日。
- Day 1 到 Day 50 对应 100 道 LeetCode 简单/中等题，后续每 50 天循环进入间隔复习。
- 每日 08:00 练题，19:00 可通过「晚间解析」查看已发布的答案。
- 当前已写入 Day 1 到 Day 12 的 24 道 C++17 解析。
- 每天题目与历史归档**无需重新部署**，网站会按北京时间自动切换。
- 学习状态和笔记存储于访问设备的浏览器 localStorage，不同设备不会同步。

## 夜间自动生成答案（可选）

已提供 `scripts/publish_inline.py` 与 GitHub Actions 计划任务，按北京时间每天约 19:15 运行（GitHub 调度可能延迟）。

要开启，需要仓库管理员自行在 [Settings → Secrets and variables → Actions](https://github.com/shushudoudou/leetcode-daily/settings/secrets/actions) 创建 repository secret `OPENAI_API_KEY`，使用自己的 OpenAI API key（API 调用通常收费）。API key **只能存放在 GitHub Actions Secrets 中**，不要写入公开仓库或网页。可选：设置 repository variable `OPENAI_MODEL`，默认 `gpt-4.1-mini`。

流程只为当前日期缺少答案的题目调用模型；结果持久化进 `index.html`，提交后由当前 GitHub Actions 直接部署。未配置 API key 时不会自动生成新答案，网站会真实提示「解析尚未发布」。

**重要：AI 生成的 C++17 题解目前只通过最基本格式校验，没有对所有 LeetCode 用例自动编译/运行验证。** 使用前请复核边界条件，不能保证每次模型输出都正确。如果 API 出错，工作流会失败并可在 Actions 查看日志；既有题目与答案不会被清除。不要在本地浏览器暴露 API key。

## 维护

- 主页 `index.html` 内的 `window.__CURRICULUM__`：50 天固定题单、100 道题题干摘要与提示。
- `window.__SOLUTIONS__`：答案 JSON 存档（题号为 key）；可手动编辑补充并推送。
- `scripts/publish_inline.py`：夜间调用 API 的自动发布脚本。
- `.github/workflows/deploy.yml`：Push、手动或计划调度部署流程。

本项目只用于算法练习，题目官方版权归 LeetCode 所有，点击题目卡片可打开官方链接。
