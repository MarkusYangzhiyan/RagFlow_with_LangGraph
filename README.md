## 环境安装

### 使用powershell

```powershell
# 创建虚拟环境
py -3.12 -m venv .venv

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
