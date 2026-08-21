import os
import re
import sys
import logging
import requests

# 設置日誌輸出
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# 大陸頻道關鍵字過濾清單
CHINA_KEYWORDS = [
    'CCTV', '中央', '衛視', '衛視', '衛視台',
    '北京', '上海', '天津', '重慶', '河北', '山西', '遼寧', '吉林', '黑龍江',
    '江蘇', '浙江', '安徽', '福建', '江西', '山東', '河南', '湖北', '湖南',
    '廣東', '廣西', '海南', '四川', '貴州', '雲南', '陝西', '甘肅', '青海',
    '內蒙古', '西藏', '寧夏', '新疆', '東南', '深圳', '南方', '廈門'
]

def is_china_channel(channel_name, group_title=""):
    """判斷頻道名稱或分類是否包含大陸頻道關鍵字"""
    text_to_check = f"{channel_name} {group_title}".upper()
    for kw in CHINA_KEYWORDS:
        if kw.upper() in text_to_check:
            return True
    return False

def parse_and_filter_m3u(m3u_content):
    """解析並過濾 M3U 內容，排除大陸頻道"""
    lines = m3u_content.splitlines()
    filtered_lines = ["#EXTM3U"]
    
    current_extinf = None
    keep_current = False
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
            
        if line.startswith("#EXTINF:"):
            current_extinf = line
            # 擷取頻道名稱
            channel_name = line.split(",")[-1] if "," in line else ""
            
            # 擷取 group-title 分類
            group_match = re.search(r'group-title="([^"]*)"', line)
            group_title = group_match.group(1) if group_match else ""
            
            # 判斷是否非大陸頻道
            if not is_china_channel(channel_name, group_title):
                keep_current = True
            else:
                keep_current = False
                
        elif not line.startswith("#"):
            # 這是 URL 行
            if keep_current and current_extinf:
                filtered_lines.append(current_extinf)
                filtered_lines.append(line)
                current_extinf = None
                keep_current = False
                
    return "\n".join(filtered_lines)

def main():
    logger.info("開始下載與過濾 IPTV 播放清單...")
    
    # 預設來源網址 (可視需要更換為您常用的訂閱源)
    source_url = "https://iptv-org.github.io/iptv/index.m3u"
    
    try:
        response = requests.get(source_url, timeout=15)
        response.raise_for_status()
        content = response.text
        
        logger.info("成功取得原始清單，開始過濾大陸頻道...")
        filtered_m3u = parse_and_filter_m3u(content)
        
        # 建立 output 資料夾
        output_dir = "output"
        os.makedirs(output_dir, exist_ok=True)
        
        # 寫入過濾後的結果
        output_path = os.path.join(output_dir, "iptv_collection.m3u")
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(filtered_m3u)
            
        logger.info(f"處理完成！已成功輸出檔案至：{output_path}")
        
    except Exception as e:
        logger.error(f"程式執行出錯: {str(e)}", exc_info=True)
        sys.exit(1)

if __name__ == "__main__":
    main()
    
