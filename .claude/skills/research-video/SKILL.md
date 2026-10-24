---
name: research-video
description: 把研报、投研文章、财报解读（PDF / 文字 / 已写好的 digest 或小红书长文）做成带中文口播的竖屏投研短视频（MP4 + SRT），画面全部用代码生成。两套风格：财经电视新闻包装（默认，暗底柠檬黄，串联单、标题条、翻牌数字、印章）和纸面编辑部数据叙事。流程：digest 核对原文 → 口播稿 → 镜头表 lint → MiniMax 配音 → 逐场景写画面 → 拼图自检 → 混音 → 渲染验收。当用户说「把研报做成视频」「做个投研视频」「财报拆解视频」「研报转短视频」「小红书视频」，或给了研报并提到视频、动画、口播时使用。
---

# 研报 → 投研短视频

这套方法来自一次实做（Lam Research 2026 年 9 月季度研报，两版成片），组合了三个开源 skill 的精华，已内置在 `scripts/vendor/`，不需要另装：

| 来源（MIT） | 用到什么 |
|---|---|
| lemo-opuscar · `news-package` 风格 | 新闻包装的画面系统与规则（`references/news-package.md`）、音效库 `vendor/lemo/sfx.py` |
| huashu-art-motion（花叔） | 镜头表写法与 `vendor/huashu/storyboard_lint.py`：红灯不清不写代码 |
| xilo-opus-video | 逐帧渲染 `vendor/xilo/render.py`、响度/波形 `audio_tools.py`、抽帧 `analyze_video.py` |

一句话原则：**每一帧都是时间 t 的纯函数；先确认结构和镜头表，再写代码；先看拼图，再出整片；屏上每个数字都能在原文里找到。**

## 0. 环境（每台机器一次）

```bash
bash .claude/skills/research-video/scripts/setup.sh            # 检查依赖 + 下载字体
bash .claude/skills/research-video/scripts/setup.sh --install  # 电脑端第一次：顺带装 playwright/numpy/scipy + Chromium
```

- 需要 Python 3.9+、ffmpeg。云端 Claude Code 环境已预装 Chromium：设 `PLAYWRIGHT_BROWSERS_PATH=/opt/pw-browsers`，并用与系统 Playwright 同版本的 Python 包（见「坑」）。
- 配音用 MiniMax：电脑端设环境变量 `MINIMAX_API_KEY`（需要时再设 `MINIMAX_GROUP_ID`；国际站设 `MINIMAX_API_HOST=api.minimax.io`）。云端环境若配置了 MiniMax 代理注入，可以不设。
- 下文 `$RV` 指 `.claude/skills/research-video`，`$P` 指项目目录（建议 `videos/<slug>/`）。

## 1. Digest：先读懂、再核对

1. 用户给的是原始研报：先总结（核心论点、逐节要点、关键数字），再写「分析与见解」（最强/最弱论点、研报没展开的点、口径与时间表、利益冲突、可验证节点）。用户给的是现成 digest：直接用，但仍要做第 2 步。
2. **逐个核对屏上要出现的数字**，对照原文（PDF 用 `pdftotext -layout` 后 grep）。特别注意**归因**：例如「约 4 亿美元推迟」是电话会上分析师的估计，管理层只说会在 3 月季度补回，口播要说准。推算的数字（如去年同期 = 本季 ÷ (1+同比)）在 review_log 里写明是推算。
3. 研报作者持仓、"不构成投资建议" 必须出现在片子里（结论镜的印章 + 片尾卡）。

## 2. 结构与口播稿 `vo.json`

- `vo.json` 是一个数组，**一项 = 一个场景的口播**。新闻风格的固定顺序：串联单（今天看 N 件事）→ 各条故事 → 结论 → 跟踪清单 → 片尾卡。
- 篇幅控制（用户偏好）：内容偏长时，删掉「比例大、金额小」的次要一节（例：Aether），把利润率/现金流并入业务一节；4 条故事最合适。口播语速 1.15 时约 4.3 字/秒，6 段约 80 秒；想压到 60 秒用 1.3 或删一节。
- 口播里数字用中文读法（「百分之四点六」），屏上/字幕会自动转成阿拉伯数字（`scripts/common.py: cn_digits`，只转带单位的数，"一致预期""四件事"不会被改）。
- 结论段要有「解读」的态度，而不只是复述研报：例如「增长加速主要靠中国，剔除后环比只有约 7%」「+70% 是重申，不是新消息」「剔除营运资本后 FCF 利润率约 33%」。

## 3. 镜头表 + lint（红灯不写代码）

照 `examples/lam-news/镜头表.md` 写 `$P/镜头表.md`：表前三行锁画风、色板、角色；每行一镜：时间段｜画面里的物（名词）｜它在做什么（动词）｜镜头｜屏上字（≤8 字）｜做法。

```bash
bash $RV/scripts/make.sh $P lint
```

常见红灯：结尾是纯字卡（改成品牌板飞回中央收尾）、单镜超过 8 秒（拆镜）、屏上数字在口播里找不到。

## 4. 建项目、配音、排时间轴

```bash
python3 $RV/scripts/new.py $P --style news          # 或 --style editorial
# 写好 $P/vo.json（和 镜头表.md）后：
bash $RV/scripts/make.sh $P tts                     # 只重做第 3 段：make.sh $P tts 3
bash $RV/scripts/make.sh $P timing                  # 打印 C(i) 字幕时间表，画面事件就按它对齐
```

