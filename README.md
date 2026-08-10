# EasyUI 扁平化 API 文档（中文）

基于国内站点 [jeasyui.cn](https://www.jeasyui.cn/) 重构的 EasyUI 组件 API 参考站。

## 为什么做这个

官方文档每个组件只列出「新增 / 重写」的成员，并靠一句「扩展自 X」层层嵌套继承——
想查 `combogrid` 的全部可用方法，要一路跳 `combo → validatebox` 和 `datagrid → panel`，非常不友好。

本站点把**每个组件全部可用的属性 / 事件 / 方法**扁平化合并到**一张表**，并用「来源」列
标注该成员实际定义在哪个祖先组件；带「重写」标记表示在当前组件被覆盖。

覆盖三族共 21 个组件：表单输入、表格 / 数据网格、树，以及组合下拉框（Combo + Grid/Tree）。

## 站点功能

- 左侧组件导航（按族分组）+ 实时搜索，按 Enter 跳到首个匹配项。
- 每个组件顶部有**继承链面包屑**，点击祖先可跳转。
- 每张表上方「按来源筛选」下拉：只看「仅自身新增」或某个祖先的成员。
- 每个组件附「原站 ↗」链接，方便对照原文。

## 本地查看

`index.html` 是**自包含单文件**（数据 / 样式 / 脚本全部内联），双击即可在浏览器打开，无需联网或构建。

## 重新生成（当 jeasyui.cn 更新时）

```bash
cd build
pip install requests beautifulsoup4   # 首次需要
python scrape.py     # 抓取并解析 21 个组件 API 页 -> components_raw.json
python flatten.py    # 沿继承链扁平合并并标注来源 -> components_flat.json
python render.py     # 渲染为 ../index.html
```

## 部署

通过 GitHub Actions + GitHub Pages 自动发布，工作流见 `.github/workflows/pages.yml`。
推送 `main` 分支即触发部署，发布地址为 `https://<github-user>.github.io/<repo>/`。
