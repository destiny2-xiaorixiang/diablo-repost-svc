from fastapi import FastAPI


app = FastAPI()


@app.get("/vex")
async def vex():
    return "test"
