import webcolors
import numpy as np
import math
from skimage.color import rgb2lab

# ==========================================
# 1. 放入你要测试的 "核心业务逻辑"
# ==========================================
def test_season_mapping(L, a, b):
    """这里放你想要测试的判定逻辑"""
    # matched_seasons = []
    # undertone_diff = b - a 
    
    # # 打印核心中间变量 (这就是探针的意义所在)
    # print(f"  [探针内部数据] Undertone Diff (b-a): {undertone_diff:.2f}")

    # --- 你的判断树 ---
    # if L >= 70:
    #     if undertone_diff > 5:
    #         matched_seasons.extend([6, 5]) # Light/Warm Spring
    #     elif undertone_diff < 0:
    #         matched_seasons.extend([7, 8]) # Light/Cool Summer
    #     else:
    #         matched_seasons.extend([6, 7]) # Neutral Light
    # elif L < 45:
    #     if b > 12 or (a + b) > 25:
    #         matched_seasons.extend([12, 11])
    #     elif b < 8:
    #         matched_seasons.extend([1, 2])
    #     else:
    #         matched_seasons.extend([1, 12])
    # else:
    #     if undertone_diff > 5: 
    #         matched_seasons.extend([11, 10])
    #     elif undertone_diff < -2:
    #         matched_seasons.extend([8, 9])
    #     else:
    #         matched_seasons.extend([9, 10])

    # return list(set(matched_seasons))
    # if L < 50 and (a + b) > 25:
    #     # Bronzy/Mahogany: unmistakably Dark Autumn or True Autumn
    #     matched_seasons.extend([9, 8])  # Dark Autumn, True Autumn
    #     return list(set(matched_seasons))

    # # ==========================================
    # # 1. Cool / Pink Undertone  (b - a < 0)
    # # ==========================================
    # if undertone_diff < 0:
    #     matched_seasons.extend([5, 11])  # True Summer, True Winter

    #     if L >= 68:
    #         matched_seasons.append(4)   # Light Summer
    #         matched_seasons.append(12)  # Bright Winter (clear, cool, light)

    #     if L < 45:
    #         matched_seasons.append(10)  # Dark Winter

    # # ==========================================
    # # 2. Warm / Golden Undertone  (b - a > 6)
    # # ==========================================
    # elif undertone_diff > 6:
    #     matched_seasons.extend([2, 8])  # True Spring, True Autumn

    #     if L >= 68:
    #         matched_seasons.append(3)   # Light Spring
    #         matched_seasons.append(1)   # Bright Spring

    #     if L < 45:
    #         matched_seasons.append(9)   # Dark Autumn

    # # ==========================================
    # # 3. Neutral / Olive Undertone  (0 <= b - a <= 6)
    # # ==========================================
    # else:
    #     matched_seasons.extend([6, 7])  # Soft Summer, Soft Autumn

    #     if L >= 68:
    #         matched_seasons.extend([3, 4])  # Light Spring, Light Summer

    #     if L < 45:
    #         matched_seasons.extend([9, 10])  # Dark Autumn, Dark Winter

    ## lip stick
    matched_seasons = []
    
    # 防止 a 为 0 导致除以零报错 (虽然口红里 a 基本不可能为 0)
    safe_a = abs(a) + 0.0001
    
    # 1. 计算 Chroma (饱和度/净度)
    chroma = math.sqrt(a**2 + b**2)
    hue_ratio = b / safe_a
    
   # --- 维度 1: 判定明暗 (Depth) ---
    # 稍微放宽口红的深浅门槛
    depth = "medium"
    if L > 55: depth = "light"
    elif L < 45: depth = "deep"

    # --- 维度 2: 判定温度 (Temperature) ---
    temp = "neutral"
    if hue_ratio > 0.40: temp = "warm"     # 橘红、砖红、焦糖色
    elif hue_ratio < 0.20: temp = "cool"   # 玫红、浆果色、紫红

    # --- 维度 3: 判定饱和度 (Clarity) ---
    clarity = "medium"
    if chroma > 48: clarity = "bright"
    elif chroma < 32: clarity = "soft"

    # ==========================================
    # 核心决策树：以 Depth 为第一优先级
    # ==========================================
    if depth == "deep":
        # 深色口红：Dark Autumn, Dark Winter 的绝对主场
        if temp == "warm":
            matched_seasons.extend([9, 8]) # Dark Autumn, True Autumn
            if clarity == "bright": matched_seasons.append(2) # True Spring 也可驾驭部分深亮红
        elif temp == "cool":
            matched_seasons.extend([10, 11]) # Dark Winter, True Winter
            if clarity == "bright": matched_seasons.append(12) # Bright Winter
        else: # Neutral
            matched_seasons.extend([9, 10]) # Dark Autumn, Dark Winter
            if clarity == "bright": matched_seasons.extend([12, 1]) # 极艳丽的深中性红 (如牛血色)

    elif depth == "light":
        # 浅色口红：Spring 和 Summer 的主场
        if temp == "warm":
            matched_seasons.extend([3, 2]) # Light Spring, True Spring
            if clarity == "soft": 
                # 完美契合理论: Dark Autumn 的 lighter lipsticks (burnt oranges)
                matched_seasons.extend([7, 9]) # Soft Autumn, Dark Autumn
        elif temp == "cool":
            matched_seasons.extend([4, 5]) # Light Summer, True Summer
            if clarity == "soft": matched_seasons.extend([6]) # Soft Summer
        else: # Neutral
            matched_seasons.extend([3, 4]) # Light Spring, Light Summer
            if clarity == "soft": matched_seasons.extend([6, 7]) # Soft Summer, Soft Autumn

    else: # medium
        # 中等明暗：各季节大乱斗，看饱和度
        if temp == "warm":
            if clarity == "bright":
                matched_seasons.extend([1, 2]) # Bright Spring, True Spring
            elif clarity == "soft":
                matched_seasons.extend([8, 7, 9]) # True Autumn, Soft Autumn, Dark Autumn (焦糖色)
            else:
                matched_seasons.extend([8, 2, 9]) # True Autumn, True Spring, Dark Autumn
        elif temp == "cool":
            if clarity == "bright":
                matched_seasons.extend([12, 11]) # Bright Winter, True Winter
            elif clarity == "soft":
                matched_seasons.extend([5, 6, 10]) # True Summer, Soft Summer, Dark Winter
            else:
                matched_seasons.extend([5, 11, 10]) # True Summer, True Winter, Dark Winter
        else: # Neutral
            if clarity == "bright":
                matched_seasons.extend([1, 12]) # Bright Spring, Bright Winter (正红色)
            elif clarity == "soft":
                matched_seasons.extend([6, 7]) # Soft Summer, Soft Autumn (豆沙色)
            else:
                matched_seasons.extend([8, 11, 9, 10]) # True Autumn, True Winter, Dark Autumn, Dark Winter
    return list(set(matched_seasons))

