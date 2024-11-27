FROM python:latest

ENV PYTHONUNBUFFERED 1

EXPOSE 7860

RUN apt update

RUN apt install curl

RUN curl -fsSL https://deb.nodesource.com/setup_22.x | bash -

RUN apt install nodejs
RUN apt install ffmpeg -y

RUN useradd -m -u 1000 user
USER user
ENV HOME=/home/user \
	PATH=/home/user/.local/bin:$PATH

WORKDIR $HOME/app

COPY --chown=user package*.json .

RUN npm install
RUN npm i twitch-dlp
#RUN npx twitch-dlp video:mira_42729465646_1730654416

COPY requirements.txt ./
RUN pip install --upgrade pip && \
    pip install -r requirements.txt

COPY --chown=user . .

#COPY --chown=user entrypoint.sh /entrypoint.sh
#RUN chmod +x /entrypoint.sh

# Sử dụng script entrypoint.sh để quản lý nhiều tiến trình
#ENTRYPOINT ["/entrypoint.sh"]
#CMD [ "node", "index.js" ]
#CMD ["python","main.py"]
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "7860"]
#CMD ["python","app.py"]