<!-- forge-slug: macbook-m5-vent-dust-cover -->
<!-- task: 1 -->
<!-- tdd: off -->
# MacBook Pro 14" M5 세로 거치용 환기구 먼지 덮개 (X1C 분리 출력)

## 목표 / 비목표
- 목표: 14인치 MacBook Pro M5를 클램쉘로 세로 거치했을 때 위를 향한 힌지 환기구(검은 힌지 띠 + 밑판 뒤쪽 슬릿 열) 위에서 먼지가 곧장 떨어지지 않도록, 지붕이 환기구 위로 떠 있는 캡형 덮개를 만든다. 공기는 좌우·앞뒤로 자유롭게 빠져야 한다. Bambu Lab X1C(256×256mm)에서 출력할 수 있게 2조각으로 나누고, 가운데는 겹침(단차) 이음으로 틈이 없게 한다.
- 비목표: 최종본의 PETG/ASA 출력(이번엔 PLA만 있음, 변형 시 교체), 좌우 가림판, 메시 필터, 세로 거치대 모델링, SolidCraft 파일 수정, 케이블 정리 기능.

## 확정된 결정 (그릴링 결과)
- 기기: MacBook Pro 14" M5. 공식 규격(Apple 한국 사양 페이지 직접 조회): 가로 312.6mm × 세로 221.2mm × 두께 15.5mm. [높음]
- 고정: 힌지 띠 윗면에 얹는 캡형. 접촉면에는 사용자가 펠트/TPU 패드를 붙인다. 슬릿 구간 아래로는 다리를 내리지 않는다.
- 공기 흐름: 지붕만, 사방 개방. 지붕 안쪽면과 환기구 사이 약 10~15mm.
- 분리: 2조각, 가운데 15~20mm 겹침 이음(접착 없이 맞물림).
- 소재: 우선 PLA, 변형되면 PETG. 시험 출력 후 지붕 안쪽 온도를 부하 상태에서 확인한다.
- 실측: 사용자가 재지 않는다. 공식 규격과 사진으로 추정하고, 시험 출력으로 맞춘다.
- 모델링: FreeCAD 1.1.3 `freecadcmd` 파라메트릭 스크립트 → STL 2개. TDD 끔.

## 추정 치수 (파라미터로 분리, 시험 출력 후 수정 대상)
- 힌지 띠 길이 약 240~270mm → 덮개 전체 길이 약 270~280mm로 시작. [낮음: 사진 비율 기반]
- 슬릿 구간 높이(힌지 윗면에서 아래로) 약 10~12mm. [낮음: 사진 기반]
- 오른쪽 끝 케이블, 뒤쪽 은색 물체와의 간격은 알 수 없음. 덮개가 뒤로 내미는 깊이는 최소로 유지한다.

## 진실의 원천
- 용어: 없음 (`.forge/CONTEXT.md` 미사용)
- 관련 ADR: 없음
- 완료 정의(DoD): 아래 명령이 모두 작성된 그대로 실행되어 기대값을 만족한다. 작성 시점(사전 상태)에는 `dust_cover.py`, `check_cover.py`, STL 파일이 모두 없어 아래 항목은 전부 실패한다. 순방향 검사이므로 이 상태가 맞다.
  1. `/Applications/FreeCAD.app/Contents/Resources/bin/freecadcmd /Users/gyuha/workspace/macbook-dust-cover/dust_cover.py` 종료 코드 0, `cover-left.stl`과 `cover-right.stl`이 생성된다. (사전: 파일 없음)
  2. `/Applications/FreeCAD.app/Contents/Resources/bin/freecadcmd /Users/gyuha/workspace/macbook-dust-cover/check_cover.py` 가 `PASS` 4줄을 출력하고 `FAIL`이 0줄이다. 검사 항목은 (a) 각 조각 바운딩 박스가 250×250×250mm 이하, (b) 두 조각을 이음 위치로 합쳤을 때 겹침 길이 15~20mm이고 서로 파고드는 부피가 0, (c) 지붕 안쪽면과 환기구 사이 간격 10~15mm이고 좌우·앞뒤 개방, 슬릿 구간 아래에 다리 없음, (d) 두 STL이 모두 닫힌 솔리드. (사전: 스크립트 없음)
  - 참고: 사전 상태에서 `freecadcmd -c "import Part; print(Part.makeBox(1,2,3).isValid())"` 가 정상 실행됨을 확인했다. 이 명령은 정적 도구 확인용이며 DoD 자체는 위 1, 2번이다.
  - 사용자 확인(UAT, 검증 전용 재개 단계): 두 조각을 PLA로 출력해 맥북에 얹었을 때 환기구가 가려지고 공기 흐름이 막히지 않는지 눈으로 확인한다. 이 항목은 자동 검증이 불가능하다. 맞지 않으면 파라미터를 고쳐 같은 스크립트로 다시 만든다.

## 작업 슬라이스
- [ ] S1. `dust_cover.py` 작성: 치수 변수를 맨 위에 모으고 FreeCAD로 좌·우 조각을 만들어 `cover-left.stl`, `cover-right.stl`로 내보낸다 — 완료 기준: DoD 1번 명령이 종료 코드 0이고 두 STL이 존재한다.
- [ ] S2. `check_cover.py` 작성: 두 STL을 읽어 바운딩 박스, 겹침 길이와 간섭, 지붕 간격과 개방, 닫힌 솔리드 여부를 숫자로 검사해 `PASS`/`FAIL` 줄을 출력한다 — 완료 기준: DoD 2번 명령이 `PASS` 4줄, `FAIL` 0줄이다. (depends: S1)
- [ ] S3. 출력 안내 작성(`README.md`): Bambu Studio에서 두 조각을 여는 방향과 PLA 기준 출력 설정, 패드 부착 위치, 맞지 않을 때 고칠 파라미터 이름을 적는다 — 완료 기준: README에 위 네 항목이 모두 있고, 언급한 파라미터 이름이 `dust_cover.py`에 실제로 존재한다. (depends: S1)
