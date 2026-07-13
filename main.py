import streamlit as st
import numpy as np
import matplotlib.pyplot as plt

# 1. 페이지 기본 설정 및 디자인
st.set_page_config(page_title="지구과학II 행성 역행 시뮬레이터", layout="wide")

st.title("🌌 지구과학II 탐구: 행성의 순행과 역행 시뮬레이터")
st.markdown("""
이 프로그램은 **지구과학II 교과과정**의 '행성의 운동' 단원에 나오는 내·외행성의 겉보기 운동을 시각화합니다.
지구와 행성의 공전 속도 차이로 인해 천구 상에서 행성의 이동 방향이 반대로 뒤집히는 **역행(Retrograde)** 현상을 실시간으로 관찰해 보세요!
""")

# 2. 사이드바 - 관측 타겟 및 변수 설정
st.sidebar.header("🛸 행성 관측 설정")
planet_type = st.sidebar.selectbox("관측할 행성 종류", ["외행성 (화성 모사)", "내행성 (금성 모사)"])

# 행성 물리량 설정 (지구 기준 상대적 값)
if planet_type == "외행성 (화성 모사)":
    r_earth = 1.0
    r_planet = 1.52   # 지구보다 먼 궤도 반지름 (AU)
    t_earth = 1.0     # 지구 공전 주기 (1년)
    t_planet = 1.88   # 외행성 공전 주기 (년)
else:
    r_earth = 1.0
    r_planet = 0.72   # 지구보다 안쪽 궤도 반지름 (AU)
    t_earth = 1.0
    t_planet = 0.62   # 내행성 공전 주기 (년)

# 시간 축 설정 (회합 주기를 관찰하기에 충분한 시간)
synodic_period = abs(1 / (1/t_earth - 1/t_planet))
st.sidebar.write(f"📊 **이론적 회합 주기:** 약 {synodic_period:.2f} 년")

time_slider = st.sidebar.slider("시간 흐름 (년 단위)", 0.0, float(synodic_period * 1.2), 0.0, 0.02)

# 3. 위치 계산 알고리즘 (삼각함수를 활용한 2차원 좌표 변환)
# 각속도 omega = 2 * pi / T
omega_earth = 2 * np.pi / t_earth
omega_planet = 2 * np.pi / t_planet

# 각 행성의 2차원 위치 벡터 (X, Y)
x_earth = r_earth * np.cos(omega_earth * time_slider)
y_earth = r_earth * np.sin(omega_earth * time_slider)

x_planet = r_planet * np.cos(omega_planet * time_slider)
y_planet = r_planet * np.sin(omega_planet * time_slider)

# 4. 시선 방향(천구 상의 위치) 계산
# 지구에서 행성을 바라보는 벡터의 사이각(라디안)을 구함
dx = x_planet - x_earth
dy = y_planet - y_earth
apparent_angle = np.arctan2(dy, dx) # 시선 방향 각도

# 5. 데이터 시각화 (Matplotlib)
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))

# ---- 왼쪽 그래프: 헬리오센트릭 (태양 중심 궤도 뷰) ----
# 태양 및 궤도 그리기
ax1.plot(0, 0, 'yo', markersize=15, label='Sun (태양)')
theta = np.linspace(0, 2*np.pi, 100)
ax1.plot(r_earth*np.cos(theta), r_earth*np.sin(theta), 'b--', alpha=0.5, label='Earth Orbit')
ax1.plot(r_planet*np.cos(theta), r_planet*np.sin(theta), 'r--', alpha=0.5, label='Planet Orbit')

# 현재 위치 점 찍기
ax1.plot(x_earth, y_earth, 'bo', markersize=10, label='Earth (지구)')
ax1.plot(x_planet, y_planet, 'ro', markersize=10, label='Planet (행성)')

# 지구에서 행성을 바라보는 시선 방향 화살표
ax1.quiver(x_earth, y_earth, dx, dy, angles='xy', scale_units='xy', scale=1, color='purple', alpha=0.6, label='Line of Sight (시선)')

ax1.set_xlim(-r_planet*1.3, r_planet*1.3)
ax1.set_ylim(-r_planet*1.3, r_planet*1.3)
ax1.set_aspect('equal')
ax1.set_title("☀️ 태양 중심 행성 공전 궤도면")
ax1.set_xlabel("X (AU)")
ax1.set_ylabel("Y (AU)")
ax1.legend()
ax1.grid(True)

# ---- 오른쪽 그래프: 지오센트릭 (지구에서 본 천구 겉보기 위치 변화) ----
# 과거 시간의 흔적을 추적하여 역행 루프(Loop)를 그리기 위한 데이터 축적
t_trace = np.linspace(0, time_slider, 100)
x_e_trace = r_earth * np.cos(omega_earth * t_trace)
y_e_trace = r_earth * np.sin(omega_earth * t_trace)
x_p_trace = r_planet * np.cos(omega_planet * t_trace)
y_p_trace = r_planet * np.sin(omega_planet * t_trace)

angles_trace = np.arctan2(y_p_trace - y_e_trace, x_p_trace - x_e_trace)
# 연속적인 각도 변화를 위해 unwrap 처리 (도 단위 변환)
angles_trace_deg = np.degrees(np.unwrap(angles_trace))

# 천구 상의 겉보기 위치 변화 플롯 (X축: 시간, Y축: 천구상 도 각도)
if len(t_trace) > 0:
    ax2.plot(t_trace, angles_trace_deg, color='purple', linewidth=2, label='Apparent Motion Path')
    ax2.plot(time_slider, angles_trace_deg[-1], 'ko', markersize=8) # 현재 시점 위치

ax2.set_title("🌌 지구에서 본 행성의 천구 상 위치 변동 (적경 방향 변화)")
ax2.set_xlabel("시간 (년, Time)")
ax2.set_ylabel("겉보기 경도 (도, Apparent Longitude)")
ax2.grid(True)

# 그래프 레이아웃 최적화 및 출력
st.pyplot(fig)

# 6. 지구과학II 개념 연계 텍스트 설명 및 탐구 과제 제시
st.markdown("---")
st.subheader("💡 탐구 가이드 및 교과 연계 분석 질문")

if planet_type == "외행성 (화성 모사)":
    st.info("""
    **[외행성의 탐구 포인트]**
    * 슬라이더를 천천히 움직이면서 오른쪽 그래프의 **기울기가 음(-)으로 꺾이는 구간**을 찾아보세요. 이 구간이 바로 **역행** 구간입니다.
    * 태양 - 지구 - 외행성이 일직선상에 놓이는 **'충(Opposition)'** 위치 부근에서 역행이 발생하는지 왼쪽 궤도도면과 매칭하여 확인해 보세요.
    """)
else:
    st.info("""
    **[내행성의 탐구 포인트]**
    * 내행성은 지구보다 공전 속도가 빠릅니다. 내행성이 지구를 추월해 나갈 때 역행이 일어납니다.
    * 내행성이 태양과 지구 사이에 오는 **'내합(Inferior Conjunction)'** 단계에서 역행이 뚜렷하게 관측되는지 분석해 보세요.
    """)