# ==========================================
# 2. 封装探针执行器 (帮你做基础转换和日志打印)
# ==========================================
def run_probe(hex_code, description="Test Target"):
    print(f"\n{'='*40}")
    print(f"🎯 探针启动: {description}")
    print(f"Hex Code: {hex_code}")
    print(f"{'-'*40}")

    try:
        # 转换逻辑
        rgb_uint8 = webcolors.hex_to_rgb(hex_code)
        rgb_norm = np.array([[[c / 255.0 for c in rgb_uint8]]], dtype=np.float64)
        lab = rgb2lab(rgb_norm)[0][0]
        L, a, b = float(lab[0]), float(lab[1]), float(lab[2])
        
        print(f"📊 物理色彩数据:")
        print(f"  L* (明暗): {L:.2f}")
        print(f"  a* (红绿): {a:.2f}")
        print(f"  b* (黄蓝): {b:.2f}")
        print(f"{'-'*40}")

        # 运行核心逻辑
        print("⚙️ 执行决策树逻辑:")
        result_ids = test_season_mapping(L, a, b)
        
        # 解释结果
        season_dict = {
            1: "Bright Spring", 2: "True Spring", 3: "Light Spring",
            4: "Light Summer", 5: "True Summer", 6: "Soft Summer",
            7: "Soft Autumn", 8: "True Autumn", 9: "Dark Autumn",
            10: "Dark Winter", 11: "True Winter", 12: "Bright Winter"
        }
        result_names = [season_dict.get(sid, "Unknown") for sid in result_ids]
        
        print(f"{'-'*40}")
        print(f"✅ 最终判定 Season IDs: {result_ids}")
        print(f"🎨 映射结果: {result_names}")
        print(f"{'='*40}\n")

    except Exception as e:
        print(f"❌ 探针执行失败: {e}")

