# 数据更新流程

这是旧文件名的兼容入口。完整的数据来源、空值语义、失败保护和验收步骤统一维护在 [docs/data-pipeline.md](docs/data-pipeline.md)。

常用命令：

```powershell
npm run validate:data
npm test
npm run build
```

不要手工编辑线上 CSV/metadata，也不要在未完成校验时覆盖已有产物。
