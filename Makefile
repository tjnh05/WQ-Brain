# 定义变量
ROOTDIR=/root/miniconda3/envs/wqbrain/bin/
PYTHON = $(ROOTDIR)python
PIP = $(ROOTDIR)pip
BACKUP_DIR = backups
FACTOR_FILE = factor_library.csv

# 默认目标
all: factors simulate

# 生成因子库并备份
factors:
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
	@echo "  help             - 显示此帮助信息"

.PHONY: all factors simulate clean_backups
