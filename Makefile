# 定义变量
ROOTDIR=/root/miniconda3/envs/wqbrain/bin/
CURRENT_DIR := $(abspath .)
DATADIR=$(DATADIR)data/
LOGDIR=$(DATADIR)log
PYTHON = $(ROOTDIR)python
PIP = $(ROOTDIR)pip
BACKUP_DIR = $(DATADIR)backups
FACTOR_FILE = $(DATADIR)factor_library.csv
DOCKER_IMAGE_TAG = wq-brain-wqbrain:latest  # 新增变量定义
VOLUME_NAME = wqbrain_data

# 默认目标
all: factors simulate

print_path:
	@echo "Current directory: $(CURRENT_DIR)"

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

# 新增从 Docker 卷复制文件到本地备份目录的目标
copy_volumes:
	@echo "Copying files from Docker volume $(VOLUME_NAME) to $(BACKUP_DIR)..."
	@mkdir -p $(BACKUP_DIR)
	@docker run --rm -v $(VOLUME_NAME):/volume_data -v $(BACKUP_DIR):/backup busybox cp -r /volume_data /backup
	@echo "Files copied successfully."


.PHONY: all factors simulate clean_backups build help
