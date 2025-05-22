# ui
import streamlit as st
# 구글 권한 사용을 위한 패키지
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
import datetime
# 환경변수
from env_config import GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET
from services.make_creds_api import make_creds
# 구글 드라이브에 json 업로드
import json 
import requests



# 저장용 폴더 만들고 폴거의 id값 반환 / 이미 있다면 그 폴더의 id 반환
def create_folder():
    service = build("drive", "v3", credentials=make_creds("drive"))
    folder_name = 'dog_ai_service'

    # 📂 루트 폴더 안에서만 검색
    query = (
        f"name = '{folder_name}' and "
        f"mimeType = 'application/vnd.google-apps.folder' and "
        f"'root' in parents and trashed = false"
    )
    response = service.files().list(q=query, fields="files(id, name)").execute()
    files = response.get('files', [])

    if files:
        # st.info(f"📁 기존 폴더 '{folder_name}' 사용")
        return files[0]['id']
    else:
        file_metadata = {
            'name': folder_name,
            'mimeType': 'application/vnd.google-apps.folder',
            'parents': ['root']  # 명시적으로 루트에 생성
        }
        folder = service.files().create(body=file_metadata, fields='id').execute()
        # st.success(f"✅ 폴더 '{folder_name}' 생성 완료")
        return folder.get('id')

# 시트 생성하고 시트의 id값 반환 / 실패시 None 반환
def sheet_create():
    creds = make_creds("drive")
    if not creds:
        st.error("❌ 먼저 로그인하세요")
        return
    folder_name='dog_ai_service'
    title="강아지 정보"

    sheet_service = build("sheets", "v4", credentials=creds)
    drive_service = build("drive", "v3", credentials=creds)

    folder_id = create_folder() # 폴더 생성

    # 폴더 안에 파일이 이미 있는지 확인
    query = (
        f"name = '{title}' and "
        f"mimeType = 'application/vnd.google-apps.spreadsheet' and "
        f"'{folder_id}' in parents and trashed = false"
    )
    response = drive_service.files().list(q=query, fields="files(id, name)").execute()
    files = response.get('files', [])
#
    if files:
        # st.info(f"기존 파일 '{title}' 사용")
        spreadsheet_id=files[0]['id']
        return spreadsheet_id
    else:
        # 시트 만들기
        spreadsheet = {'properties': {'title': title}}
        try:
            sheet = sheet_service.spreadsheets().create(body=spreadsheet).execute()
            spreadsheet_id = sheet['spreadsheetId']
            st.success(f"{title}")
        except Exception as e:
            st.error(f"오류 : {e}")
            return
#

    # 시트를 이동
    file = drive_service.files().get(fileId=spreadsheet_id, fields='parents').execute()
    previous_parents = ",".join(file.get('parents', []))

    drive_service.files().update(
        fileId=spreadsheet_id,
        addParents=folder_id,
        removeParents=previous_parents,
        fields='id, parents'
    ).execute()

    # st.info(f"'{folder_name}' 폴더로 이동됨")


    return spreadsheet_id

# id값으로시트 정보 가져오기
def sheet_read(spreadsheet_id):
    creds = make_creds("drive")
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
            st.info("시트에 데이터 없음")
            return []
        
        values=json_key_change(values)  # 키 변경
        st.table(values)    # st표
        st.write(values)    # st표
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
    creds = make_creds("drive")
    if not creds:
        st.error("❌ 인증되지 않았습니다. 로그인 후 다시 시도하세요.")
        return

    sheet_service = build("sheets", "v4", credentials=creds)

    # 첫 번째 행: 헤더(컬럼)
    header = ["이름", "나이", "몸무게", "견종", "성별", "예방접종", "중성화", "특이사항"]

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
        st.success("✅ 강아지 정보가 성공적으로 입력되었습니다.")
    except Exception as e:
        st.error(f"오류 : {e}")

def sheet_delete():
    pass

