
import openai
import os


client = openai.OpenAI(api_key=os.environ['OPENAI_API_KEY'])


def health_info_summation(health_info):
    try:
        prompt = f"""
강아지의 건강상태는 아래와 같아.
{health_info}

건강정보를 자세하게 요약해서 알려줘.
이를 수의사에게 전달할거야.
특히, 수의사가 주의깊게 봐야하는 사항들을 꼼꼼히 적어줘.
        """

        health_info_summation = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "너는 강아지 건강정보를 요약해주는 보조야. 프롬프트를 자세하게 요약해줘."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.1
        )
        text = health_info_summation.choices[0].message.content
        return text
    except:
        return health_info