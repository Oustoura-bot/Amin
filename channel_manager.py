# -*- coding: utf-8 -*-
import os
import re
import sys
import json

BASE_PATH = "/home/ubuntu/tv-logos/countries"

def get_countries():
    """أخذ قائمة الدول المتاحة من المجلدات."""
    try:
        countries = [d for d in os.listdir(BASE_PATH) if os.path.isdir(os.path.join(BASE_PATH, d))]
        # تحسين أسماء الدول (استبدال الشرطة بمسافة وتحويل الحرف الأول لكبير)
        formatted_countries = [country.replace('-', ' ').title() for country in countries]
        # إزالة الدول العالمية مؤقتاً لتبسيط القائمة
        formatted_countries = [c for c in formatted_countries if not c.lower().startswith('world')]
        return sorted(formatted_countries)
    except FileNotFoundError:
        # print(f"Error: Base path {BASE_PATH} not found.")
        raise FileNotFoundError(f"Base path {BASE_PATH} not found.")
    except Exception as e:
        # print(f"An error occurred while listing countries: {e}")
        raise Exception(f"An error occurred while listing countries: {e}")

def get_original_country_name(formatted_country_name):
    """تحويل اسم الدولة المنسق إلى اسم المجلد الأصلي."""
    return formatted_country_name.lower().replace(' ', '-')

def get_channels(country_formatted_name):
    """أخذ قائمة القنوات لدولة معينة."""
    country_original_name = get_original_country_name(country_formatted_name)
    country_path = os.path.join(BASE_PATH, country_original_name)
    channels = set() # استخدام مجموعة لمنع التكرار
    try:
        if not os.path.isdir(country_path):
            # print(f"Error: Country directory not found: {country_path}")
            raise FileNotFoundError(f"Country directory not found: {country_path}")

        for filename in os.listdir(country_path):
            if filename.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.webp')):
                name_part = os.path.splitext(filename)[0]
                cleaned_name = re.sub(r'-(?:[a-zA-Z]{2,3}|icon|hz|plus|white|hd|sd|fhd|uhd|logo|alt|dark|light|\d{4})$', '', name_part, flags=re.IGNORECASE)
                cleaned_name = re.sub(r'_dark$', '', cleaned_name, flags=re.IGNORECASE) # إزالة لاحقة شائعة أخرى
                channel_name = cleaned_name.replace('-', ' ').replace('_', ' ').strip().title()
                # تجاهل الأسماء القصيرة جداً أو التي تبدو كرموز
                if channel_name and len(channel_name) > 1 and not channel_name.isdigit():
                    channels.add(channel_name)

        return sorted(list(channels))
    except FileNotFoundError as e:
        raise e
    except Exception as e:
        # print(f"An error occurred while listing channels for {country_formatted_name}: {e}")
        raise Exception(f"An error occurred while listing channels for {country_formatted_name}: {e}")

def find_logo_file(country_formatted_name, channel_formatted_name):
    """العثور على ملف الشعار المطابق لاسم القناة."""
    country_original_name = get_original_country_name(country_formatted_name)
    country_path = os.path.join(BASE_PATH, country_original_name)
    search_term = channel_formatted_name.lower().replace(' ', '-')

    try:
        if not os.path.isdir(country_path):
            # print(f"Error: Country directory not found: {country_path}")
            raise FileNotFoundError(f"Country directory not found: {country_path}")

        best_match = None
        min_len_diff = float('inf')
        best_match_is_variant = True # افتراض أن أول تطابق قد يكون متغيراً

        # قائمة الملفات المرشحة
        candidate_files = [f for f in os.listdir(country_path) if f.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.webp'))]

        # المرحلة الأولى: البحث عن تطابق يبدأ بالاسم ويفضل غير المتغيرات
        for filename in candidate_files:
            name_part = os.path.splitext(filename)[0].lower()
            if name_part.startswith(search_term):
                len_diff = len(name_part) - len(search_term)
                is_variant = any(variant in name_part for variant in ['-icon', '-hz', '-plus', '-white', '-hd', '-sd', '-fhd', '-uhd', '-logo', '-alt', '-dark', '-light', '_dark'])

                # تحديث أفضل تطابق
                if best_match is None or len_diff < min_len_diff or (len_diff == min_len_diff and not is_variant and best_match_is_variant):
                    min_len_diff = len_diff
                    best_match = filename
                    best_match_is_variant = is_variant
                # إذا وجدنا تطابقاً تاماً غير متغير، نستخدمه مباشرة
                if len_diff == 0 and not is_variant:
                    best_match = filename
                    break

        # المرحلة الثانية: إذا لم نجد تطابقاً جيداً، نبحث عن أي ملف يحتوي على الاسم
        if best_match is None:
            # محاولة البحث عن الاسم ككلمة كاملة (محاط بشرطات أو بداية/نهاية)
            pattern = r'(?:^|-|_)(' + re.escape(search_term) + r')(?:-|_|$)'
            for filename in candidate_files:
                name_part = os.path.splitext(filename)[0].lower()
                if re.search(pattern, name_part):
                    best_match = filename
                    break # نأخذ أول تطابق
            # إذا لم نجد كلمة كاملة، نبحث عن أي احتواء
            if best_match is None:
                 for filename in candidate_files:
                    name_part = os.path.splitext(filename)[0].lower()
                    if search_term in name_part:
                        best_match = filename
                        break # نأخذ أول تطابق

        if best_match:
            return os.path.join(country_path, best_match)
        else:
            return None # لم يتم العثور على أي تطابق

    except FileNotFoundError as e:
        raise e
    except Exception as e:
        # print(f"An error occurred while finding logo for {channel_formatted_name} in {country_formatted_name}: {e}")
        raise Exception(f"An error occurred while finding logo for {channel_formatted_name} in {country_formatted_name}: {e}")

# --- التعامل مع وسائط سطر الأوامر --- 
if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(json.dumps({"error": "No function specified"}))
        sys.exit(1)

    func_name = sys.argv[1]
    args = sys.argv[2:]
    result = None
    error_msg = None

    try:
        if func_name == "get_countries":
            result = get_countries()
        elif func_name == "get_channels":
            if len(args) == 1:
                result = get_channels(args[0])
            else:
                error_msg = "Missing country name argument for get_channels"
        elif func_name == "find_logo_file":
            if len(args) == 2:
                result = find_logo_file(args[0], args[1])
            else:
                error_msg = "Missing country and channel name arguments for find_logo_file"
        else:
            error_msg = f"Unknown function: {func_name}"
    except FileNotFoundError as e:
        error_msg = str(e)
    except Exception as e:
        error_msg = f"Error executing {func_name}: {str(e)}"

    if error_msg:
        print(json.dumps({"error": error_msg}))
        sys.exit(1)
    else:
        print(json.dumps({"result": result}))
        sys.exit(0)

