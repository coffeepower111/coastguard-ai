
import os,json
from flask import Flask,request,jsonify,send_from_directory
from openai import OpenAI
app=Flask(__name__,static_folder="static")
client=OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
MODEL=os.environ.get("OPENAI_MODEL","gpt-5.6-luna")
PROMPT="""너는 대한민국 해양경찰 현장근무자를 지원하는 해양치안 신고·순찰 지원 AI다.
신고내용을 분석해 아래 JSON만 출력한다.
{"type":"신고유형","risk":"낮음/보통/높음/매우높음","place":"추정 장소","visit":"현장 출동 필요성 및 이유","check":["현장 확인사항"],"questions":["신고자 추가 확인사항"],"action":["초동조치"],"patrol":"순찰 제안","report":"상관 보고용 짧은 요약"}
규칙: 입력에 없는 사실을 만들지 말 것. 장소가 불명확하면 추가확인 필요. 인명위험과 해양사고 가능성을 우선 고려. 불법행위는 단정하지 말고 의심/확인 필요로 표현. 현장 안전을 최우선. AI는 판단 보조이며 최종 출동·법집행 판단은 담당자가 한다. 유효한 JSON만 출력."""
@app.get("/")
def home(): return send_from_directory("static","index.html")
@app.get("/health")
def health(): return jsonify(status="ok")
@app.post("/api/analyze")
def analyze():
    d=request.get_json(silent=True) or {}; text=d.get("report","").strip()
    if not text:return jsonify(error="신고내용을 입력해 주세요."),400
    try:
        r=client.responses.create(model=MODEL,instructions=PROMPT,input=text)
        return jsonify(json.loads(r.output_text))
    except json.JSONDecodeError:return jsonify(error="AI 응답 형식 오류입니다."),502
    except Exception as e:return jsonify(error=str(e)),500
if __name__=="__main__": app.run(host="0.0.0.0",port=int(os.environ.get("PORT","10000")))
