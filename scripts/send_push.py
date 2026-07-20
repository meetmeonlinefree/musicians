import os
import json
import subprocess
import requests
from pathlib import Path


PROJECT_ID = os.environ.get("FIREBASE_PROJECT_ID")
ACCESS_TOKEN = os.environ.get("ACCESS_TOKEN")


def get_changed_files():
    """
    Получаем список изменённых файлов
    между текущим коммитом и предыдущим
    """

    try:
        result = subprocess.check_output(
            [
                "git",
                "diff",
                "--name-only",
                "HEAD~1",
                "HEAD"
            ],
            text=True
        )

        return result.strip().split("\n")

    except Exception:
        return []


def load_json(file_path):

    try:
        with open(
            file_path,
            "r",
            encoding="utf-8"
        ) as file:

            return json.load(file)

    except Exception:
        return None


def create_notification(files):

    title = None
    body = None


    for file in files:


        # Обновление приложения
        if file == "app_update.json":

            data = load_json(file)

            if data:

                version = data.get(
                    "version",
                    ""
                )

                title = "📱 Новая версия приложения"

                body = (
                    f"Вышла новая версия "
                    f"Tajik Musician {version}. "
                    "Пожалуйста, обновите приложение."
                )

                break


        # Новый исполнитель
        if file.startswith("artists/") and file.endswith(".json"):
        
            data = load_json(file)
        
            if data:
        
                name = data.get(
                    "name",
                    "Исполнитель"
                )
        
                videos = data.get(
                    "videos",
                    []
                )
        
        
                # Если у исполнителя есть видео
                if videos:
        
                    last_video = videos[-1]
        
                    video_title = last_video.get(
                        "title",
                        "Новое видео"
                    )
        
        
                    title = "🎵 Новое видео от исполнителя"
        
                    body = (
                        f"{name}: {video_title} "
                        "добавлено в приложение Tajik Music"
                    )
        
        
                else:
        
                    title = "🎤 Новый исполнитель"
        
                    body = (
                        f"{name} добавлен "
                        "в приложение Tajik Music"
                    )
        
        
                break



        # Новые клипы
        elif file.startswith("feed/") and file.endswith(".json"):

            data = load_json(file)


            if data and "items" in data:

                item = data["items"][0]

                song = item.get(
                    "title",
                    "Новый клип"
                )

                title = "🎵 Новый клип"
                body = song

                break



        # Shorts
        elif file.startswith("shorts/") and file.endswith(".json"):

            data = load_json(file)


            if data and "items" in data:

                item = data["items"][0]

                short = item.get(
                    "title",
                    "Новый Short"
                )

                title = "📱 Новый Short"
                body = short

                break



    return title, body



def send_push(title, body):

    url = (
        f"https://fcm.googleapis.com/v1/projects/"
        f"{PROJECT_ID}/messages:send"
    )


    headers = {

        "Authorization":
            f"Bearer {ACCESS_TOKEN}",

        "Content-Type":
            "application/json"

    }


    payload = {
    
        "message": {
    
            "topic": "new_music",
    
            "notification": {
    
                "title": title,
    
                "body": body
    
            },
    
            "data": {
    
                "type": "update",
    
                "url": "https://play.google.com/store/apps/details?id=com.neuronit.tajikmusician"
    
            },
    
            "android": {
    
                "priority": "HIGH"
    
            }
    
        }
    
    }


    response = requests.post(
        url,
        headers=headers,
        json=payload
    )


    print(response.text)



def main():

    print("Checking changes...")


    files = get_changed_files()


    print(
        "Changed files:",
        files
    )


    if not files:

        print(
            "No changes"
        )

        return



    title, body = create_notification(files)



    if not title:

        print(
            "No notification needed"
        )

        return



    print(
        title,
        body
    )


    send_push(
        title,
        body
    )



if __name__ == "__main__":

    main()
