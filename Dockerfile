
FROM python:3.14


WORKDIR /importhub


COPY ./requirements.txt /importhub/requirements.txt


RUN pip install --no-cache-dir --upgrade -r /importhub/requirements.txt


COPY ./src /importhub/src/


CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]