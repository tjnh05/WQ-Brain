FROM docker.m.daocloud.io/python:3.12-alpine

# 安装必要的工具（adduser 和 su-exec）
RUN apk add --no-cache shadow

# 创建用户和用户组
RUN adduser -D -u 1000 -g 1000 appuser


# 创建 /app 和 /app/data 目录
RUN mkdir -p /app/data/log && mkdir -p /app/data/backup

# 设置工作目录
WORKDIR /app

# 将指定文件复制到容器的 /app 目录
COPY main.py scrape_alphas.py submit_alphas.py database.py alpha_miner.py arxiv.txt /app/
COPY /data/factor_library.csv /app/data/

# 复制 requirements.txt 并安装依赖（使用清华源）
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple

# 设置环境变量，防止Python输出被缓冲
ENV PYTHONUNBUFFERED=1

# 修改文件权限，确保普通用户有访问权限
RUN chown -R appuser:appuser /app

# 切换到普通用户
USER appuser

# 运行 main.py
CMD ["python", "main.py"]
