# DOG-AI-SERVICE
반려견과 보호자를 위한 AI 비서

---

## 프로젝트 추가 설명
> 추후 내용 추가

---

## 디렉토리 구조

```
dog_ai_service/
├── app.py              : 메인기능
├── .env                : 환경변수 파일(Git예외처리 되어서 수동으로 추가해야하고 **파일명 절대 변경금지**)
├── env_config.py       : 환경변수 로드
├── requirements.txt    : 패키지 설치 파일
├── test.txt            : 테스트 파일
├── .gitignore          : git 예외설정
├── other_files/        : 기타 파일(pdf 등)
├── components/
│   ├── prompt_box.py   : 질문창
│   ├── sidebar.py      : 사이드 바 
│   └── st_calendar.py  : streamlit 캘린더출력
├── pages/
│   ├── __init__.py     : 모듈 정리
│   ├── calendar_page.py: 캘린더 페이지
│   ├── chatbot_page.py : 챗봇 페이지
│   └── login_page.py   : 로그인 페이지
├── agent/
│   └── init_agent.py   : 랭체인-에이전트 초기화
├── services/
│   ├── calendar_api.py : 캘린더 api
│   ├── google_to_st_calendar.py        : 구글캘린더 > st캘린더로 정보 출력
│   └── login_api.py    : 로그인 api
├──
├──
└──

```

---

## 서버 실행/점검 커멘드
> streamlit run app.py --server.port 8080  
> streamlit hello

---

## 주의사항
> .env에는 gpt의 api-key 유출 방지로 Git 예외처리를 하여 수동으로 다운로드해줘야함  
> 중요 key가 있다면 유출되지 않도록 주의!  

---

## 번외(추후 삭제예정)
>윈11 한글 마지막 2번 써지는거 해결법
>>https://m.blog.naver.com/sbs5709/223075779033

---

## 각 branch 용도
> ### main(*중요)
>> 메인 branch  
>> main에 대한 모든 업데이트는 **test에서 먼저 시도**하여 이상이 없을 시에 **팀원 모두의 동의**를 구하고한다.
>
> ### test
>> 각자의 개인 branch에서의 업데이트를 먼저 테스트 해보는 곳.
>
> ### backup
>> 만일의 사태를 대비한 백업용 branch  
>> main이나 test에서 이상이 없다면 주기적으로 백업해두자
>
> ### hanbin
>> 성한빈 개인 branch
> ### kyusang
>> 심규상 개인 branch
> ### obj
>> 오병재 개인 branch


---

## 초기 설정
> 패키지 설치
>> pip install -r requirements.txt  

## Git 초기설정.
>터미널/cmd/git bash에서 프로젝트를 저장할 위치로 이동 후 아래 코드 입력
>> git clone https://github.com/dog-ai-service/dog-ai-service.git  
>
> vscode에서 해당 프로젝트를 폴더 열기  
> vscode의 터미널에서 아래 코드 입력
>> git switch test  
>> git switch -c [원하는 개인 branch명]  
>
> 좌측 소스 제어(깃)에서 [게시 Branch] 버튼 클릭
> 
> 아래 코드를 입력하여 각 branch가 제대로 추가되었는지 확인  
>> git branch -r
>
> 특정 커밋의 수정사항 취소하고 새로 커밋
>> git revert <되돌리고 싶은 커밋 id>

---

## GIT 명령어 모음
> branch 새로 생성 후 해당 branch로 즉시 전환
>> git switch -c [branch명]
>
> 로컬(개인컴) branch 목록 조회(*로 강조된 곳이 현재 branch)
>> git branch
>
> 원격(깃허브) branch 목록 조회(*로 강조된 곳이 현재 branch)
>> git branch -r
>
> branch 전환 코드 2가지(최근에는 switch를 더 자주 사용한다고함. checkout은 참고용)
>> git switch [branch명]
>> git checkout [branch명]
>
> branch 병합하기(현재 branch를 대상으로 명령어의 branch를 덮어씌우는 느낌)
>> git merge [branch명]
>

---

## .gitignore 사용법 예시 (원하는 파일의 커밋제한)
>// 1. '파일명'으로 제외하는 방법 (* 해당 방법은 경로 상관없이 지정한 파일명으로 모두 제외할 수 있다)  
>ignoreFileName.js
>
>// 2. 특정 '파일'만 제외하는 방법 (* 현재 기준을 .ignore파일이 있는 경로라고 생각하면 된다)  
>src/ignoreFileName.js
>
>// 3. 특정 '디렉토리' 기준 이하 파일들 제외 방법  
>node_module/
>
>// 4. 특정 디렉토리 하위의 특정 '확장자' 제외하는 방법  
>src/*.txt
>
>// 5. 특정 디렉토리 하위의 그 하위의 특정 '확장자' 제외하는 방법  
>src/**/*.txt
>
>// 6. 특정 '확장자' 제외하기  
>.txt
>
>// 7. 4번 특정 '확장자'에서 일부 제외 할 파일  
>!manual.txt

---

## 수정해야 할곳
```
login_api.py에서 
redirect_uri="http://localhost:8080"


```
---

## 기능 추가 계획
```
MCP 를 이용한 자동화 시스템
create_schedule와 pages/calendar_page.py를 합쳐야함
챗봇페이지는 pages/chatbot.py하고 pages/chatbot_page.py제거
pages/user_page.py 없애고 pages/health_note.py 넣기
services\AI와 pages/chatbot.py pages/health_note.py가 연동되어있음
```
---