# json 파일 생성하기
def upload_json_list_to_drive(json_list: list, filename: str = "강아지리스트.json"):
    creds = make_creds("drive")
    if not creds:
        # st.error("❌ 인증되지 않았습니다.")
        return None

    drive_service = build("drive", "v3", credentials=creds)
    access_token = creds.token
    headers = {
        "Authorization": f"Bearer {access_token}"
    }

    # ✅ 중복 파일 검사
    query = f"name = '{filename}' and mimeType = 'application/json' and trashed = false"
    response = drive_service.files().list(q=query, fields="files(id, name)").execute()
    files = response.get('files', [])

    if files:
        file_id = files[0]['id']
        # st.info(f"📄 기존 파일 '{filename}'이(가) 이미 존재합니다. 덮어씁니다.")

        # 기존 파일 덮어쓰기 (PATCH)
        upload_url = f"https://www.googleapis.com/upload/drive/v3/files/{file_id}?uploadType=media"
        upload_headers = headers.copy()
        upload_headers["Content-Type"] = "application/json"
        response = requests.patch(upload_url, headers=upload_headers, data=json.dumps(json_list, ensure_ascii=False))

        if response.status_code in (200, 201):
            # st.success(f"✅ 파일이 덮어써졌습니다. 파일 ID: {file_id}")
            pass
        else:
            # st.error(f"❌ 덮어쓰기 실패: {response.text}")
            return None

    else:
        # 새 파일 업로드 (POST)
        metadata = {
            "name": filename,
            "mimeType": "application/json"
        }
        files_payload = {
            "data": ("metadata", json.dumps(metadata), "application/json; charset=UTF-8"),
            "file": ("file", json.dumps(json_list, ensure_ascii=False), "application/json")
        }
        upload_url = "https://www.googleapis.com/upload/drive/v3/files?uploadType=multipart"
        response = requests.post(upload_url, headers=headers, files=files_payload)

        if response.status_code in (200, 201):
            file_id = response.json().get("id")
            # st.success(f"✅ 새 파일이 업로드되었습니다. 파일 ID: {file_id}")
        else:
            # st.error(f"❌ 업로드 실패: {response.text}")
            return None

    # ✅ 폴더로 이동
    try:
        folder_id = create_folder()
        file = drive_service.files().get(fileId=file_id, fields='parents').execute()
        previous_parents = ",".join(file.get('parents', []))

        drive_service.files().update(
            fileId=file_id,
            addParents=folder_id,
            removeParents=previous_parents,
            fields='id, parents'
        ).execute()

        # st.info(f"📂 '{filename}' 파일이 폴더로 이동되었습니다.")
    except Exception as e:
        # st.error(f"📁 폴더 이동 오류: {e}")
        pass

    return file_id
    
# 파일명으로 json 읽어오기 - 기본 반환값 리스트(강아지 정보 딕셔너리), 실패 시 [] 반환
def read_json_list_by_name(folder_name="dog_ai_service", filename="강아지리스트.json"):
    creds = make_creds("drive")
    if not creds:
        # st.error("❌ 인증되지 않았습니다.")
        return []

    service = build("drive", "v3", credentials=creds)

    # 1. 폴더명으로 폴더 ID 찾기
    folder_query = (
        f"name = '{folder_name}' and "
        "mimeType = 'application/vnd.google-apps.folder' and "
        "trashed = false"
    )
    folder_response = service.files().list(q=folder_query, fields="files(id, name)").execute()
    folders = folder_response.get('files', [])

    if not folders:
        # st.error(f"❌ '{folder_name}' 폴더를 찾을 수 없습니다.")
        return []

    folder_id = folders[0]['id']

    # 2. 해당 폴더 안에서 파일명 검색
    file_query = (
        f"name = '{filename}' and "
        f"'{folder_id}' in parents and "
        "trashed = false"
    )
    file_response = service.files().list(q=file_query, fields="files(id, name)").execute()
    files = file_response.get('files', [])

    if not files:
        # st.info(f"ℹ️ '{filename}' 파일이 '{folder_name}' 폴더 안에 없습니다.")
        return []

    file_id = files[0]['id']
    # st.info(f"🔍 '{filename}' 파일 발견, ID: {file_id}")

    # 3. 파일 내용 다운로드 및 JSON 파싱
    access_token = creds.token
    headers = {"Authorization": f"Bearer {access_token}"}
    download_url = f"https://www.googleapis.com/drive/v3/files/{file_id}?alt=media"
    response = requests.get(download_url, headers=headers)

    if response.status_code == 200:
        try:
            json_data = response.json()
            if isinstance(json_data, list):
                return json_data
            else:
                # st.warning("⚠️ JSON 내용이 리스트가 아닙니다.")
                return []
        except json.JSONDecodeError:
            # st.error("❌ JSON 디코딩 실패")
            return []
    else:
        # st.error(f"❌ 다운로드 실패: {response.status_code} - {response.text}")
        return []
    
def _convert_dates(obj):
    if isinstance(obj, dict):
        return {k: _convert_dates(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [_convert_dates(v) for v in obj]
    if isinstance(obj, (datetime.date, datetime.datetime)):
        return obj.isoformat()
    return obj

'''
dogs = [
    {
        "이름": "뽀삐",
        "나이": "3",
        "몸무게": "5.2",
        "견종": "말티즈",
        "성별": "암컷",
        "예방접종": "O",
        "중성화": "X",
        "특이사항": "알레르기 있음"
    },
    {
        "이름": "초코",
        "나이": "5",
        "몸무게": "8.1",
        "견종": "시바견",
        "성별": "수컷",
        "예방접종": "X",
        "중성화": "O",
        "특이사항": "사람을 좋아함"
    }
]
'''