#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
并行处理器 - 工具模块

负责实现文件的并行处理功能，提高多文件处理效率
"""

import concurrent.futures
import time
from typing import List, Dict, Any, Callable


def process_files_in_parallel(
    file_paths: List[str], 
    process_func: Callable[[str], Dict[str, Any]],
    max_workers: int = 4
) -> List[Dict[str, Any]]:
    """并行处理多个文件

    Args:
        file_paths: 文件路径列表
        process_func: 处理单个文件的函数
        max_workers: 最大工作线程数

    Returns:
        List[Dict[str, Any]]: 处理结果列表
    """
    start_time = time.time()
    results = []

    # 使用线程池并行处理文件
    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        # 提交所有任务
        future_to_file = {
            executor.submit(process_func, file_path): file_path 
            for file_path in file_paths
        }

        # 收集结果
        for future in concurrent.futures.as_completed(future_to_file):
            file_path = future_to_file[future]
            try:
                result = future.result()
                results.append(result)
            except Exception as e:
                results.append({
                    "success": False,
                    "message": f"处理文件 {file_path} 时出错: {str(e)}"
                })

    total_time = time.time() - start_time
    print(f"并行处理完成: {len(file_paths)} 个文件, 耗时: {total_time:.2f}秒")
    
    return results


def process_files_in_parallel_with_progress(
    file_paths: List[str], 
    process_func: Callable[[str], Dict[str, Any]],
    max_workers: int = 4,
    progress_callback: Callable[[int, int], None] = None
) -> List[Dict[str, Any]]:
    """带进度回调的并行文件处理

    Args:
        file_paths: 文件路径列表
        process_func: 处理单个文件的函数
        max_workers: 最大工作线程数
        progress_callback: 进度回调函数，接收(已完成数, 总数)参数

    Returns:
        List[Dict[str, Any]]: 处理结果列表
    """
    start_time = time.time()
    results = []
    completed_count = 0
    total_count = len(file_paths)

    # 使用线程池并行处理文件
    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        # 提交所有任务
        future_to_file = {
            executor.submit(process_func, file_path): file_path 
            for file_path in file_paths
        }

        # 收集结果
        for future in concurrent.futures.as_completed(future_to_file):
            file_path = future_to_file[future]
            try:
                result = future.result()
                results.append(result)
            except Exception as e:
                results.append({
                    "success": False,
                    "message": f"处理文件 {file_path} 时出错: {str(e)}"
                })
            finally:
                completed_count += 1
                if progress_callback:
                    progress_callback(completed_count, total_count)

    total_time = time.time() - start_time
    print(f"并行处理完成: {total_count} 个文件, 耗时: {total_time:.2f}秒")
    
    return results
