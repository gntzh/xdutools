# XDU Tools

- 西电相关工具，包括基础的认证服务和在此基础上构建的各种功能；
- 同时提供了一个 CLI。

## 安装

```bash
// 要求 Python >= 3.9
pip install xdutools[all] --pre -U
xdu --help
```
默认是没有 CLI 的，可以使用`xdutools[cli]`来安装CLI。

## CLI
### 课表查询

```bash
xdu schedule --format=wakeup
```
除默认格式外, `format`可选`[simple|wakeup]`：
- simple对应[Simple课程表](https://www.coolapk.com/apk/com.strivexj.timetable)的文件导入格式（.txt）。
- wakeup对应[WakeUp课程表](https://www.coolapk.com/apk/com.suda.yzune.wakeupschedule)的Excel导入格式（.csv）。

## Disclaimer
