# BidGuard

面向 IT、软件和网络服务类政府采购的招投标文件智能审查与响应辅助平台。项目使用 RAGFlow、LangGraph 和 FastAPI，重点实现复杂文档解析、关键条款抽取、响应矩阵、证据检索、风险审查和人工复核闭环。

- [年度项目路线图](./PROJECT_ROADMAP_3W.md)
- [Day 1：项目章程](./docs/bidguard/day01_project_charter.md)

当前进度：Week 1 / Day 1 已完成。下一步是建立数据 Manifest，并登记首批真实公开采购项目。

## 环境安装

### 使用powershell

```powershell
# 创建虚拟环境
py -3.14 -m venv .venv

# 激活虚拟环境
.venv\Scripts\avtivate.ps1
```

## Git 多人协作

### 创建自己的分支

```powershell
# 创建分支：dev_(自己命名)
git chechout -b dev_yzy

# 切换本地仓库到自己的分支
git swtich dev_yzy

# 查看验证
git branch --show-current 

# 第一次在分支push代码
git add . 
git commit -m "first git push"
git push -u origin dev_yzy    # 以后在该分支直接使用 git push 命令即可
```
