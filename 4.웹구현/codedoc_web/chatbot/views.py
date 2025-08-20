from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from .rag_pipeline import get_rag_response

def chatbot_view(request):
    return render(request, 'chatbot/chatbot.html')

@csrf_exempt
def chatbot_api(request):
    if request.method == 'POST':
        try:
            # request.body에서 JSON 데이터를 읽어 파이썬 dict로 변환
            data = json.loads(request.body)
            query = data.get('query')

            # 필수 데이터(query)가 있는지 확인
            if not query:
                return JsonResponse({'error': '질문(query)이 없습니다.'}, status=400)

            # RAG 파이프라인 호출
            answer = get_rag_response(query)
            
            # 결과를 JSON 형태로 응답
            return JsonResponse({'answer': answer})

        except json.JSONDecodeError:
            return JsonResponse({'error': '잘못된 JSON 형식입니다.'}, status=400)
    else:
        return JsonResponse({'error': 'POST 요청만 허용됩니다.'}, status=405)
