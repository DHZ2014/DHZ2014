# review log · lam-news（新闻包装版）

## 用到的 skill
- lemo-opuscar / news-package：画面系统（片头→台标、串联单、标题条、翻牌、比例条、门槛线、印章、色带擦除、斜向片尾卡）、配色 #121417/#F2CF1D/#D4B064/#F4F1E8、字体 Noto Sans SC + Barlow Condensed + IBM Plex Mono；音效用 lemo core/audio/sfx.py
- huashu-art-motion / storyboard_lint：镜头表 + 文稿数字核对；第 1 次红灯（结尾是字卡、两镜超长）→ 拆镜后绿灯
- xilo-opus-video：render.py 逐帧渲染、audio_tools normalize/check、analyze_video 抽帧

## 结构（按要求：删第五节 Aether，第六节利润率/现金流并入第三节）
串联单 → ① 指引 → ② 中国 → ③ 系统业务 + 利润率 + 现金流 → ④ 先进封装 → 结论 + 跟踪清单 → 片尾卡

## 事实核对（I/O Fund PDF）
- NAND $1.49B 同比 +133.5%、DRAM $1.15B +102.1%、代工 $2.64B 环比 +41%：p9–10 ✓
- GAAP 营业利润率 40%，首次：p11 ✓
- CoWoS 3.5×→5.5× 光罩，HBM 8→12：p3 ✓（示意图标注 SCHEMATIC）
- FY27 一致预期 $34.95B：p7 ✓ → 下半财年 (34.95−8.22−8.6)/2 ≈ $9.07B/季
- 其余同 lam-fq1 版

## 自检
- 第 1 轮：字体路径错误导致页面不就绪 → 修
- 第 2 轮拼图：≈$0.4B 溢出、“重申”印章压住条形、90.7 标注撞数值、75% 徽章压眉题 → 修
- 第 3 轮：门槛镜、CoWoS 镜、结论柱 OK；计算芯片加标签
- 音频：-15.6 LUFS，true peak -0.7 dBFS，无削顶无静音段
- 已知：83 秒偏长；风格规定不烧字幕，字幕单独交付 out/lam-news.srt
