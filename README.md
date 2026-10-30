# 龙雅人 Portfolio

> 站内 Upwork 跳转：**统一使用 `/go/<slug>`**
> 例：`/go/home`、`/go/geo-guide-2026`（相对路径，站点挂在 GitHub Pages 的
> `/longyaren-portfolio/` 子路径下，因此链接用相对形式而非站点根绝对路径）

## 跳转口径（当前生效）

| 项 | 现状 |
|---|---|
| 跳转目标 | `https://www.upwork.com/freelancers/longyaren?utm_source=longyaren&utm_medium=portfolio&utm_campaign=<slug>` |
| 跳转方式 | 静态页 meta refresh + `window.location.replace`（**客户端跳转**） |
| 服务端 HTTP 302 | ❌ 未启用（GitHub Pages 为纯静态托管，不支持服务端 302） |
| 点击计数 | ✅ **真实计数**（webhook.site collector 存活，beacon 已恢复） |
| 归因依据 | Upwork 侧 `utm_source` / `utm_medium` / `utm_campaign` + 本地点击日报 |

## 点击计数：口径与局限

计数**是真实的**，不是估算：每个 `/go/<slug>` 页面加载时会向 webhook.site collector
发一次 fire-and-forget 请求（`navigator.sendBeacon`），带上 `slug` 与 `referrer`；
采集器按请求行累计，日报脚本 `~/.openclaw/workspace/scripts/upwork_click_digest.py`
读取后推送飞书。

局限（必须知道）：
1. **统计的是「跳转页被打开」**，不是「Upwork 成交」；成交仍需看 Upwork 后台。
2. 计数在**浏览器端**产生 → 受广告拦截器、隐私模式、beacon 被网络层拦截影响，
   真实数值会**低于**实际点击；因此不能把该数字当成精确值，只能当趋势。
3. 依赖第三方免费服务 webhook.site；该服务若失效，计数会中断
   （曾发生一次误判为「账号 inactive」，2026-10-30 复核为存活）。
4. 计数服务尚未对公网暴露，`localhost:8799` 的 SQLite 计数只反映本机自测流量。

## 服务端 302 的迁移路径（待凭据）

服务端真实 302 + 服务端计数需要把 `/go/:slug` 变成同源 serverless 函数，
候选平台与所需凭据：

| 平台 | 形态 | 需要的凭据 |
|---|---|---|
| Vercel | `vercel.json` rewrite `/go/:slug` → `/api/go`，函数返回 302 | 有效 Vercel token 或设备码授权 |
| Cloudflare Pages/Workers | 同上 | Cloudflare 账号 + API token |
| 自有服务器 | openresty `return 302` | 服务器 SSH + 域名 DNS 控制权 |

计数存储建议随平台走：Vercel KV / Edge Config，或回写 GitHub Gist（token 存环境变量）。

## 相关文件

- `go/<slug>.html` — 跳转页（14 个 slug，含点击 beacon）
- `~/.openclaw/workspace/scripts/upwork_click_digest.py` — 每日点击日报（读采集器 → 飞书 DM）
- `~/projects/upwork-redirect/server.py` — 本机自建 302 + SQLite 计数服务（参考实现，未公网暴露）
- `~/projects/upwork-redirect/app/api/go.js` — Vercel 函数版实现（待有效 token 后部署）
