FROM python:3.11

WORKDIR /user/src/app

COPY requirements.txt ./
#why do we copy the requirements.txt first? because it is a small file and it will be cached, so it will be faster to install the dependencies
#so this is the first layer of the image, and it is a small optimization
#unless there are any changes in the requirements.txt, this layer will be cached, and we don't need to do the pip install again!

RUN pip install --no-cache-dir -r requirements.txt

COPY . . 
#copy all the files in the current directory to the working directory
#if there are any changes in the files, this layer will be rebuilt, and we don't need to do the pip install again!

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"] 
#if no --reload and no override in the docker-compose.yml, the container will not restart when the files are changed even we have bind mount the volume

