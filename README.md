# Artisan

## About Artisan
Artisan is a tool that simplifies the creation of serverless applications on AWS by generating Python code for classes and more. It streamlines your development process, saving you time and ensuring code consistency in your serverless projects.

1. Install all required packages
```bash
pip install -r requirements.txt
```

or

```bash
poetry install
````

2. Copy the .env.example to .env

3. Then it locally using the following command
```bash
uvicorn public.main:app --reload --port 8888
```