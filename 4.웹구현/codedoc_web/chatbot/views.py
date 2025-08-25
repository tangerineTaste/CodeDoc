from django.shortcuts import render
from django.http import JsonResponse,StreamingHttpResponse
from django.views.decorators.csrf import csrf_exempt
import json
from .rag_pipeline import get_rag_response, stream_rag_response, analyze_profile_with_llm
from accounts.models import UserProfile
from django.contrib.auth.decorators import login_required

def chatbot_view(request):
    return render(request, 'chatbot/chatbot.html')

@csrf_exempt
@login_required
def chatbot_api(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            query = data.get('query')

            if not query:
                return JsonResponse({'error': '질문(query)이 없습니다.'}, status=400)

            # 1. 먼저 질문이 금융 관련인지 확인
            classification = get_rag_response(query)
            
            # 2. 금융 관련 질문이 아니면, 스트리밍이 아닌 일반 응답
            if classification != "OK":
                def error_stream():
                    yield classification
                return StreamingHttpResponse(error_stream(), content_type="text/plain") # type: ignore

            # 3. 금융 관련 질문이면 스트리밍 응답 및 사용자 분석

            # 사용자 성향 분석 및 콘솔 출력
            print("===== LLM을 사용한 사용자 성향 분석 결과 =====")
            risk_score = analyze_profile_with_llm(query)
            print('경향(1: 안정적, -1: 위험)',risk_score)

            # risk_score를 UserProfile에 업데이트
            try:
                user_profile = request.user.profile
                user_profile.금융위험태도 = risk_score
                user_profile.save()
            except UserProfile.DoesNotExist:
                # UserProfile이 없는 경우 처리 (예: 새로 생성)
                UserProfile.objects.create(user=request.user, 금융위험태도=risk_score)
            except Exception as e:
                print(f"Error updating profile: {e}")
            
            # 응답 출력
            return StreamingHttpResponse(stream_rag_response(query), content_type="text/plain")

        except json.JSONDecodeError:
            return JsonResponse({'error': '잘못된 JSON 형식입니다.'}, status=400)
    else:
        return JsonResponse({'error': 'POST 요청만 허용됩니다.'}, status=405)