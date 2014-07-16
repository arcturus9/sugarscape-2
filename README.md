SugarScape Simulation Project
==========

이 프로젝트는 SugarScape라는 실험을 simulation하기 위한 project입니다.

설명은 (부의 기원)[http://www.aladin.co.kr/shop/wproduct.aspx?ISBN=8925512432] 에서 보실 수 있습니다.

실행하기 위해 couchbase db 설치가 필요합니다. 실행하는 machine과 couchbase db 실행 machine이 다를 경우 Config.py의 dbHost를 변경하시면 됩니다.

실행 전 DBInit.py를 실행하여 초기 data를 설정해야 합니다. map 크기는 Data.py에서 조정 가능하며, DBInit.py에서 Player 수를 조정할 수 있습니다.

실행 중 ctrl-c를 한 번 누를 경우, 현재의 모든 상태를 저장하고 종료합니다.
