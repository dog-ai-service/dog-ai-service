# pdf 관련
import aspose.pdf as ap
import io
import re
# 강아지 증상 정보 요약 
from services.AI.health_info_summation import health_info_summation


def make_pdf_data(values):
    # 요약된 강아지 건강 정보 --> LLM을 통해 요약된 텍스트 받ㅇ옴
    summation_health_info = health_info_summation(values)

    # PDF 문서 생성
    document = ap.Document()
    page = document.pages.add()

    # 줄 단위로 텍스트 처리 --> 아래는 **text** 이렇게 볼드체로 되어있는 부분을 PDF에서 볼드체로 나타내기 위한 코드 
    lines = summation_health_info.split('\n')

    for line in lines:
        line = line.strip()
        if not line:
            continue

        # 텍스트 프래그먼트 초기화
        text_fragment = ap.text.TextFragment()
        # 기본적인 설정 --> 폰트, 폰트 크기, 줄 간격 등등 
        text_fragment.text_state.font = ap.text.FontRepository.find_font("Malgun Gothic")
        text_fragment.text_state.font_size = 12
        text_fragment.text_state.foreground_color = ap.Color.from_rgb(0, 0, 0)
        text_fragment.text_state.line_spacing = 10

        # **bold** 구문 분리
        segments = re.split(r'(\*\*.*?\*\*)', line)

        for seg in segments:
            if seg.startswith("**") and seg.endswith("**"):
                clean_text = seg[2:-2]  # ** 제거
                segment = ap.text.TextSegment(clean_text)
                segment.text_state.font = ap.text.FontRepository.find_font("Malgun Gothic")
                segment.text_state.font_size = 12
                segment.text_state.font_style = ap.text.FontStyles.BOLD
            else:
                segment = ap.text.TextSegment(seg)
                segment.text_state.font = ap.text.FontRepository.find_font("Malgun Gothic")
                segment.text_state.font_size = 12

            # append를 통해 text_fragment에 담음
            text_fragment.segments.append(segment)

        # 페이지에 문장 추가
        page.paragraphs.add(text_fragment)

    # PDF 저장 및 반환 --> 메모리에 pdf 바이트 데이터를 저장 --> 그 다음 해당 값을 받아오고 반환
    pdf_stream = io.BytesIO()
    document.save(pdf_stream)
    pdf_stream.seek(0)
    pdf_bytes = pdf_stream.getvalue()
    return pdf_bytes