# ==========================================
# 3. 提供控制变量 (喂数据)
# ==========================================
if __name__ == "__main__":
    # 你可以在这里放入任何你想测试的色号
    
    # 1. Cool Winter Fair
    # run_probe("#EEDBD7", description="fair1")
    # run_probe("#E9CEAB", description="fair2")
    # run_probe("#754F4E", description="fair3")
    # run_probe("#D6B096", description="fair4")
    # run_probe("#CA9374", description="fair5")

    # 2. Light Summer Fair
    # run_probe("#E1AB82", description="fair1")
    # run_probe("#DAAB87", description="fair2")
    # run_probe("#EDD0A8", description="fair3")
    # run_probe("#F5DAC9", description="fair4")
    # run_probe("#F5E6DB", description="fair5")
    # run_probe("#EACFAB", description="fair6")

    # 3. Warm Spring Fair
    # run_probe("#F8DFC1", description="fair1")
    # run_probe("#EDD6A8", description="fair2")
    # run_probe("#E2B681", description="fair3")
    # run_probe("#C58857", description="fair4")

    # 4. Deep Autamn Fair
    # run_probe("#EDD3A8", description="fair1")
    # run_probe("#EDD0A8", description="fair2")
    # run_probe("#E2B081", description="fair3")
    # run_probe("#E1AB82", description="fair4")
    # run_probe("#C58357", description="fair5")
    # run_probe("#C57B57", description="fair6")
    # run_probe("#855942", description="fair7")
    # run_probe("#855042", description="fair8")
    # run_probe("#5A3E28", description="fair9")
    # run_probe("#5A3828", description="fair10")
    # run_probe("#563028", description="fair11")

    # 4. Soft Autamn Fair
    # run_probe("#EDD0A8", description="fair1")
    # run_probe("#C57B57", description="fair2")
    # run_probe("#804F45", description="fair3")
    # run_probe("#473034", description="fair4")
    # run_probe("#52302C", description="fair5")
    # run_probe("#563028", description="fair6")
    # run_probe("#F5DAC9", description="fair7")

    # test 1
    # run_probe("#E8B99A", description="Very Fair 02")
    # run_probe("#E9B894", description="Very Fair 04")
    # run_probe("#E4AD85", description="Very Fair 05")
    # run_probe("#E3AB7F", description="Very Fair 06")
    # run_probe("#DFAC8B", description="Very Fair 07")
    # run_probe("#E4AD87", description="Very Fair 08")
    # run_probe("#DCA68A", description="Moderately Fair 10")
    # run_probe("#CF916B", description="Moderately Fair 12")
    # run_probe("#D59972", description="Moderately Fair 14")
    # run_probe("#D3936C", description="Medium 16")
    # run_probe("#CD9571", description="Medium 18")
    # run_probe("#C58F64", description="Medium 20")
    # run_probe("#BF8562", description="Medium 22")
    # run_probe("#CB8964", description="Medium 15")
    # run_probe("#BA7F53", description="Deep 24")
    # run_probe("#E5855E", description="Apricot Corrector")
    # run_probe("#996454", description="Deep 26")
    # run_probe("#8b594c", description="Deep 28")


    run_probe("#b72227", description="Bee's Knees")
    run_probe("#BB656B", description="Brain Freeze")
    run_probe("#8E4140", description="Drip")
    run_probe("#A12A33", description="On a Stick")
    run_probe("#904550", description="Ice Cube")
    run_probe("#452222", description="Lolly")
    run_probe("#7C3F35", description="Candyfloss")

    # test 2
    # run_probe("#AE0F37", description="1")
    # run_probe("#FBBEAE", description="2")
    # run_probe("#CE5044", description="3")
    # run_probe("#F78180", description="4")
    # run_probe("#D75C5D", description="5")
    # run_probe("#7E3840", description="6")
    # run_probe("#6B3331", description="7")
    # run_probe("#BA4A4E", description="8")
    # run_probe("#781F2D", description="9")
    # run_probe("#FFC4B6", description="10")

    # test 3
    # run_probe("#AB5E98", description="1")
    # run_probe("#642B61", description="2")
    # run_probe("#D97AA3", description="3")
    # run_probe("#9E2C69", description="4")
    # run_probe("#6C234C", description="5")
    # run_probe("#A5234F", description="6")
    # run_probe("#92316F", description="7")
    # run_probe("#C82152", description="8")
    # run_probe("#CB4385", description="9")
    # run_probe("#DE9AC3", description="10")

    # 测试案例 3：你可以随时加新的 Hex 来验证你的算法
    # run_probe("#YOUR_HEX", description="My Test")