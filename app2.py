import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# 페이지 설정
st.set_page_config(
    page_title="판매 데이터 시각화",
    page_icon="📊",
    layout="wide"
)

# 앱 제목
st.title("📊 월별 판매 데이터 시각화")
st.markdown("다양한 차트를 통해 판매 데이터를 시각화하는 앱입니다.")

# 1. 데이터프레임 생성 (요구사항 1)
@st.cache_data
def generate_sales_data():
    # 랜덤 시드 설정으로 일관된 데이터 생성
    np.random.seed(42)
    
    # 월별 데이터 생성
    months = [f"{i}월" for i in range(1, 13)]
    
    # 무작위 판매량 생성 (50~200 사이)
    product_a = np.random.randint(50, 201, size=12)
    product_b = np.random.randint(50, 201, size=12)
    product_c = np.random.randint(50, 201, size=12)
    
    # 데이터프레임 생성
    df = pd.DataFrame({
        '월': months,
        '상품A': product_a,
        '상품B': product_b,
        '상품C': product_c
    })
    
    # 무작위 위치 데이터 생성 (한국 지역 위주)
    locations = pd.DataFrame({
        '지역': ['서울', '부산', '인천', '대구', '광주', '대전', '울산', '세종', '경기', '강원', '충북', '충남'],
        'lat': [37.5665, 35.1796, 37.4563, 35.8714, 35.1595, 36.3504, 35.5384, 36.4800, 37.4138, 37.8228, 36.6357, 36.6588],
        'lon': [126.9780, 129.0756, 126.7052, 128.6014, 126.8526, 127.3845, 129.3114, 127.2890, 127.5183, 128.1555, 127.4914, 126.8000],
        '판매량': np.random.randint(100, 1001, size=12)
    })
    
    return df, locations

# 데이터 생성
sales_df, locations_df = generate_sales_data()

# 사이드바 - 필터링 및 옵션
st.sidebar.header("데이터 필터 및 옵션")

# 제품 선택 (도전 과제)
selected_products = st.sidebar.multiselect(
    "시각화할 제품 선택",
    ["상품A", "상품B", "상품C"],
    default=["상품A", "상품B", "상품C"]
)

# 월 범위 선택 (도전 과제)
months_range = st.sidebar.slider(
    "월 범위 선택",
    1, 12, (1, 12),
    step=1
)

# 선택된 월 범위에 따라 데이터 필터링
filtered_df = sales_df.iloc[(months_range[0]-1):months_range[1]]

# 선택된 제품만 포함하는 데이터프레임 생성
filtered_products_df = filtered_df[['월'] + selected_products]

# 데이터 탭과 시각화 탭 생성
tab1, tab2 = st.tabs(["📋 데이터", "📊 시각화"])

with tab1:
    st.header("판매 데이터")
    st.dataframe(filtered_products_df, use_container_width=True)
    
    # 데이터 요약 정보
    st.subheader("데이터 요약")
    
    # 총 판매량 계산
    total_sales = {}
    for product in selected_products:
        total_sales[product] = filtered_df[product].sum()
    
    # 총 판매량 표시
    col1, col2, col3 = st.columns(3)
    
    for i, (product, sales) in enumerate(total_sales.items()):
        if i == 0:
            col1.metric(f"{product} 총 판매량", f"{sales:,}개")
        elif i == 1:
            col2.metric(f"{product} 총 판매량", f"{sales:,}개")
        else:
            col3.metric(f"{product} 총 판매량", f"{sales:,}개")
    
    # 월별 총 판매량 계산
    filtered_df['월별 총 판매량'] = filtered_df[selected_products].sum(axis=1)
    
    # 상위 판매월 표시
    st.subheader("상위 판매월")
    top_months = filtered_df[['월', '월별 총 판매량']].sort_values('월별 총 판매량', ascending=False).head(3)
    st.dataframe(top_months, use_container_width=True)

