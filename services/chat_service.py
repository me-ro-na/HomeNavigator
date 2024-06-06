from flask import Blueprint, request, jsonify
from openai import OpenAI
import os

chat_service = Blueprint('chat_service', __name__)

# Initialize OpenAI client
client = OpenAI(api_key='sk-proj-RGxBgR0aZsBGjmZ6nuPdT3BlbkFJwL1OFukJDx6SaUPfWewH')

prompt = '''
너는 디딤돌 대출에 대해 알려주는 상담원이야.
상대방의 질문에 간결하게 대답해줘.
제시된 대출 규정을 이용해서만 상담해줘야해.

대출규정:
신청대상
민법상 성년
대한민국 국민
접수일 현재 세대주
한국신용정보원 신용정보관리규약 해당사항 없고
CB점수 350점 이상
본인 및 배우자 합산 순자산 가액 4.69억원 이하

대출요건
5억원(신혼 · 2자녀 이상 가구 6억원) 이하 공부상 주택
세대원 전원이 무주택*
부부합산 연소득 60백만원 이하(생애최초, 2자녀 이상 가구 70백만원, 신혼가구 85백만원)
LTV 최대 70%
DTI 최대 60%

상품구조
대출한도 최대 2억 5천만원
(생애최초 주택구입자 3억원, 신혼 · 2자녀 이상 가구는 4억원)
대출만기 10년, 15년, 20년, 30년(거치기간은 1년 또는 비거치)
원리금 균등, 원금 균등, 체증식 분할상환
'''

@chat_service.route('/chat', methods=['POST'])
def chat():
    data = request.json
    message = data.get('message')
    chat_history = data.get('chat_history', [])

    # Construct messages for OpenAI API
    messages = [
        {"role": chat['role'].lower(), "content": chat['message']}
        for chat in chat_history
    ]
    messages.insert(0, {"role": "system", "content": prompt})
    messages.append({"role": "user", "content": message})

    response = client.chat.completions.create(
        model="gpt-4o",  # or "gpt-4"
        messages=messages
    )
    
    # Extract the response message
    answer = response.choices[0].message.content
    return jsonify({'response': answer})
