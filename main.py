import random
import subprocess

from fastapi.responses import HTMLResponse
from fastapi import FastAPI

app = FastAPI()


@app.get("/", response_class=HTMLResponse)
def get_root():
    return """
    <html>
        <head><title>Min FastAPI</title></head>
        <body>
            <h1>Välkommen till mitt projekt!</h1>
            <p>Kolla in min <a href="/random-gif">slumpmässiga gif</a> eller se 
            <a href="/docs">API-dokumentationen</a>.</p>
        </body>
    </html>
    """

@app.get("/")
def get_root():
    """
    Our root endpoint.

    It greets the user.
    """
    return {"Hello": "World"}

@app.get("/items/{item_id}")
def reed_item(item_id, q: str | None = None):
    """
    Get an itemby its id.


    You can use a query parameter `q` as well, if you want to.
    """
    return {"item_id": item_id, "q": q.upper()}

@app.get("/who")
def who():
    """Returns the hostname of the container handling the request.

    """
    r = subprocess.run("hostname", stdout=subprocess.PIPE)
    return {"hostname": r.stdout.decode()}

@app.get("/random-gif")
def gif():
    """Return the URL to a random gif.
    """
    return {"url": random.choice(["https://media1.tenor.com/m/J6czupAP77IAAAAd/el-banano.gif",
                                  "https://media1.tenor.com/m/zfPYirJGdOgAAAAC/doginme-dog-in-me.gif",
                                  "https://media1.tenor.com/m/4uCTNSAPCXUAAAAC/apple-cat.gif",
                                  "https://media0.giphy.com/media/v1.Y2lkPTc5MGI3NjExYTFyaTlpNzcyZzN4YzRpdTc1bG9zc2hkeHBtOHRyc29kNGRxMm1nNyZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/bh1u06PFhB9FCtTFaS/giphy.gif"])}

