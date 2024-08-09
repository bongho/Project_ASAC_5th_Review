import streamlit as st
import pandas as pd
import numpy as np
from streamlit_folium import folium_static
import folium


###### 페이지 설정 변경
st.set_page_config(
    page_title="ASAC_5th_Review",
    page_icon="🛵",
    layout="wide",  # 'wide' layout 사용
)
####### main 화면 ########
def show_main():
    # 페이지 타이틀 설정
    st.title("Welcome to ASAC-MAP")
    # 프로젝트 설명
    st.write("YELP 데이터셋을 활용한 고객 탐색경험 향상을 위한 키워드 요약 프로젝트")
    st.write("좌측에 가게 이름을 검색해주세요.")


####### show result 함수 #########
def show_result (business_name) :
    # 페이지 타이틀 설정
    st.title(f" {business_name}")
    
    ## 가게정보 
    # 컬럼 레이아웃 정의
    col1, col2, col3 = st.columns(3)

    # 첫 번째 컬럼에 이미지 추가
    with col1:
        image_url = "https://via.placeholder.com/200"  # 임의의 이미지 URL 사용
        st.image(image_url, caption='Store Image', width=200)


    # 두 번째 컬럼에 키워드 추가
    with col2:

        map_center = [37.5453577, 126.9525465]
        m = folium.Map(location=map_center, zoom_start=12,tiles = 'cartodbpositron',
            width='100%', height=200)
        folium.Marker(
            location=map_center,
            popup=f"{business_name} Location",
            tooltip="Click for more info",
            caption='Store Location'
            
        ).add_to(m)

        folium_static(m, width=400, height=200)  # Display the map in Streamlit
       

    with col3:
        st.write("")
    ## 가게 요약
    # 컬럼 레이아웃 정의
    col1, col2 = st.columns(2)

    # 첫 번째 컬럼에 이미지 추가
    with col1:
        st.subheader("Good")
        st.write("- Tasty Pasta")
        st.write("- Kind Waitress")
        st.write("- Cozy Atmosphere")

    # 두 번째 컬럼에 키워드 추가
    with col2:
        st.subheader("Bad")
        st.write("- Awful Location")
        st.write("- High Cost")
        st.write("- No Parking")

 
    # 데이터 생성 (임시 데이터)
    np.random.seed(1)
    data = pd.DataFrame({
        'Reviewer': np.random.choice(['Hoon', 'Hyeji', 'Eunji', 'Sehee'], 100),
        'Topic': np.random.randint(1, 6, 100),
        'Reviewer Type': np.random.choice(['Local', 'Tourist', 'etc'], 100),
        'Review Text': ['Review ' + str(i) for i in range(100)]
    })

    # 토픽 필터
    rating_filter = st.multiselect('Select Topic(s)', options=range(1, 6), default=[5])
    filtered_data = data[data['Topic'].isin(rating_filter)]

    # 리뷰어 유형 필터
    reviewer_type_filter = st.multiselect('Select reviewer type(s)', options=['Local', 'Tourist', 'etc'], default=['Local'])
    filtered_data = filtered_data[filtered_data['Reviewer Type'].isin(reviewer_type_filter)]

    # 결과 표시
    st.write(f"Filtered Reviews: {len(filtered_data)} found")
    st.dataframe(filtered_data)


####### sidebar #########
# CSS를 이용해 커스텀 스타일 적용
st.markdown("""
<style>
    .reportview-container .main .block-container {
        max-width: 1000px;  /* 최대 너비 설정 */
    }
</style>
""", unsafe_allow_html=True)

with st.sidebar :
    # 사이드바에 타이틀 추가
    st.sidebar.title("ASAC-MAP")
    # 검색창 (* business_name 기준)
    input_name = st.text_input("Search...")

    btn_submit = st.button("Go to Review", key='submit_btn', disabled=(input_name is False))


        
####### main page #########
if not btn_submit:
    show_main()
else:
    ## submit 버튼 onclick 이벤트

    # 입력이 없을 경우 에러 메시지
    if not input_name:
        st.error("Please enter the store name.")
    else:
        # 결과 표시
        show_result(input_name)


