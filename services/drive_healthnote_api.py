# ui
import streamlit as st
# 구글 권한 사용을 위한 패키지
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
import datetime
# 환경변수
from env_config import GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET



def drive_creds():
    client_id=GOOGLE_CLIENT_ID
    client_secret=GOOGLE_CLIENT_SECRET

    # 세션 상태에 token이 없으면 로그인 버튼 표시
    # 사용할 계정의 Google Calendar API를 사용 상태로 바꾸어야 사용가능
    if "token" not in st.session_state:
        pass
    else:
        token = st.session_state.token
        # 드라이브(스프레드시트) 사용을 위한 구글계정 정보를 세션에서 가져오기
        creds = Credentials(
            token=token["token"]["access_token"],
            refresh_token=token.get("refresh_token"),
            token_uri="https://oauth2.googleapis.com/token",
            client_id=client_id,
            client_secret=client_secret,
            scopes=["https://www.googleapis.com/auth/drive"]
        )


        return creds

# 저장용 폴더 만들고 폴거의 id값 반환
def create_folder():
    service = build("drive", "v3", credentials=drive_creds())
    folder_name='dog_health_service'

    # 이미 존재하는 폴더가 있는지 확인
    query = f"name = '{folder_name}' and mimeType = 'application/vnd.google-apps.spreadsheet' and trashed = false"
    response = service.files().list(q=query, fields="files(id, name)").execute()
    files = response.get('files', [])

    if files:
        return files[0]['id']
    else:
        file_metadata = {
            'name': folder_name,
            'mimeType': 'application/vnd.google-apps.folder'
        }
        folder = service.files().create(body=file_metadata, fields='id').execute()
        return folder.get('id')

# 시트 생성하고 시트의 id값 반환
def sheet_create():
    creds = drive_creds()
    if not creds:
        st.error("❌ 먼저 로그인하세요")
        return
    title="건강노트 정보"

    sheet_service = build("sheets", "v4", credentials=creds)
    drive_service = build("drive", "v3", credentials=creds)

    # 이미 존재하는 폴더가 있는지 확인
    query = f"name = '{title}' and mimeType = 'application/vnd.google-apps.spreadsheet' and trashed = false"
    response = drive_service.files().list(q=query, fields="files(id, name)").execute()
    files = response.get('files', [])
#
    if files:
        spreadsheet_id=files[0]['id']
        return spreadsheet_id
    else:
        # 시트 만들기
        spreadsheet = {'properties': {'title': title}}
        try:
            sheet = sheet_service.spreadsheets().create(body=spreadsheet).execute()
            spreadsheet_id = sheet['spreadsheetId']
        except Exception as e:
            st.error(f"오류 : {e}")
            return
#

    # 시트를 이동
    try:
        folder_id = create_folder()

        file = drive_service.files().get(fileId=spreadsheet_id, fields='parents').execute()
        previous_parents = ",".join(file.get('parents', []))

        drive_service.files().update(
            fileId=spreadsheet_id,
            addParents=folder_id,
            removeParents=previous_parents,
            fields='id, parents'
        ).execute()

    except Exception as e:
        st.error(f"폴더 이동 오류: {e}")

    return spreadsheet_id

# id값으로시트 정보 가져오기
def sheet_read(spreadsheet_id):
    creds = drive_creds()
    if not creds:
        st.error("❌ 인증되지 않았습니다. 로그인 후 다시 시도하세요.")
        return

    sheet_service = build("sheets", "v4", credentials=creds)

    try:
        sheet_service = build("sheets", "v4", credentials=creds)
        response = sheet_service.spreadsheets().values().get(
            spreadsheetId=spreadsheet_id,
            range="시트1!A1:Z100"#H100이여도 컬럼엔 문제없지만 일단 넉넉하게 잡기
        ).execute()

        values = response.get("values", [])
        
        if not values:
            return []
        
        #테스트
        st.write("강아지의 건강정보")
        values=json_key_change(values)  # 키 변경
        st.table(values)    # st표
        return values

    except Exception as e:
        st.error(f"시트 읽기 실패 오류 : {e}")
        return []

# json의 디폴트 키가 숫자여서 컬럼으로 변경
def json_key_change(values):
    if not values or len(values)<2: # 값이 없으면 컷
        return []
    result=[]
    for value in values[1:]:
        new_dict={values[0][i]:value[i] if not (value[i]=="공백") else "공백"for i in range(len(values[0]))}
        result.append(new_dict)
    return result




# id값으로 시트에 정보 넣기
def sheet_write(spreadsheet_id, dogs):
    creds = drive_creds()
    if not creds:
        st.error("❌ 인증되지 않았습니다. 로그인 후 다시 시도하세요.")
        return

    sheet_service = build("sheets", "v4", credentials=creds)

    # 첫 번째 행: 헤더(컬럼)
    header = ["날짜", "주요 증상", "의심 질병", "필요한 조치", "추가 메모"]

    # 나머지 행: 실제 데이터
    values = [header]
    for dog in dogs:
        row = [dog.get(col, "공백") for col in header]
        values.append(row)

    body = {
        "values": values
    }

    try:
        response = sheet_service.spreadsheets().values().update(
            spreadsheetId=spreadsheet_id,
            range="시트1!A1",  # A1부터 시작, 한국인 계정이면 시트명 디폴트가 시트1이라 그런지 sheet1이 아닌 시트1로해야함
            valueInputOption="RAW",
            body=body
        ).execute()
    except Exception as e:
        st.error(f"오류 : {e}")

def sheet_delete():
    pass
