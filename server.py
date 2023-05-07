import json
import markdown2

from src.EdgeGPT import Chatbot
from src.ImageGen import ImageGen

from flask import Flask, request, json, render_template_string

app = Flask(__name__)
bot: Chatbot = None

markdown_html_convertor = markdown2.Markdown()

@app.route("/cookie", methods=["PUT"])
def set_cookie():
    content = request.get_json()
    with open("cookies.json", "w") as file:
        json.dump(content, file)
    return content

@app.route("/reset")
async def reset():
    global bot
    if bot is None:
        bot = await Chatbot.create(cookie_path="cookies.json")
    else:
        await bot.reset()
    return "done"


@app.route("/text")
async def generate_text():
    prompt = request.args.get("prompt", "Hello World")
    style = request.args.get("style", "balanced")
    format = request.args.get("format", "html")
    global bot
    if bot is None:
        await reset()
    result = await bot.ask(
        prompt=prompt,
        conversation_style=style,
        search_result=True
    )
    if format == "markdown":
        try:
            result = [
                message["adaptiveCards"][0]["body"][0].get("text")
                for message in result["item"]["messages"]
                if message["author"] == "bot" and "messageType" not in message and "text" in message["adaptiveCards"][0]["body"][0]
            ][0]
        except Exception as e:
            print(e) # print the exception for debugging
    if format == "html":
        try:
            result = render_template_string(markdown_html_convertor.convert(
            "<!-- markdown-extras: break-on-newline, fenced-code-blocks, footnotes, target-blank-links, tag-friendly, task_list -->" +
            [
                message["adaptiveCards"][0]["body"][0].get("text")
                for message in result["item"]["messages"]
                if message["author"] == "bot" and "messageType" not in message and "text" in message["adaptiveCards"][0]["body"][0]
            ][0]))
        except Exception as e:
            print(e) # print the exception for debugging
    return result

@app.route("/image")
async def generate_image():
    prompt = request.args.get("prompt", "Hello World")

    cookie = ""
    with open("cookies.json", encoding="utf-8") as file:
        cookie_json = json.load(file)
        for cookie in cookie_json:
            if cookie.get("name") == "_U":
                cookie = cookie.get("value")
                break

    # Create image generator
    image_generator = ImageGen(auth_cookie=cookie, quiet=True)
    return image_generator.get_images(prompt=prompt)