import cv2
import numpy as np
import os

def split_menu_by_day(image_path, output_dir="./output"):
    """
    급식 메뉴 이미지를 요일별로 자르는 함수
    
    Args:
        image_path (str): 메뉴 이미지 파일 경로
        output_dir (str): 잘린 이미지를 저장할 디렉토리
    """
    # 이미지 로드
    img = cv2.imread(image_path)
    if img is None:
        print(f"이미지를 불러올 수 없습니다: {image_path}")
        returns
    
    # 출력 디렉토리 생성
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    # 이미지 전체 너비 구하기
    height, width, _ = img.shape
    
    # 요일 이름 (파일명용)
    day_names = ["월요일", "화요일", "수요일", "목요일", "금요일"]
    
    # 5등분하여 각 요일별 영역 계산 및 저장
    col_width = width // 5
    
    for i in range(5):
        # 열 좌표 계산
        start_x = i * col_width
        end_x = (i + 1) * col_width if i < 4 else width  # 마지막 열은 이미지 끝까지
        
        # 열 추출
        day_img = img[:, start_x:end_x]
        
        # 저장
        output_path = os.path.join(output_dir, f"{day_names[i]}.png")
        cv2.imwrite(output_path, day_img)
        print(f"{day_names[i]} 메뉴 저장 완료: {output_path}")


def split_menu_by_day_advanced(image_path, output_dir="./output"):
    """
    급식 메뉴 이미지를 테이블 경계 감지를 사용하여 요일별로 자르는 함수
    
    Args:
        image_path (str): 메뉴 이미지 파일 경로
        output_dir (str): 잘린 이미지를 저장할 디렉토리
    """
    # 이미지 로드
    img = cv2.imread(image_path)
    if img is None:
        print(f"이미지를 불러올 수 없습니다: {image_path}")
        return
    
    # 출력 디렉토리 생성
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    # 이미지 크기 정보 얻기
    height, width, _ = img.shape
    
    # 그레이스케일 변환
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    
    # 에지 감지
    edges = cv2.Canny(gray, 50, 150, apertureSize=3)
    
    # 직선 감지 (수직선 찾기)
    lines = cv2.HoughLinesP(edges, 1, np.pi/180, threshold=100, minLineLength=height*0.6, maxLineGap=20)
    
    # 수직선 필터링
    vertical_lines = []
    
    if lines is not None:
        for line in lines:
            x1, y1, x2, y2 = line[0]
            # 수직에 가까운 선만 선택 (x 좌표 차이가 작은 경우)
            if abs(x1 - x2) < 20:
                vertical_lines.append((min(x1, x2), max(x1, x2)))
    
    # 수직선 x좌표 정렬
    vertical_lines.sort()
    
    # 열 경계 감지
    col_boundaries = [0]  # 이미지 시작점
    
    # 인접한 경계선 병합
    if vertical_lines:
        for i in range(len(vertical_lines)):
            x_avg = (vertical_lines[i][0] + vertical_lines[i][1]) // 2
            # 이전 경계와 충분히 떨어져 있는지 확인
            if not col_boundaries or (x_avg - col_boundaries[-1] > width * 0.1):
                col_boundaries.append(x_avg)
    
    # 이미지 끝점 추가
    col_boundaries.append(width)
    
    # 요일 이름 (파일명용)
    day_names = ["월요일", "화요일", "수요일", "목요일", "금요일"]
    
    # 감지된 경계가 충분하지 않으면 기본 방식으로 분할
    if len(col_boundaries) < 6:
        print("테이블 경계를 충분히 감지하지 못했습니다. 기본 분할 방식을 사용합니다.")
        split_menu_by_day(image_path, output_dir)
        return
    
    # 요일별로 이미지 자르기
    for i in range(5):
        # 열 좌표 계산
        start_x = col_boundaries[i]
        end_x = col_boundaries[i + 1]
        
        # 열 추출
        day_img = img[:, start_x:end_x]
        
        # 저장
        output_path = os.path.join(output_dir, f"{day_names[i]}.png")
        cv2.imwrite(output_path, day_img)
        print(f"{day_names[i]} 메뉴 저장 완료: {output_path}")


if __name__ == "__main__":
    # 이미지 파일 경로
    image_path = "menu.png"
    
    # 기본 분할 방식 사용
    split_menu_by_day(image_path)
    
    # 고급 분할 방식 사용 (테이블 경계 감지)
    # split_menu_by_day_advanced(image_path, "./output_advanced") 