`config.json` 可调：`voice_id`（默认 male-qn-jingying）、`speed`、`lead`/`tail`（场景首尾留白）、`leads`（场景 0 给片头留 1.9 秒）、`end_pad`（片尾卡时长）、`digits`（额外的文字替换）、`burn_subs`（`true` 时字幕烧进画面）。

## 5. 写画面 `template.html`

- 新项目的 `template.html` 是上一支片子的完整实现，**保留包装系统的函数，按新研报重写场景函数**。新闻风格里可直接复用：`makeFlap`（翻牌板）、`makeStrap`（每个场景自带的标题条，内容可在场景内翻换）、`stampIn`（印章 + 扩散环）、`popIn`、`shake`、比例条卡片、门槛线、串联单行 `row`、片头 → 台标、色带擦除、斜向片尾卡。规则见 `references/news-package.md`；纸面风格见 `references/editorial.md`。
- 画面事件一律挂在字幕时间上：`C(i)` 是第 i 条字幕开始、`CE(i)` 是结束、`SC[k].t0/t1` 是场景边界。改口播重跑 `timing` 后画面自动跟上。
- 渲染合约：`window.render(t)` 决定一切；不用 CSS transition/animation、setTimeout、`Math.random()`、帧间状态；随机用种子函数，弹簧用闭式解；字体加载完再 `window.ready = true`。
- 一屏一个事实；故事之间色带擦除，故事内部硬切；印章每个故事最多一个；示意图（非真实数据比例）挂 `SCHEMATIC / 示意图` 标签。

## 6. 拼图自检（最关键）

```bash
bash $RV/scripts/make.sh $P stills 1.2 9.5 15.5 22 27 33.6 43.3 48.5 53.5 59.5 68.5 82.5
```

打开 `$P/qa/sheet.png` 亲自看，按 开场 / 手机可读 / 动作 / 变化 / 构图 / 贴合原材料 / 声画同步 各打 1–10 分，修最差的 3 处再出拼图，直到每项 ≥ 8。常见问题：数字和印章叠在一起、标签撞柱顶数值、徽章压眉题、大字溢出色块、下半屏空。每轮写进 `$P/qa/review_log.md`。

## 7. 混音、渲染、验收

```bash
bash $RV/scripts/make.sh $P audio     # 改 $P/mix.py 里「音效」一节的时间点（按 C(i)）后再跑
bash $RV/scripts/make.sh $P render    # 约 5–6 秒渲染 1 秒成片，83 秒的片子约 9 分钟：放后台跑
```

- 响度目标 −14 LUFS（−15 左右也可接受），true peak 低于 −1 dB 为佳；看 `qa/audio-wave.png` 有无削顶和静音段。
- 看 `qa/final-sheet.png` 整片抽帧，确认转场、收尾都对。

## 8. 交付

`out/<项目>.mp4`、`out/<项目>.srt`。新闻风格原版规定画面不烧字幕；发小红书、视频号这类常被静音观看的平台时，在 `config.json` 设 `"burn_subs": true`：字幕放在标题条下方（y≈1588，深色底条 + 强调色下划线，数字染黄），来源线自动挪到 tab 右侧，底部 220px 仍留给平台 UI。只改字幕不改口播时，沿用原来的 `audio/mix.wav`，直接 `render` 即可、`qa/review_log.md`（事实核对 + 自检分数 + 已知不足）。告诉用户怎么改：口播改 `vo.json` → `tts`/`timing`，画面改 `template.html`，再 `render`。

## 坑（实做中踩过的）

- `fonts/fonts.css` 里 `url()` 是相对 CSS 文件本身的：写 `url('X.ttf')`，不要再加 `fonts/` 前缀，否则字体 404、`window.ready` 永远不为真、渲染 60 秒超时。
- 页面不就绪时，用 Playwright 抓 `pageerror` / console 看原因，别盲目重试。
- 不要 `pkill -f "render.py ..."`：模式会匹配到执行它的那个 shell 自己。
- 字幕时间按字数分配时，英文单词要按约 1.5 个汉字计权重，否则 "Lam Research" 这类开头会对歪；相邻字幕至少间隔 0.45 秒，防止吸附停顿后出现零时长字幕。
- MiniMax 的 `subtitle_file`（逐字时间戳）在阿里云 OSS，云端代理访问不到，所以用 ffmpeg `silencedetect` 找停顿代替。
- 云端用 Python Playwright 时，pip 装与系统 Node Playwright 相同的版本号（如 `playwright==1.63.0`），才能用上预装的 Chromium；不要再 `playwright install`。
- 往 `~/.claude/skills` 写文件在云端可能被权限拦下：用仓库里的项目级 skill（就是本目录）即可。

## 更多风格

`news-package` 来自 lemo-opuscar 的 59 套风格库，其中适合投研的还有 `dataviz`、`briefing-board`、`halftone-dossier`、`caption-news`。需要时安装原库读对应 `styles/<名>/STYLE.md`：

```bash
claude plugin marketplace add lemomo-ai/lemo-opuscar && claude plugin install lemo-opuscar@lemolab
npx skills add alchaincyf/huashu-art-motion      # 花叔：36 种艺术风格、解说动画语法
npx skills add Kianzzz/xilo-opus-video           # 三方案 + 预览的出片流程
```
