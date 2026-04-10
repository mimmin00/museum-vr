# 루브르 박물관 인터랙티브 3D 웹사이트

## 프로젝트 개요
도난당한 루브르 박물관 유물에서 영감받은 인터랙티브 3D 웹 전시관.
Meshy AI로 제작한 GLB 모델을 웹캠 손 인식으로 조작 가능.

## 파일 구조
- `index.html` — 메인 파일 (HTML/CSS/JS 전체 포함)
- `Galerie_d'Apollon_(Louvre).jpg` — 배경 이미지
- `Meshy_AI_왕관_0404073506_texture.glb` — 외제니 왕후의 왕관
- `Meshy_AI_Emerald_Teardrop_Halo_0404084536_texture.glb` — 외제니 황후의 에메랄드 목걸이
- `Meshy_AI_Azure_Sapphire_Halo_N_0404093900_texture.glb` — 목걸이와 귀걸이
- `Meshy_AI_외제니_왕후의_귀_0404072330_texture.glb` — 외제니 왕후의 귀걸이

## 서버 실행
```bash
cd "/Users/min/Desktop/루브르 박물관"
python3 -m http.server 8000
```
→ http://localhost:8000

## 유물 순서 (index.html artifacts 배열)
1. 외제니 왕후의 왕관
2. 외제니 황후의 에메랄드 목걸이 (rotationX: Math.PI/2 — 보석이 보이도록)
3. 목걸이와 귀걸이 (No.M89)
4. 외제니 왕후의 귀걸이

## 주요 기술
- **Three.js** — 3D 렌더링, GLTFLoader, OrbitControls
- **MediaPipe Hands** — 웹캠 손 인식 (minDetectionConfidence: 0.7)
- **YouTube IFrame API** — 배경 음악 (처음부터 재생)

## 손 제스처
- 왼손 검지 → 좌우 회전
- 오른손 주먹 앞뒤 → 확대/축소

## 미니게임
- 실제 GLB 모델 geometry를 6구역으로 분할
- 5개 조각을 분리 후 원래 슬롯에 맞추는 퍼즐

## 주의사항
- 3D 모델 톤맵 제거 (ACESFilmicToneMapping 사용 시 모델이 어두워짐)
- ambient light: 2.5, hemisphere light: 0.5 유지
- 줌 범위: 0.5 ~ 20