with tab2:
    st.header("판매 데이터 시각화")
    
    # 2. 월별 판매량 막대 그래프 (요구사항 2)
    st.subheader("월별 판매량 막대 그래프")
    
    bar_fig = px.bar(
        filtered_products_df, 
        x='월', 
        y=selected_products,
        title='월별 제품 판매량',
        labels={'월': '월', 'value': '판매량', 'variable': '제품'},
        barmode='group'
    )
    
    st.plotly_chart(bar_fig, use_container_width=True)
    
    # 3. 총 판매량 파이 차트 (요구사항 3)
    st.subheader("제품별 총 판매량 파이 차트")
    
    # 총 판매량 계산
    total_by_product = {}
    for product in selected_products:
        total_by_product[product] = filtered_df[product].sum()
    
    # 파이 차트 생성
    pie_fig = px.pie(
        values=list(total_by_product.values()),
        names=list(total_by_product.keys()),
        title='제품별 총 판매량 비중',
        hole=0.3,
    )
    
    st.plotly_chart(pie_fig, use_container_width=True)
    
    # 4. 월별 판매 트렌드 선 그래프 (요구사항 4)
    st.subheader("월별 판매 트렌드")
    
    line_fig = px.line(
        filtered_products_df, 
        x='월', 
        y=selected_products,
        title='월별 판매 추이',
        labels={'월': '월', 'value': '판매량', 'variable': '제품'},
        markers=True,
        line_shape='linear'
    )
    
    st.plotly_chart(line_fig, use_container_width=True)
    
    # 5. 제품 간 상관관계 산점도 (요구사항 5)
    if len(selected_products) >= 2:
        st.subheader("제품 간 상관관계 산점도")
        
        # 산점도에 사용할 두 제품 선택
        scatter_col1, scatter_col2 = st.columns(2)
        
        with scatter_col1:
            x_product = st.selectbox("X축 제품", selected_products, index=0)
        
        with scatter_col2:
            # x_product와 다른 제품을 y축 기본값으로 설정
            default_y_index = 1 if selected_products[0] == x_product else 0
            y_product = st.selectbox("Y축 제품", selected_products, index=default_y_index)
        
        # 산점도 생성
        scatter_fig = px.scatter(
            filtered_df, 
            x=x_product, 
            y=y_product,
            trendline="ols",  # 추세선 추가
            title=f'{x_product}와 {y_product} 판매량 상관관계',
            labels={x_product: f'{x_product} 판매량', y_product: f'{y_product} 판매량'},
            hover_data=['월']  # 호버 시 월 정보 표시
        )
        
        # 상관계수 계산
        correlation = filtered_df[x_product].corr(filtered_df[y_product])
        scatter_fig.add_annotation(
            x=0.95, y=0.05,
            xref="paper", yref="paper",
            text=f"상관계수: {correlation:.2f}",
            showarrow=False,
            font=dict(size=12),
            bgcolor="rgba(255, 255, 255, 0.8)",
            bordercolor="black",
            borderwidth=1,
            borderpad=4
        )
        
        st.plotly_chart(scatter_fig, use_container_width=True)
    else:
        st.warning("산점도를 표시하려면 최소 2개 이상의 제품을 선택하세요.")
    
    # 6. 판매 위치 지도 시각화 (요구사항 6)
    st.subheader("지역별 판매 위치")
    
    map_fig = px.scatter_mapbox(
        locations_df, 
        lat="lat", 
        lon="lon", 
        hover_name="지역", 
        size="판매량",
        color="판매량",
        color_continuous_scale=px.colors.cyclical.IceFire,
        zoom=6,
        mapbox_style="carto-positron",
        title="지역별 판매량"
    )
    
    st.plotly_chart(map_fig, use_container_width=True)

# 추가 분석 - 제품 비교 히트맵
st.header("추가 분석: 월별 제품 판매 비교")

if len(selected_products) >= 2:
    # 히트맵 생성
    heatmap_data = filtered_df.pivot_table(
        index='월', 
        values=selected_products
    )
    
    heatmap_fig = px.imshow(
        heatmap_data,
        title="월별 제품 판매량 히트맵",
        labels=dict(x="제품", y="월", color="판매량"),
        color_continuous_scale="Viridis",
        aspect="auto"
    )
    
    st.plotly_chart(heatmap_fig, use_container_width=True)
else:
    st.warning("히트맵을 표시하려면 최소 2개 이상의 제품을 선택하세요.")

# 푸터
st.markdown("---")
st.caption("© 멋쟁이사자처럼") 