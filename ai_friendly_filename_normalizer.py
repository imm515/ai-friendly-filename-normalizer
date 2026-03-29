#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
文件名规范化脚本
功能：递归处理目录下的所有文件和文件夹，将文件名中的特殊字符替换为下划线
"""

import os
import sys
import re
import logging
from pathlib import Path
from typing import List, Tuple


# 配置日志格式
def setup_logging(log_file: str = None):
    """
    配置日志系统
    
    Args:
        log_file: 日志文件路径，如果为None则只输出到控制台
    """
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.INFO)
    
    # 日志格式
    formatter = logging.Formatter(
        '%(asctime)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # 控制台处理器
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    # 文件处理器（如果指定了日志文件）
    if log_file:
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setLevel(logging.INFO)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    
    return logger

logger = logging.getLogger(__name__)


class FileNameNormalizer:
    """文件名规范化工具"""
    
    def __init__(self, root_dir: str, dry_run: bool = False):
        """
        初始化
        
        Args:
            root_dir: 要处理的根目录
            dry_run: 试运行模式，只显示将要执行的操作，不实际执行
        """
        self.root_dir = Path(root_dir).resolve()
        self.dry_run = dry_run
        self.rename_count = 0
        self.skip_count = 0
        self.error_count = 0
        
    def normalize_filename(self, name: str) -> str:
        """
        规范化文件名
        
        处理规则：
        1. 全角字符转半角（空格、连字符、括号等）
        2. 空格（包括全角）替换为下划线
        3. 连字符（包括全角）替换为下划线
        4. 方括号和圆括号前后添加下划线分隔
        5. 不替换其他特殊字符
        6. 多个连续下划线合并为一个
        7. 去除首尾下划线
        
        Args:
            name: 原始文件名
            
        Returns:
            规范化后的文件名
        """
        # 保存扩展名
        stem = Path(name).stem
        suffix = Path(name).suffix
        
        # 全角字符转半角
        # 全角空格 → 半角空格
        stem = stem.replace('　', ' ')
        # 全角连字符 → 半角连字符
        stem = stem.replace('—', '-').replace('–', '-')
        
        # 先替换空格和连字符为下划线，再合并
        # 空格（半角） → 下划线
        stem = stem.replace(' ', '_')
        # 连字符（半角） → 下划线
        stem = stem.replace('-', '_')
        
        # 合并多个连续下划线为一个（第一次）
        stem = re.sub(r'_+', '_', stem)
        
        # 全角括号 → 半角括号（前后添加双下划线分隔）
        # 使用特殊标记避免被合并
        stem = stem.replace('【', '§OPENBRACKET§')
        stem = stem.replace('】', '§CLOSEBRACKET§')
        stem = stem.replace('（', '§OPENPAREN§')
        stem = stem.replace('）', '§CLOSEPAREN§')
        
        # 替换特殊标记为双下划线+括号
        stem = stem.replace('§OPENBRACKET§', '__[')
        stem = stem.replace('§CLOSEBRACKET§', ']__')
        stem = stem.replace('§OPENPAREN§', '__(')
        stem = stem.replace('§CLOSEPAREN§', ')__')
        
        # 合并多个连续下划线为一个（第二次，但保留双下划线）
        # 使用负向断言，避免合并双下划线
        stem = re.sub(r'(?<!_)_(?!_)', '_', stem)
        
        # 去除首尾下划线
        stem = stem.strip('_')
        
        # 如果处理后为空，使用默认名称
        if not stem:
            stem = 'unnamed'
            
        return stem + suffix
    
    def collect_items(self) -> List[Tuple[Path, Path]]:
        """
        收集所有需要重命名的项目（文件和文件夹）
        
        使用深度优先遍历，确保先处理子目录再处理父目录
        
        Returns:
            [(原路径, 新路径), ...] 的列表
        """
        items_to_rename = []
        
        # 递归遍历所有文件和文件夹
        for root, dirs, files in os.walk(self.root_dir, topdown=False):
            root_path = Path(root)
            
            # 处理文件
            for filename in files:
                old_path = root_path / filename
                new_filename = self.normalize_filename(filename)
                
                if new_filename != filename:
                    new_path = root_path / new_filename
                    items_to_rename.append((old_path, new_path))
                    
            # 处理文件夹
            for dirname in dirs:
                old_path = root_path / dirname
                new_dirname = self.normalize_filename(dirname)
                
                if new_dirname != dirname:
                    new_path = root_path / new_dirname
                    items_to_rename.append((old_path, new_path))
                    
        return items_to_rename
    
    def rename_item(self, old_path: Path, new_path: Path) -> bool:
        """
        重命名单个项目
        
        Args:
            old_path: 原路径
            new_path: 新路径
            
        Returns:
            是否成功
        """
        try:
            if new_path.exists():
                logger.warning(f"目标已存在，跳过: {new_path}")
                self.skip_count += 1
                return False
                
            if self.dry_run:
                logger.info(f"[试运行] 将重命名: {old_path.name} -> {new_path.name}")
            else:
                old_path.rename(new_path)
                logger.info(f"✓ 重命名成功: {old_path.name} -> {new_path.name}")
                
            self.rename_count += 1
            return True
            
        except Exception as e:
            logger.error(f"✗ 重命名失败: {old_path.name} - {str(e)}")
            self.error_count += 1
            return False
    
    def run(self):
        """执行重命名操作"""
        logger.info("=" * 60)
        logger.info(f"开始处理目录: {self.root_dir}")
        logger.info(f"运行模式: {'试运行（不实际执行）' if self.dry_run else '正式执行'}")
        logger.info("=" * 60)
        
        # 收集所有需要重命名的项目
        items = self.collect_items()
        
        if not items:
            logger.info("未发现需要重命名的文件或文件夹")
            return
            
        logger.info(f"发现 {len(items)} 个需要重命名的项目")
        logger.info("-" * 60)
        
        # 执行重命名
        for old_path, new_path in items:
            self.rename_item(old_path, new_path)
            
        # 输出统计
        logger.info("=" * 60)
        logger.info("处理完成！统计信息：")
        logger.info(f"  成功重命名: {self.rename_count} 个")
        logger.info(f"  跳过: {self.skip_count} 个")
        logger.info(f"  失败: {self.error_count} 个")
        logger.info("=" * 60)


def main():
    """主函数"""
    import argparse
    from datetime import datetime
    
    parser = argparse.ArgumentParser(
        description='文件名规范化工具 - 将文件名中的特殊字符替换为下划线',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例：
  python ai_friendly_filename_normalizer.py                    # 处理当前目录
  python ai_friendly_filename_normalizer.py -d /path/to/dir    # 处理指定目录
  python ai_friendly_filename_normalizer.py --dry-run          # 试运行模式
  python ai_friendly_filename_normalizer.py -l rename.log      # 指定日志文件
  python ai_friendly_filename_normalizer.py -d /path/to/dir --dry-run --log rename.log
        """
    )
    
    parser.add_argument(
        '-d', '--dir',
        default='.',
        help='要处理的目录路径（默认：当前目录）'
    )
    
    parser.add_argument(
        '-l', '--log',
        default=None,
        help='日志文件路径（可选，默认只输出到控制台）'
    )
    
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='试运行模式，只显示将要执行的操作，不实际执行'
    )
    
    args = parser.parse_args()
    
    # 设置日志系统
    global logger
    logger = setup_logging(args.log)
    
    if args.log:
        logger.info(f"日志文件: {args.log}")
    
    # 检查目录是否存在
    target_dir = Path(args.dir).resolve()
    if not target_dir.exists():
        logger.error(f"目录不存在: {target_dir}")
        sys.exit(1)
        
    if not target_dir.is_dir():
        logger.error(f"路径不是目录: {target_dir}")
        sys.exit(1)
    
    # 创建规范化器并执行
    normalizer = FileNameNormalizer(str(target_dir), dry_run=args.dry_run)
    normalizer.run()


if __name__ == '__main__':
    main()
