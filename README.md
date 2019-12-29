# XDU Tools

- 工具实现了对西电网站和西电一站式服务大厅apps的cookies的获取
- CLI调用工具接口

## 安装

```bash
// python环境
mkdir xduapps
cd xduapps
git clone git@github.com:ShoorDay/xduapps.git
// 或者http下载 https://github.com/ShoorDay/xduapps.git
pip install .
// 检查
xdu --help
```

## 课表查询

```bash
xdu schedule --format=simple
```
默认保存为csv格式, 目前可选`[simple|csv]`
simple对应Android应用[Simle课程表](https://www.coolapk.com/apk/com.strivexj.timetable)的文本文件导入格式

## 注意

1. 对于网络、登录成功没有做任何检查, 请在网络良好下使用, 确保账号密码正确
2. 西电接口多变, 可能明年就不能用了:cry

## 其他

- 以后有时间完善课表查询功能
- 一站式服务大厅的其他应用以后也看看

## Disclaimer
