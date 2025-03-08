# 使用Python 3.12作为基础镜像
FROM python:3.12-slim

# 安装 pip
RUN python -m ensurepip --upgrade && \
    pip install --upgrade pip

# 创建 /app 和 /app/data 目录
RUN mkdir -p /app/{data,logs}

# 创建一个普通用户（例如：appuser）
RUN useradd -m appuser

# 设置工作目录
WORKDIR /app

# 将指定文件复制到容器的 /app 目录
COPY main.py scrape_alphas.py submit_alphas.py database.py alpha_miner.py arxiv.txt factor_library.csv /app/

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
