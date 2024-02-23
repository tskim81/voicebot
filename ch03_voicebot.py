import streamlit as st
import openai
from audiorecorder import audiorecorder
import os
from datetime import datetime
import numpy as np
from gtts import gTTS
import base64




#####기능 구현 함수#######
def STT(audio):
    #파일저장
    filename = "input.mp3"
    wav_file = open(filename, "wb")
    wav_file.write(audio.tobytes())
    wav_file.close()
    ##음성 데이터를 input.mp3라는 이름의 파일로 저장합니다. 
    ##open 함수를 이용해 파일을 바이너리 쓰기 모드("wb")로 열고, audio.tobytes() 메소드를 통해 얻은 바이트 데이터를 파일에 씁니다. 
    ##이후 파일을 닫습니다(wav_file.close())


    #음원 파일 열기
    audio_file = open(filename,"rb")
    #whisper 모델을 활용해 텍스트 얻기 
    transcript=openai.Audio.transcribe("whisper-1",audio_file) 
    audio_file.close()
    ##저장된 음원 파일을 다시 열어서 음성 인식을 수행할 준비를 합니다. 이번에는 파일을 바이너리 읽기 모드("rb")로 엽니다
    ##OpenAI의 Audio.transcribe 메소드를 사용하여 음성 파일을 텍스트로 변환합니다. 
    ##여기서는 "whisper-1"이라는 모델을 사용하는데, 이는 OpenAI가 제공하는 Whisper 음성 인식 모델 중 하나입니다. 
    ##함수는 변환된 텍스트를 포함하는 transcript를 반환합니다.
    ##음성 파일 사용이 끝났으므로 파일을 닫습니다.


    #파일삭제
    os.remove(filename)
    return transcript["text"]
    ##변환 작업이 완료된 후에는 더 이상 필요하지 않은 음성 파일을 삭제합니다. 이는 os.remove 함수를 사용하여 수행됩니다.
    ##마지막으로, transcript 딕셔너리에서 "text" 키에 해당하는 값을 반환합니다. 이 값은 Whisper 모델을 통해 변환된 텍스트, 즉 음성 데이터의 텍스트 변환 결과입니다.

    ##요약하자면, 이 함수는 주어진 음성 데이터를 파일로 저장하고, Whisper 모델을 사용하여 이를 텍스트로 변환한 후, 사용된 파일을 삭제하고 변환된 텍스트를 반환합니다


def ask_gpt(prompt,model):
    response=openai.ChatCompletion.create(model=model, messages=prompt)
    system_message=response["choices"][0]["messages"]
    return system_message["content"]



def TTS(response):
    #gTTS를 활용하여 음성파일 생성
    filename="output.mp3"
    tts=gTTS(text=response, lang="ko")
    tts.save(filename)


    #음원 파일 자동 재생
    with open(filename, "rb") as f:
        data=f.read()
        b64=base64.b4encode(data).decode()
        md=f"""
           <audio autoplay="True">
           <source src="data:audio/mp3;base64,{b64}" type="audio/mp3>
           </audio>
           """
        st.markdown(md, unsafe_allow_html=True)

    #파일삭제
    os.remove(filename)    







### 메인함수 ###
def main():


    #기본설정
    st.set_page_config(
        page_title="음성 비서 프로그램",
        layout="wide")

    flag_start = False
    


    #제목
    st.header("음성 비서 프로그램")

    #구분선
    st.markdown("---")


    #session state 초기화
    if "chat" not in st.session_state:
        st.session_state["chat"]=[]

    if "messages" not in st.session_state:
        st.session_state["messages"]=[{"role": "system", "content": "You are a thoughtful assistant. Respond to all input in 25 words and answer in korea"}]

    if "check_audio" not in st.session_state:
        st.session_state["check_audio"]=[]




    #기본 설명
    with st.expander("음성 비서 프로그램에 관하여", expanded=True):
        st.write(
        """
        - 음성 비서 프로그램의 UI는 스트림릿을 활용했습니다.
        - STT(Speech-TO-Text)는 OpenAI의 whisper AI를 활용했습니다.
        - 답변은 OpenAI의 GPT모델을 활용 했습니다.
        - TTS(Text-To-Speech)는 구글의 Google Translate TTS를 활용했습니다.
        """    
        )

        st.markdown("")




    #사이드바 생성
    with st.sidebar:

        #Open AI API 키 입력받기
        openai.api_key = st.text_input(label="OPENAI API 키", placeholder="Enter Your API Key", value="",type="password")

        st.markdown("---")

        #GPT 모델을 선택하기 위한 라디오 버튼 생성
        model = st.radio(label="GPT 모델", options=["gpt-4", "gtp-3.5-turbo"])

        st.markdown("")


        #리셋버트 생성
        if st.button(label="초기화"):
            #리셋 코드
            st.session_state["chat"]=[]
            st.session_state["messages"]=[{"role": "system", "content": "You are a thoughtful assistant. Respond to all input in 25 words and answer in korea"}]




    #기능 구현 공간
    col1, col2 = st.columns(2)

    with col1:
        #왼쪽 영역 작성
        st.subheader("질문하기")
        #음성 녹음 아이콘 추가
        audio = audiorecorder("클릭하여 녹음하기", "녹음중...")
        if len(audio) > 0 and not np.array_equal(audio, st.session_state["check_audio"]): #녹음을 실행하면
            #음성재생
            st.audio(audio.tobytes())
            #음성 파일에서 텍스트 추출
            question = STT(audio)

            #채팅을 시각화하기 위해 질문 내용 저장
            now = datetime.now().strftime("%H:%M")
            st.session_state["chat"]=st.session_state["chat"] + [("user", now, question)]
            #질문 내용 저장
            st.session_state["messages"]=st.session_state["messages"] + [{"role":"user", "content": question}]
            #audio 버퍼를 확인하기 위해 오디오 정보 저장
            st.session_state["check_audio"]=audio
            flag_start = True


    with col2:
        #오른쪽 영역 작성
        st.subheader("질문/답변")
        if flag_start:
            #ChatGPT에게 답변얻기
            response=ask_gpt(st.session_state["messages"], model)

            #GPT 모델에 넣을 프롬프트를 위해 답변 내용 저장
            st.session_state["messages"]=st.session_state["messages"] + [{"role":"system", "content": response}]

            #채팅 시각화를 위한 답변 내용 저장
            now = datetime.now().strftime("%H:%M")
            st.session_state["chat"]=st.session_state["chat"]+[("bot",now,response)]
            

            #채팅 형식으로 시각화 하기
            for sender, time, message in st.session_state["chat"]:
                if sender == "user":
                    st.write(f'div style="display:flex;align-items:center;"><div style="background-color:#007AFF;color:white;border-radius:12px;padding:8px 12px;margin-right:8px;">{message}</div><div style="font-size:0.8rem;color:gray;">{time}</div></div>', unsage_allow_html=True)
                    st.write("")
                else:
                    st.write(f'<div style="display:flex;align-items:center;justify-content:flex-end;"><div style="background-color:lightgray;border-radius:12px;padding:8px 12px;margin-left:8px;">{message}</div><dirv style="font-size:0.8rem;color:gray;">{time}</div></div>', unsafe_allow_html=True)
                    st.write("")
            
            # gTTS를 활용하여 음성 파일 생성 및 재생
            TTS(response)
            
            
        


if __name__=="__main__":
    main()




      