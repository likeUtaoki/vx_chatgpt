# wxmp_chat

## 介绍

基于ChatGPT开发微信公众号智能机器人，同时也支持网页版的。全程免费试用，不限额度。网页版的通过关注微信公众号实现登录之后，即可开启于人工智能机器人畅快的聊天了

## 技术栈

- [FastAPI](https://fastapi.tiangolo.com/zh/)

- [redis](https://aioredis.readthedocs.io/en/latest/)

- [layim](http://layui.org.cn/fly/docs/7.html)

- [wechatpy](http://docs.wechatpy.org/zh_CN/stable/)

## 安装过程

### 安装redis

`redis`的安装方式采用`docker`方式安装，首先，我们新建一个文件夹`redis`，然后在该目录下创建出`data`文件夹、`redis.conf`文件和`docker-compose.yaml`文件

`redis.conf`文件的内容如下(后面的配置可在这更改，比如requirepass 我指定的密码为`didiplus`)

```
protected-mode no
port 6379
timeout 0
save 900 1 
save 300 10
save 60 10000
rdbcompression yes
dbfilename dump.rdb
dir /data
appendonly yes
appendfsync everysec
requirepass didiplus
```

`docker-compose.yaml`的文件内容如下：

```yaml
version: '3'
services:
  redis:
    image: redis:latest
    container_name: redis
    restart: always
    ports:
      - 6379:6379
    volumes:
      - ./redis.conf:/usr/local/etc/redis/redis.conf:rw
      - ./data:/data:rw
    command:
      /bin/bash -c "redis-server /usr/local/etc/redis/redis.conf "
```

配置的工作就完了，如果是云服务器，记得开redis端口**6379**

启动Redis

```shell
docker-compose up -d

docker ps

docker exec -it redis redis-cli

auth didiplus
```

### 拉取本项目

由于个人的订阅号没有权限去获取场景二维码

![](https://didiplus.oss-cn-hangzhou.aliyuncs.com/20230226123115.png)

```shell
 git clone git@gitee.com:didiplus/mp_chatgpt.git
```
在项目的根根目录下新建一个`.env`环境变量配置文件,内容如下：
```
#redis服务器地址
REDIS_HOST="redis地址"
REDIS_PORT = 6379
REDIS_PASSWORD = "redis密码"
REDIS_DATABASE = 0

#微信公众号
TOKEN = "公众号token"
APPID = "公众号token_APPID"
APPSECRET = "公众号token_APPSECRET"


#ChatGPT
OPENAIKEY = "sk-"
SESSION_TOKEN =""
```

构建docker镜像
```
docker build -t mp_chatgpt:v1 .
```
启动镜像
```shell
docker run -d -p 80:80 --name mp_chatgpt mp_chatgpt:v1
```

## 效果图

![](https://didiplus.oss-cn-hangzhou.aliyuncs.com/VeryCapture_20230225214104.gif)

