# 定义变量
ROOTDIR=/root/miniconda3/envs/wqbrain/bin/
DATADIR=data/
LOGDIR=log/
PYTHON = $(ROOTDIR)python
PIP = $(ROOTDIR)pip
BACKUP_DIR = backups
FACTOR_FILE = $(DATADIR)factor_library.csv
DOCKER_IMAGE_TAG = wq-brain-wqbrain:latest  # 新增变量定义

# 默认目标
all: factors simulate

# 生成因子库并备份
factors:
	# 创建数据目录
	mkdir -p $(DATADIR)
	# 创建日志目录
	mkdir -p $(LOGDIR)
	# 创建备份目录（如果不存在）
	mkdir -p $(BACKUP_DIR)
	# 如果存在factor_library.csv，则备份
	@if [ -f $(FACTOR_FILE) ]; then \
		TIMESTAMP=$$(date +"%Y%m%d%H%M%S"); \
		cp $(FACTOR_FILE) $(BACKUP_DIR)/$(FACTOR_FILE).$$TIMESTAMP; \
	fi
	# 执行commands.py生成新的factor_library.csv
	$(PYTHON) commands.py

# 模拟运行
simulate:
	# 执行main.py进行模拟
	$(PYTHON) main.py

install:
	$(PIP) install -r requirements.txt

# 清理备份文件
clean_backups:
	rm -rf $(BACKUP_DIR)/*

# 帮助信息目标
help:
	@echo "Usage: make [target]"
	@echo ""
	@echo "Available targets:"
	@echo "  all              - 默认目标，依次执行 generate_factors 和 simulate"
	@echo "  generate_factors - 生成因子库并备份到 $(BACKUP_DIR)"
	@echo "  simulate         - 执行模拟运行 (main.py)"
	@echo "  clean_backups    - 清理所有备份文件"
	@echo "  build            - 构建 Docker 镜像"
	@echo "  up               - 启动 Docker 容器"
	@echo "  down             - 停止 Docker 容器"
	@echo "  log              - 查看容器运行时日志"
	@echo "  help             - 显示此帮助信息"


# 新增构建 Docker 镜像的目标
build:
	docker build -t $(DOCKER_IMAGE_TAG) .

# 新增启动 Docker 容器的目标
up:
	docker compose up -d

# 新增停止 Docker 容器的目标
down:
	docker compose down

# 新增查看容器运行时日志的目标
log:
	docker compose logs -f

.PHONY: all factors simulate clean_backups build help
