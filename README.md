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
| 点击计数 | ❌ **无真实计数**（原 webhook.site collector 账号已失效，已移除该 beacon） |
| 归因依据 | 仅靠 Upwork 侧 `utm_source` / `utm_medium` / `utm_campaign` |

## ⚠️ 关于「点击计数」的明确声明

**本方案不提供站内真实点击计数。**
站内 `/go/<slug>` 页面已移除失效的 webhook.site 上报脚本，因此**没有任何数据**
可以统计真实点击；任何声称来自本站的点击数都是不成立的。

可用的真实数据只有两处，且都不是「站内点击」：
1. Upwork 官方后台按 `utm_campaign=<slug>` 拆分的访问/消息来源；
2. 本机自建服务的 SQLite 计数（`~/projects/upwork-redirect/server.py`，
   仅统计打到该服务自身的请求，**目前未对公网开放**）。

## 服务端 302 的迁移路径（待凭据）

服务端真实 302 + 真实计数需要把 `/go/:slug` 变成同源 serverless 函数，
候选平台与所需凭据：

| 平台 | 形态 | 需要的凭据 |
|---|---|---|
| Vercel | `vercel.json` rewrite `/go/:slug` → `/api/go`，函数返回 302 | 有效 Vercel token 或设备码授权 |
| Cloudflare Pages/Workers | 同上 | Cloudflare 账号 + API token |
| 自有服务器 | openresty `return 302` | 服务器 SSH + 域名 DNS 控制权 |

计数存储建议随平台走：Vercel KV / Edge Config，或回写 GitHub Gist（token 存环境变量）。

## 相关文件

- `go/<slug>.html` — 跳转页（14 个 slug）
- `~/projects/upwork-redirect/server.py` — 本机自建 302 + SQLite 计数服务（参考实现，未公网暴露）
- `~/projects/upwork-redirect/app/api/go.js` — Vercel 函数版实现（待有效 token 后部署）
