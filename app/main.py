import uvicorn
import mpmath
from fastapi import FastAPI, status
from pydantic import BaseModel
from fastapi.responses import JSONResponse
from app.middlewares import ResponseTimeMiddleware

app = FastAPI()
app.add_middleware(ResponseTimeMiddleware)

class body_to_predict(BaseModel):
    instances: list

# Liste de chiffres avec une taille N,  1 < N < 100000000

factorial_cache = {}


def long_calculation(param: int) -> int:
    if param in factorial_cache:
        return factorial_cache[param]
    else:
        result = mpmath.factorial(param)
        factorial_cache[param] = result
        return result

@app.get('/long-calculation')
async def perform_long_calculation(param: int) -> str:
    if param < 0:
        return JSONResponse({'error': 'Le paramètre doit être un entier positif'}, status_code=400)

    factorial_result = str(long_calculation(param)).rstrip('0').rstrip('.')
    
    return factorial_result


@app.post('/predict')
async def predict(X: body_to_predict):
    instances = X.instances
    results = []

    for instance in instances:
        result = await perform_long_calculation(int(instance))
        results.append(result)
    return {'predictions': results} 

@app.get('/healthcheck', status_code=status.HTTP_200_OK)
def health_check_handler():
    """
    Simple route for the Vertex AI to healthcheck on.

    It basically sends a GET request to the route & hopes to get a "200"
    response code. Failing to return a 200 response code just enables
    the Vertex Ai Models to do not deploy the model. It acts as a last
    line of defense in case something goes south.

    In other hands, it's ensure that the endpoint is alive

    :return: Json response in form of '200 OK'
    """
    return '200 OK'

if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=5000)


