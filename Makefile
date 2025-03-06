# 定义变量
PYTHON = python
BACKUP_DIR = backups
FACTOR_FILE = factor_library.csv

# 默认目标
all: factors simulate

# 生成因子库并备份
factors:
	# 创建备份目录（如果不存在）
	mkdir -p $(BACKUP_DIR)
	# 如果存在factor_library.csv，则备份
	if [ -f $(FACTOR_FILE) ]; then \
		TIMESTAMP=$$(date +"%Y%m%d%H%M%S"); \
		cp $(FACTOR_FILE) $(BACKUP_DIR)/$(FACTOR_FILE).$$TIMESTAMP; \
	fi
	# 执行commands.py生成新的factor_library.csv
	$(PYTHON) commands.py

# 模拟运行
simulate:
	# 执行main.py进行模拟
	$(PYTHON) main.py

# 清理备份文件
clean_backups:
	rm -rf $(BACKUP_DIR)/*

.PHONY: all factors simulate clean_backups
