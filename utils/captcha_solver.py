import base64
import numpy as np
from io import BytesIO
from PIL import Image
from selenium.webdriver import ActionChains
from selenium.webdriver.common.by import By
import cv2


def gap_y_to_x(y, bg_image):
    return 250  # 未找到时返回None
class CaptchaSolver:

    def __init__(self, driver):
        self.driver = driver
        self.retry_limit = 3
        self.slider_locator = (By.CSS_SELECTOR, '.verify-move-block')  # 根据实际结构调整

    def _get_puzzle_image(self):
        """专业级图像获取方法"""
        img_element = self.driver.find_element(
            By.CSS_SELECTOR, '.verify-img-panel img')
        img_data = img_element.get_attribute('src').split(',')[1]
        return Image.open(BytesIO(base64.b64decode(img_data)))

    def _analyze_gap_position(self, bg_image):
        """识别所有缺口位置"""
        gray = cv2.cvtColor(np.array(bg_image), cv2.COLOR_BGR2GRAY)
        edges = cv2.Canny(gray, 100, 200)

        # 垂直投影分析
        vertical_projection = np.sum(edges, axis=1)

        # 检测缺口区域，使用阈值来过滤出显著的缺口
        threshold = np.max(vertical_projection) * 0.1  # 设定阈值
        gap_positions_y = np.where(vertical_projection > threshold)[0]

        # 对每个有效的缺口位置进行 X 轴的计算，您可以设定具体的 X 轴位置
        gap_positions_x = [gap_y_to_x(y, bg_image) for y in gap_positions_y]

        if len(gap_positions_x) == 0:
            return None  # None, 如果未发现缺口

        return gap_positions_x  # 返回所有缺口的位置

    def _generate_humanized_trajectory(self, distance):
        """拟人化轨迹生成算法"""
        base_speed = 2.0  # 提升基础速度系数
        acceleration = 0.8  # 增强加速力度
        deceleration_start = 0.7  # 更晚开始减速

        trajectory = []
        current = 0
        v = base_speed  # 初始速度提升

        while current < distance:
            progress = current / distance

            # 动态速度调节
            if progress < deceleration_start:
                # 强化加速阶段
                v += (np.random.rand() * 0.5 + 0.8) * acceleration
            else:
                # 平滑减速
                v *= 0.7 - (progress * 0.1)

            # 添加噪声（保持随机性）
            v += np.random.uniform(-1.5, 1.5)
            v = max(3, min(v, 25))  # 提高速度上限

            # 计算实际步长
            step = v * base_speed
            remaining = distance - current
            step = min(step, remaining)

            # 时间间隔优化（更紧凑）
            interval = np.random.uniform(0.005, 0.02) if step > 5 else np.random.uniform(0.03, 0.07)

            # 智能微停顿（降低触发概率）
            if np.random.rand() > 0.9:  # 10%概率微停顿
                interval += np.random.uniform(0.03, 0.1)
                step *= 0.7

            trajectory.append((step, interval))
            current += step

        # 添加惯性滑动特征
        if distance - current > 0:
            trajectory.append((distance - current, 0.01))

        return trajectory

    def solve(self):
        """主处理方法（含重试机制）"""
        for attempt in range(self.retry_limit):
            try:
                bg_image = self._get_puzzle_image()
                gap_positions_x = self._analyze_gap_position(bg_image)

                # 检查找到的缺口位置
                print(f"检测到拼图缺口X轴坐标: {gap_positions_x}")  # 调试信息
                if not gap_positions_x:
                    print("未能识别缺口位置，重试...")
                    continue

                # 选择最小的X坐标作为目标
                target_gap_x = min(gap_positions_x)  # 找到目标缺口的 X 坐标
                print(f"选择的目标缺口X轴坐标: {target_gap_x}")  # 调试信息
                slider = self.driver.find_element(By.CLASS_NAME, 'verify-move-block')

                actual_distance = target_gap_x  # 使用目标缺口位置
                print(f"计算的实际移动距离: {actual_distance}")  # 调试信息

                actions = ActionChains(self.driver)
                actions.click_and_hold(slider)

                total_moved = 0  # 用于记录已移动距离
                for step, interval in self._generate_humanized_trajectory(actual_distance):
                    actions.move_by_offset(step, 0)
                    actions.pause(interval)
                    total_moved += step
                    print(f"已移动距离: {total_moved}, 当前步长: {step}, 目标距离: {actual_distance}")  # 调试信息
                # 在滑动结束前，进行最后的小步调整，增加停顿
                # final_adjust_for_stop = 5  # 可以调整这个值
                # actions.move_by_offset(final_adjust_for_stop, 0)
                actions.pause(0.1)  # 对应小停顿

                actions.release().perform()
                return True
            except Exception as e:
                print(f"验证尝试 {attempt + 1} 失败: {str(e)}")
