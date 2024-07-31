import streamlit as st
import pandas as pd
import numpy as np


# CSS를 이용해 커스텀 스타일 적용
st.markdown("""
<style>
    .reportview-container .main .block-container {
        max-width: 1000px;  /* 최대 너비 설정 */
    }
</style>
""", unsafe_allow_html=True)

# 사이드바에 타이틀 추가
st.sidebar.title("Sidebar Controls")

# 사이드바에 선택 박스 추가
option = st.sidebar.selectbox(
    'Which number do you like best?',
     np.arange(1, 11))

# # 사이드바에 슬라이더 추가
slider_val = st.sidebar.slider("Select a range of values", 0.0, 100.0, (25.0, 75.0))

# # 사이드바에 체크박스 추가
checkbox_val = st.sidebar.checkbox("Check me for more options")

# 페이지 타이틀 설정
st.title("Store A")

# 컬럼 레이아웃 정의
col1, col2 = st.columns(2)

# 첫 번째 컬럼에 이미지 추가
with col1:
    image_url = "https://via.placeholder.com/200"  # 임의의 이미지 URL 사용
    st.image(image_url, caption='Store A Example Image', width=200)

# 두 번째 컬럼에 키워드 추가
with col2:
    st.subheader("Good")
    st.write("Tasty Pasta, Kind Waitress, Cozy Atmosphere")
    st.subheader("Bad")
    st.write("Awful Location, High Cost, No Parking")

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
