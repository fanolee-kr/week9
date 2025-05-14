import os
from datetime import datetime
from google import genai
from PIL import Image
import io
from dotenv import load_dotenv

# .env 파일에서 환경 변수 로드
load_dotenv()

# Google API 키 설정
api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    raise ValueError("GEMINI_API_KEY 환경 변수를 설정해주세요.")

# Gemini API 클라이언트 설정
client = genai.Client(api_key=api_key)

def combine_images(img_path1, img_path2, output_path=None):
    """
    두 이미지를 좌우로 합치는 함수
    
    Args:
        img_path1: 첫 번째 이미지 경로 (식당 정보)
        img_path2: 두 번째 이미지 경로 (요일별 메뉴)
        output_path: 합친 이미지 저장 경로 (선택 사항)
        
    Returns:
        합쳐진 이미지 객체
    """
    # 이미지 로드
    img1 = Image.open(img_path1)
    img2 = Image.open(img_path2)
    
    # 높이가 다른 경우 더 높은 쪽에 맞춤
    max_height = max(img1.height, img2.height)
    
    # 이미지 리사이징 (높이만 맞추고 너비는 유지)
    if img1.height != max_height:
        new_width = int(img1.width * (max_height / img1.height))
        img1 = img1.resize((new_width, max_height), Image.LANCZOS)
    
    if img2.height != max_height:
        new_width = int(img2.width * (max_height / img2.height))
        img2 = img2.resize((new_width, max_height), Image.LANCZOS)
    
    # 새 이미지 생성 (두 이미지의 너비 합)
    combined_width = img1.width + img2.width
    combined_img = Image.new('RGB', (combined_width, max_height))
    
    # 이미지 붙이기 (좌우로)
    combined_img.paste(img1, (0, 0))
    combined_img.paste(img2, (img1.width, 0))
    
    # 합친 이미지 저장 (선택 사항)
    if output_path:
        combined_img.save(output_path)
        print(f"합친 이미지가 {output_path}에 저장되었습니다.")
    
    return combined_img

def ocr_with_gemini(image, date=None):
    """
    Gemini를 사용하여 이미지에서 메뉴 정보를 추출하는 함수
    
    Args:
        image: 이미지 객체
        date: 날짜 문자열 (기본값: 오늘 날짜)
        
    Returns:
        추출된 메뉴 정보
    """
    if date is None:
        date = datetime.now().strftime("%Y-%m-%d")
    
    # 이미지를 임시 파일로 저장
    temp_image_path = "temp_combined_image.png"
    image.save(temp_image_path)
    
    # 이미지 파일 업로드
    image_file = client.files.upload(file=temp_image_path)
    
    # 프롬프트 구성
    prompt = f'''이 이미지는 주간 구내식당 메뉴표입니다. 표 형식으로 구성되어 있으며, 각 열은 요일(월요일부터 금요일)을 나타내고, 각 행은 식사 종류(아침, 점심, 저녁 등)와 메뉴를 나타냅니다.
        
다음 작업을 수행해주세요:
1. 이미지의 표에서 {date} 일자의 점심 메뉴를 정확하게 추출해주세요 
2. 해당 일자의 메뉴는 일자 구분과 같은 열에 위치합니다.
3. 각 메뉴 항목의 이름과 칼로리 정보(있는 경우)를 구분하여 추출해주세요.
4. 오늘의 점심 메뉴를 추출해서 직원들한테 메세지로 전달할 수 있도록 만들어주세요

다음은 샘플입니다.

**🥗 중식 (11:30 ~ 13:00)**

*   **[소담스레 한식]** (912Kcal)
    *   메뉴1
    *   메뉴2
    *   ...
    *   ...
*   **[오감만족 일품면]** (816Kcal)
    *   메뉴1
    *   메뉴2
    *   ...
    *   ...
*   **[상상세계 직화양식]** (978Kcal)
    *   메뉴1
    *   메뉴2
    *   ...
    *   ...
*   **[Take out Zone]**
    *   도시락팩: 메뉴1 (Kcal)
    *   비건샐러드: 메뉴2 (Kcal)
    *   토핑샐러드: 메뉴3 (Kcal)
    *   헬시팩: 메뉴4 (Kcal)
    *   샌드위치: 메뉴5 (별도표기)
    *   즉석빵: 메뉴6 & 메뉴7 (Kcal)
'''
    
    # Gemini API 호출
    response = client.models.generate_content(
        model='gemini-1.5-flash',
        contents=[image_file, prompt],
    )
    
    # 임시 파일 삭제
    try:
        os.remove(temp_image_path)
    except:
        pass
    
    return response.text

def process_day_menu(day_num, output_dir='./output', save_combined=True):
    """
    특정 요일의 메뉴 이미지를 처리하는 함수
    
    Args:
        day_num: 요일 번호 (1: 월요일, 2: 화요일, ...)
        output_dir: 이미지 디렉토리
        save_combined: 합친 이미지 저장 여부
        
    Returns:
        추출된 메뉴 정보
    """
    restaurant_img = os.path.join(output_dir, '0.png')
    day_img = os.path.join(output_dir, f'{day_num}.png')
    
    combined_img_path = None
    if save_combined:
        combined_img_path = os.path.join(output_dir, f'combined_{day_num}.png')
    
    day_names = {1: '월요일', 2: '화요일', 3: '수요일', 4: '목요일', 5: '금요일'}
    day_name = day_names.get(day_num, f'{day_num}번째 날')
    
    # 이미지 합치기
    combined_img = combine_images(restaurant_img, day_img, combined_img_path)
    
    # 날짜 설정 (요일 정보로 대체, 실제 날짜로 변환하려면 추가 로직 필요)
    date = day_name
    
    # Gemini로 OCR 수행
    result = ocr_with_gemini(combined_img, date)
    
    print(f"===== {day_name} 메뉴 OCR 결과 =====")
    print(result)
    print("="*30)
    
    # 결과를 텍스트 파일로 저장
    result_path = os.path.join(output_dir, f'menu_{day_num}.md')
    with open(result_path, 'w', encoding='utf-8') as f:
        f.write(result)
    print(f"메뉴 정보가 {result_path}에 저장되었습니다.")
    
    return result

if __name__ == "__main__":
    # 월요일 메뉴 처리 (0.png + 1.png)
    process_day_menu(1)
    
    # 다른 요일도 처리하려면 아래 주석을 해제하세요
    # for day in range(2, 6):
    #     process_day_menu(day) 