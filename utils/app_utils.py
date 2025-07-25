from base.electron_pc_base import ElectronPCBase

def start_securenet_win_app():
    base = ElectronPCBase() #启动应用
    driver = base.start_app()  # 启动应用并返回 driver 对象
    return driver

