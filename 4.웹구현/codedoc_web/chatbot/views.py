from django.shortcuts import render
from django.http import JsonResponse,StreamingHttpResponse 
from django.views.decorators.csrf import csrf_exempt
import json
from .rag_pipeline import get_rag_response, stream_rag_response, get_risk_profile_by_similarity

def chatbot_view(request):
    return render(request, 'chatbot/chatbot.html')

@csrf_exempt
def chatbot_api(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            query = data.get('query')

            if not query:
                return JsonResponse({'error': '질문(query)이 없습니다.'}, status=400)

            # 사용자 성향 분석 및 콘솔 출력
            risk_profile = get_risk_profile_by_similarity(query)
            print("===== 사용자 성향 분석 결과 =====")
            print(risk_profile)
            print("==============================")

            # 1. 먼저 질문이 금융 관련인지 확인
            classification = get_rag_response(query)
            
            # 2. 금융 관련 질문이 아니면, 스트리밍이 아닌 일반 응답
            if classification != "OK":
                def error_stream():
                    yield classification
                return StreamingHttpResponse(error_stream(), content_type="text/plain") # type: ignore

            # 3. 금융 관련 질문이면 스트리밍 응답
            return StreamingHttpResponse(stream_rag_response(query), content_type="text/plain")

        except json.JSONDecodeError:
            return JsonResponse({'error': '잘못된 JSON 형식입니다.'}, status=400)
    else:
        return JsonResponse({'error': 'POST 요청만 허용됩니다.'}, status=405)