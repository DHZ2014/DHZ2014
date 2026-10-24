# brief：Opus 用代码做视频 · 5 个 skill

<role>小红书竖屏知识短片的动效导演，全部画面和声音用代码生成。</role>

<inputs>
- 题材：小红书笔记「Opus 5.5 做视频杀疯了！5个 Skills 推荐」里的 5 个仓库
- 事实来源（全部来自仓库的 SKILL.md / 目录）：
  - huashu-art-motion：SKILL.md 描述「36种既有实做风格」
  - lemo-opuscar：`styles/` 下 59 个风格目录（不含 README、_template）
  - animate：故事、画面、分镜三次确认后才动画（SKILL.md Non-negotiables #1）
  - opus-video-skills：一种风格一个 skill（README）
  - xilo-opus-video：先给三个方案 + 预览（SKILL.md 第 2–3 步）
</inputs>

<direction>
- 画幅 1080×1920，30fps，19 秒，纯音乐 + 屏幕文字，无配音
- 风格：编辑部 · 纸面。纸色底 #f2f0ea，墨色 #141414，唯一强调色蓝 #2f5bea（呼应原笔记封面的蓝）
- 字体：标题文泉驿正黑，代码/元信息等宽体
- 禁止：深色底居中大字淡入、粒子、光晕、抖动、文字句号
</direction>

<structure>
| 时间 | 镜头 | 读到什么 | 声音 |
|---|---|---|---|
| 0–3.5 | 代码卡里敲出 `render(t)`，一帧画面从卡里弹出 | Opus 不会剪视频 / 但它会写代码 | 打字 tick，弹出 pop |
| 3.5–8 | 一条胶片带横向流过，t 计数器滚动 | 每一帧 = f(t)：网页 → 逐帧截图 → MP4 | kick 律动 |
| 8–13.5 | 蓝色擦除转场；5 个仓库按拍依次滑入 | 5 个开源 skill 各自的特点 | 每行一个 click |
| 13.5–17 | 蓝色擦除；三张步骤卡 + 勾 | 共同的秘密：先分镜 · 拼图自检 · 红灯不交付 | success |
| 17–19 | 回到开头的代码卡（首尾呼应） | 流程 > 提示词 | impact 收尾 |
</structure>

<build>单个 index.html，window.render(t)；xilo-opus-video 的 render.py 渲染，audio_tools.py 合成音效，numpy 写一层和弦铺底。</build>

<gotchas>转场色块画在内容之上，场景切换发生在色块铺满的那一帧；所有状态只由 t 决定。</gotchas>

<start>先出每个镜头的静帧拼图自检，再渲整片。</start>
