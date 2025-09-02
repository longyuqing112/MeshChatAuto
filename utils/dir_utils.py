def resolve_media_path(relative_path):
    """将相对路径解析为绝对路径"""
    import os
    current_dir = os.path.dirname(os.path.abspath(__file__))
    base_dir = os.path.abspath(os.path.join(current_dir, ".."))
    abs_path = os.path.abspath(os.path.join(base_dir, relative_path))
    # 验证文件是否存在
    # 验证文件是否存在
    if not os.path.exists(abs_path):
        print(f"警告: 文件不存在 {abs_path}")

    return abs_path

def resolve_media_paths(relative_paths):
    """批量处理相对路径列表"""
    if not relative_paths:
        return []
    return [resolve_media_path(path) for path in relative_paths]