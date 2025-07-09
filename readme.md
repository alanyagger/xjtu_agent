##### Table of contents
1. [Environment setup](#environment-setup)
2. [How to run](#how-to-run)
### **XJTU 交小荣智能学生教务平台**
## Environment setup
Install dependencies:
```shell
node.js v22.17.0
conda   v24.9.2
```
```shell
conda create -n xjtu_agent python=3.12
pip -r requirements.txt
```
Evironment dependencies can be **downloaded** from provided links in the table below:
<table style="width:100%">
  <tr>
    <th></th>
    <th>Link</th>
  </tr>
  <tr>
    <td>node</td>
    <td><a href="https://nodejs.org/en/download">node.js</a></td>
  </tr>
  <tr>
    <td>conda</td>
    <td><a href="https://repo.anaconda.com/archive/">Anaconda</a></td>
  </tr>
  <tr>
    <td>Redis</td>
    <td><a href="https://github.com/tporadowski/redis/releases">Redis(截至5.0已停止维护)//</a><a href="https://github.com/redis-windows/redis-windows/releases">Redis(社区编译新版本)</a></td>
  </tr>
  <tr>
    <td>Chrome Driver</td>
    <td><a href="https://developer.chrome.com/docs/chromedriver">Chrome</a></td>
  </tr>
</table>

## How to run:
run frontend ./frontend
```bash
npm install
npm run dev
```
run backend ./backend
```bash
python start_server.py
```
